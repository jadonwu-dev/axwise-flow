from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json
import logging
from datetime import datetime

from backend.models import User, InterviewData

# Configure logging
logger = logging.getLogger(__name__)

class DataService:
    """
    Service class for handling data upload and management operations.
    Encapsulates business logic related to file uploads, data parsing and database operations.
    """
    
    def __init__(self, db: Session, user: User):
        """
        Initialize the DataService with database session and user.
        
        Args:
            db (Session): SQLAlchemy database session
            user (User): Current authenticated user
        """
        self.db = db
        self.user = user
    
    async def upload_interview_data(self, file: UploadFile, is_free_text: bool = False) -> dict:
        """
        Process uploaded interview data file (JSON or free-text).
        
        Args:
            file (UploadFile): Uploaded file object
            is_free_text (bool): Whether the file contains free-text format (not JSON)
            
        Returns:
            dict: Result with data_id, success status and message
        
        Raises:
            HTTPException: For invalid file formats or other errors
        """
        try:
            # Read file content
            content = await file.read()
            content_text = content.decode("utf-8")
            
            # Determine input type based on file extension and is_free_text flag
            file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            
            if is_free_text or file_extension in ['txt', 'text']:
                logger.info(f"Processing as free-text format: {file.filename}")
                input_type, json_content = self._process_free_text(content_text, file)
            else:
                # Attempt to parse as JSON
                try:
                    data = json.loads(content_text)
                except json.JSONDecodeError:
                    # If JSON parsing fails but user didn't specify free-text, raise an error
                    if file_extension not in ['txt', 'text']:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid JSON format. Please upload a valid JSON file or specify is_free_text=true for text files."
                        )
                    # Otherwise, treat as free text
                    logger.info(f"JSON parsing failed, treating as free-text format: {file.filename}")
                    input_type, json_content = self._process_free_text(content_text, file)
                else:
                    # Determine JSON input type
                    if isinstance(data, list):
                        input_type = "json_array"
                    elif isinstance(data, dict):
                        input_type = "json_object"
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail="Unsupported JSON structure. Expected array or object."
                        )
                    json_content = content_text
            
            # Save to database
            interview_data = self._create_interview_data_record(
                filename=file.filename,
                input_type=input_type,
                json_content=json_content
            )
            
            logger.info(f"Data uploaded successfully for user {self.user.user_id}. Data ID: {interview_data.data_id}")
            
            # Return response
            return {
                "success": True,
                "message": "Data uploaded successfully",
                "data_id": interview_data.data_id
            }
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error uploading data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Server error: {str(e)}"
            )
    
    def _process_free_text(self, content_text: str, file: UploadFile) -> tuple:
        """
        Process content as free-text and prepare for storage.
        
        Args:
            content_text (str): Text content of the file
            file (UploadFile): The uploaded file object
            
        Returns:
            tuple: (input_type, json_content)
        """
        # Create a consistent data structure for free text
        data = {
            "free_text": content_text,
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "is_free_text": True
            }
        }
        
        # Store as JSON string for consistency in storage
        json_content = json.dumps(data)
        input_type = "free_text"
        
        return input_type, json_content
    
    def _create_interview_data_record(self, filename: str, input_type: str, json_content: str) -> InterviewData:
        """
        Create and save InterviewData record in database.
        
        Args:
            filename (str): Name of the uploaded file
            input_type (str): Type of data (free_text, json_array, json_object)
            json_content (str): JSON string of the content
            
        Returns:
            InterviewData: The created record
        """
        interview_data = InterviewData(
            user_id=self.user.user_id,
            filename=filename,
            input_type=input_type,
            original_data=json_content
        )
        
        self.db.add(interview_data)
        self.db.commit()
        self.db.refresh(interview_data)
        
        return interview_data 