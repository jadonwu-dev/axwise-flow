from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Literal
from sqlalchemy import desc, asc

from backend.models import User, InterviewData, AnalysisResult, Persona

# Configure logging
logger = logging.getLogger(__name__)

# Default sentiment values when none are available
DEFAULT_SENTIMENT_OVERVIEW = {
    "positive": 0.33,
    "neutral": 0.34,
    "negative": 0.33
}

class ResultsService:
    """
    Service class for handling retrieval and formatting of analysis results.
    """
    
    def __init__(self, db: Session, user: User):
        """
        Initialize the ResultsService with database session and user.
        
        Args:
            db (Session): SQLAlchemy database session
            user (User): Current authenticated user
        """
        self.db = db
        self.user = user
    
    def get_analysis_result(self, result_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific analysis result.
        
        Args:
            result_id: ID of the analysis result to retrieve
            
        Returns:
            Analysis result data formatted for API response
            
        Raises:
            HTTPException: If result not found or not accessible by user
        """
        try:
            logger.info(f"Retrieving results for result_id: {result_id}, user: {self.user.user_id}")
            
            # Query for results with user authorization check
            analysis_result = self.db.query(AnalysisResult).join(
                InterviewData
            ).filter(
                AnalysisResult.result_id == result_id,
                InterviewData.user_id == self.user.user_id
            ).first()

            if not analysis_result:
                logger.error(f"Results not found - result_id: {result_id}, user_id: {self.user.user_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Results not found for result_id: {result_id}"
                )

            # Check if results are available
            if not analysis_result.results:
                return {
                    "status": "processing",
                    "message": "Analysis is still in progress."
                }

            # Check for error in results
            if isinstance(analysis_result.results, dict) and "error" in analysis_result.results:
                return {
                    "status": "error",
                    "result_id": analysis_result.result_id,
                    "error": analysis_result.results["error"]
                }

            # Parse stored results and format them
            try:
                # Parse stored results to Python dict
                results_dict = (
                    json.loads(analysis_result.results) 
                    if isinstance(analysis_result.results, str)
                    else analysis_result.results
                )
                
                # Enhanced logging for personas debug
                logger.info(f"Results keys available: {list(results_dict.keys())}")
                self._ensure_personas_present(results_dict, result_id)
                
                # Create formatted response
                formatted_results = {
                    "status": "completed",
                    "result_id": analysis_result.result_id,
                    "analysis_date": analysis_result.analysis_date,
                    "results": {
                        "themes": results_dict.get("themes", []),
                        "patterns": results_dict.get("patterns", []),
                        "sentiment": results_dict.get("sentiment", []),
                        "sentimentOverview": results_dict.get("sentimentOverview", DEFAULT_SENTIMENT_OVERVIEW),
                        "insights": results_dict.get("insights", []),
                        "personas": results_dict.get("personas", []),
                    },
                    "llm_provider": analysis_result.llm_provider,
                    "llm_model": analysis_result.llm_model
                }
                
                return formatted_results
                
            except (json.JSONDecodeError, AttributeError, KeyError) as e:
                logger.error(f"Error formatting results: {str(e)}")
                return {
                    "status": "error",
                    "result_id": analysis_result.result_id,
                    "error": f"Error formatting results: {str(e)}"
                }
                
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error retrieving results: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    def get_all_analyses(self,
                        sort_by: Optional[str] = None,
                        sort_direction: Optional[Literal["asc", "desc"]] = "desc",
                        status: Optional[Literal["pending", "completed", "failed"]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all analyses for the current user.
        
        Args:
            sort_by: Field to sort by (createdAt, fileName)
            sort_direction: Sort direction (asc, desc)
            status: Filter by status
            
        Returns:
            List of formatted analysis results
        """
        try:
            # Log retrieval request
            logger.info(f"list_analyses called - user_id: {self.user.user_id}")
            logger.info(f"Request parameters - sortBy: {sort_by}, sortDirection: {sort_direction}, status: {status}")
            
            # Build the query with user authorization check
            query = self.db.query(AnalysisResult).join(
                InterviewData
            ).filter(
                InterviewData.user_id == self.user.user_id
            )
            
            # Apply status filter if provided
            if status:
                query = query.filter(AnalysisResult.status == status)
            
            # Apply sorting
            if sort_by == "createdAt" or sort_by is None:
                # Default sorting by creation date
                if sort_direction == "asc":
                    query = query.order_by(AnalysisResult.analysis_date.asc())
                else:
                    query = query.order_by(AnalysisResult.analysis_date.desc())
            elif sort_by == "fileName":
                # Sorting by filename requires joining with InterviewData
                if sort_direction == "asc":
                    query = query.order_by(InterviewData.filename.asc())
                else:
                    query = query.order_by(InterviewData.filename.desc())
                    
            # Execute query
            analysis_results = query.all()
            
            # Format the results
            formatted_results = []
            for result in analysis_results:
                # Skip results with no data
                if not result or not result.interview_data:
                    continue
                    
                # Format data to match frontend schema
                formatted_result = self._format_analysis_list_item(result)
                formatted_results.append(formatted_result)
                
            logger.info(f"Returning {len(formatted_results)} analyses for user {self.user.user_id}")
            
            return formatted_results
                
        except Exception as e:
            logger.error(f"Error retrieving analyses: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error: {str(e)}"
            )
    
    def _ensure_personas_present(self, results_dict: Dict[str, Any], result_id: int) -> None:
        """
        Ensure personas are present in the results dictionary.
        Instead of querying the personas table, this extracts personas directly from the results JSON.
        
        Args:
            results_dict: Analysis results dictionary to modify
            result_id: ID of the analysis result
        """
        # Log the method call for debugging
        logger.info(f"_ensure_personas_present called with result_id: {result_id}")
        
        # Check if personas are already in the results dictionary
        if "personas" in results_dict and results_dict["personas"]:
            persona_count = len(results_dict.get("personas", []))
            logger.info(f"Found {persona_count} personas already in results dictionary")
            return  # Personas already exist in the results, no need to modify
        
        # No personas in the results dict, initialize empty array
        # Note: We're not adding mock personas anymore since we want real data only
        logger.info(f"No personas found in results dictionary for result_id: {result_id}")
        results_dict["personas"] = []
    
    def _format_analysis_list_item(self, result: AnalysisResult) -> Dict[str, Any]:
        """
        Format a single analysis result for the list view.
        
        Args:
            result: AnalysisResult database record
            
        Returns:
            Formatted result for API response
        """
        # Format data to match frontend schema
        formatted_result = {
            "id": str(result.result_id),
            "status": result.status,
            "createdAt": result.analysis_date.isoformat(),
            "fileName": result.interview_data.filename if result.interview_data else "Unknown",
            "fileSize": None,  # We don't store this currently
            "themes": [],
            "patterns": [],
            "sentimentOverview": DEFAULT_SENTIMENT_OVERVIEW,
            "sentiment": [],
            "personas": [],  # Initialize empty personas list
        }
        
        # Add results data if available
        if result.results:
            try:
                # Parse results data
                results_data = (
                    json.loads(result.results) 
                    if isinstance(result.results, str)
                    else result.results
                )
                
                if isinstance(results_data, dict):
                    if "themes" in results_data and isinstance(results_data["themes"], list):
                        formatted_result["themes"] = results_data["themes"]
                    if "patterns" in results_data and isinstance(results_data["patterns"], list):
                        formatted_result["patterns"] = results_data["patterns"]
                    if "sentimentOverview" in results_data and isinstance(results_data["sentimentOverview"], dict):
                        formatted_result["sentimentOverview"] = results_data["sentimentOverview"]
                    if "sentiment" in results_data:
                        formatted_result["sentiment"] = results_data["sentiment"] if isinstance(results_data["sentiment"], list) else []
                    # Add personas if available
                    if "personas" in results_data:
                        formatted_result["personas"] = results_data["personas"] if isinstance(results_data["personas"], list) else []
                    
                    # Add error info if available
                    if result.status == 'failed' and "error" in results_data:
                        formatted_result["error"] = results_data["error"]
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error parsing results data: {str(e)}")
                
        # Map API status to schema status values
        if result.status == 'processing':
            formatted_result["status"] = "pending"  # Match schema requirements
        elif result.status == 'error':
            formatted_result["status"] = "failed"  # Match schema requirements
            
        return formatted_result 