"""
Script to check personas in the database.
"""
import sys
import os
import logging
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database and models
from backend.database import SessionLocal
from backend.models import Persona, AnalysisResult

def check_personas():
    """Check if there are any personas in the database."""
    session = SessionLocal()
    try:
        # Check total number of personas
        persona_count = session.query(Persona).count()
        logger.info(f"Total personas in database: {persona_count}")
        
        # Check total number of analysis results
        result_count = session.query(AnalysisResult).count()
        logger.info(f"Total analysis results in database: {result_count}")
        
        # Get all analysis results
        results = session.query(AnalysisResult).all()
        for result in results:
            # Check personas for each result
            personas = session.query(Persona).filter(Persona.result_id == result.result_id).all()
            logger.info(f"Result ID: {result.result_id} has {len(personas)} personas")
            
            # If there are personas, print some details
            for persona in personas:
                logger.info(f"  - Persona ID: {persona.persona_id}, Name: {persona.name}")
    
    finally:
        session.close()

if __name__ == "__main__":
    check_personas() 