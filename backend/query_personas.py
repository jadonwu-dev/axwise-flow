import os
import sys
import logging
import json
import pprint
from sqlalchemy import text

# Set up more detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to resolve imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database connection
from backend.database import engine

def query_personas():
    """
    Query for personas in the results JSON field
    """
    try:
        with engine.connect() as connection:
            # Find a specific result with personas
            test_id = 101  # This ID showed personas in previous run
            logger.info(f"Examining result ID: {test_id} in detail")
            
            result = connection.execute(text(f"SELECT results FROM analysis_results WHERE result_id = {test_id}"))
            row = result.fetchone()
            
            if row and row[0]:
                results_data = row[0]
                
                # Parse JSON if it's a string
                if isinstance(results_data, str):
                    try:
                        results_data = json.loads(results_data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in result {test_id}")
                        return
                
                # Check top-level keys
                if isinstance(results_data, dict):
                    keys = list(results_data.keys())
                    logger.info(f"Top-level keys in result: {keys}")
                    
                    # Look for personas
                    if 'personas' in results_data:
                        personas = results_data['personas']
                        logger.info(f"Found {len(personas)} personas in result")
                        
                        # Print first persona with pretty formatting
                        if personas and len(personas) > 0:
                            logger.info("First persona structure:")
                            pp = pprint.PrettyPrinter(indent=2)
                            logger.info(pp.pformat(personas[0]))
                            
                            # Check persona structure
                            if isinstance(personas[0], dict):
                                logger.info(f"Persona fields: {list(personas[0].keys())}")
                    else:
                        logger.info("No 'personas' key in results")
                else:
                    logger.info("Results data is not a dictionary")
            
            # Now check for multiple results with personas
            logger.info("Looking for results with personas...")
            result = connection.execute(text("""
                SELECT result_id FROM analysis_results 
                WHERE results IS NOT NULL 
                ORDER BY result_id ASC
            """))
            
            result_ids = [row[0] for row in result.fetchall()]
            
            persona_counts = {}
            for result_id in result_ids[:20]:  # Check first 20 results
                result = connection.execute(text(f"SELECT results FROM analysis_results WHERE result_id = {result_id}"))
                row = result.fetchone()
                
                if row and row[0]:
                    results_data = row[0]
                    
                    # Parse JSON if needed
                    if isinstance(results_data, str):
                        try:
                            results_data = json.loads(results_data)
                        except json.JSONDecodeError:
                            continue
                    
                    # Check for personas
                    if isinstance(results_data, dict) and 'personas' in results_data:
                        personas = results_data['personas']
                        if personas and len(personas) > 0:
                            persona_counts[result_id] = len(personas)
            
            if persona_counts:
                logger.info(f"Results with personas: {persona_counts}")
            else:
                logger.info("No results found with personas in the first 20 results")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    query_personas() 