"""
Enhanced role identification for persona formation
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def identify_roles(speaker_texts: Dict[str, str],
                  participants: Optional[List[Dict[str, Any]]] = None) -> Dict[str, str]:
    """Identify the role of each speaker in the conversation

    Args:
        speaker_texts: Dictionary mapping speaker names to their combined text
        participants: Optional list of participant information with roles

    Returns:
        Dictionary mapping speaker names to their roles (Interviewee, Interviewer, Participant)
    """
    logger.info(f"Identifying roles for {len(speaker_texts)} speakers")

    # If participants with roles are provided, use them
    if participants:
        roles = {}
        for speaker in speaker_texts:
            # Find matching participant
            for participant in participants:
                if participant.get("name", "") == speaker:
                    roles[speaker] = participant.get("role", "Participant")
                    break
            else:
                # Default to Participant if no match found
                roles[speaker] = "Participant"
        return roles

    # Otherwise, use heuristics to identify roles
    roles = {}
    
    # Check for explicit interviewer/interviewee indicators in speaker names
    for speaker, text in speaker_texts.items():
        speaker_lower = speaker.lower()
        if "interviewer" in speaker_lower or "moderator" in speaker_lower or "researcher" in speaker_lower:
            roles[speaker] = "Interviewer"
            logger.info(f"Identified {speaker} as Interviewer based on name")
        elif "interviewee" in speaker_lower or "participant" in speaker_lower or "subject" in speaker_lower:
            roles[speaker] = "Interviewee"
            logger.info(f"Identified {speaker} as Interviewee based on name")
    
    # If we've identified all speakers, return the roles
    if len(roles) == len(speaker_texts):
        return roles
        
    # If we've identified some but not all speakers, use heuristics for the rest
    unassigned_speakers = [s for s in speaker_texts if s not in roles]
    if roles and unassigned_speakers:
        # If we have identified interviewers but no interviewees, the unassigned are likely interviewees
        if "Interviewer" in roles.values() and "Interviewee" not in roles.values():
            for speaker in unassigned_speakers:
                roles[speaker] = "Interviewee"
                logger.info(f"Assigned {speaker} as Interviewee (complementary to identified Interviewers)")
        # If we have identified interviewees but no interviewers, the unassigned are likely interviewers
        elif "Interviewee" in roles.values() and "Interviewer" not in roles.values():
            for speaker in unassigned_speakers:
                roles[speaker] = "Interviewer"
                logger.info(f"Assigned {speaker} as Interviewer (complementary to identified Interviewees)")
        return roles

    # Heuristic: The speaker with the most text is likely the interviewee
    text_lengths = {speaker: len(text) for speaker, text in speaker_texts.items()}
    if text_lengths:
        primary_speaker = max(text_lengths, key=text_lengths.get)
        roles[primary_speaker] = "Interviewee"
        logger.info(f"Identified {primary_speaker} as Interviewee based on text length")

        # All others are likely interviewers
        for speaker in speaker_texts:
            if speaker != primary_speaker:
                roles[speaker] = "Interviewer"
                logger.info(f"Identified {speaker} as Interviewer (complementary to primary speaker)")

    # If no speakers found, return empty dict
    if not roles:
        logger.warning("No speakers identified for role assignment")

    return roles
