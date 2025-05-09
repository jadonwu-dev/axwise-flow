"""
Transcript processing module for handling interview transcripts.

This module provides functionality for:
1. Parsing raw transcripts into structured format
2. Identifying roles in transcripts (interviewer vs interviewee)
3. Extracting names from text
4. Splitting text by roles
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """
    Processes interview transcripts into structured format and extracts relevant information.
    """

    def __init__(self):
        """Initialize the transcript processor."""
        logger.info("Initialized TranscriptProcessor")

    def parse_raw_transcript_to_structured(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse raw transcript text into structured format with speaker and text fields.

        Args:
            text: Raw interview transcript text

        Returns:
            List of dictionaries with speaker and text fields
        """
        logger.info("Parsing raw transcript to structured format")
        structured_transcript = []

        # Try different patterns to identify speakers and their text
        # Pattern 1: "Speaker: Text" format
        pattern1 = re.compile(r"([^:]+):\s*(.+?)(?=\n[^:]+:|$)", re.DOTALL)
        matches1 = pattern1.findall(text)

        # If we found matches with pattern 1, process them
        if matches1:
            logger.info(f"Found {len(matches1)} matches with 'Speaker: Text' pattern")
            valid_matches = []
            for speaker, content in matches1:
                # Skip if speaker is just numbers or very short
                if speaker.strip().isdigit() or len(speaker.strip()) < 2:
                    continue
                # Skip if content is just numbers or very short
                if content.strip().isdigit() or len(content.strip()) < 3:
                    continue
                valid_matches.append((speaker, content))

            logger.info(f"Filtered to {len(valid_matches)} valid matches")

            # Only proceed if we have enough valid matches
            if len(valid_matches) > 2:
                for speaker, content in valid_matches:
                    structured_transcript.append({
                        "speaker": speaker.strip(),
                        "text": content.strip()
                    })
                return structured_transcript

        # Pattern 2: Q&A format
        pattern2 = re.compile(r"(Q|A):\s*(.+?)(?=\n[QA]:|$)", re.DOTALL)
        matches2 = pattern2.findall(text)

        # If we found matches with pattern 2, process them
        if matches2:
            logger.info(f"Found {len(matches2)} matches with Q&A pattern")
            for qa_type, content in matches2:
                speaker = "Interviewer" if qa_type == "Q" else "Interviewee"
                structured_transcript.append({
                    "speaker": speaker,
                    "text": content.strip()
                })
            return structured_transcript

        # Pattern 3: Timestamp format "[HH:MM] Speaker: Text"
        pattern3 = re.compile(r"\[([0-9:]+)\]\s*([^:]+):\s*(.+?)(?=\n\[[0-9:]+\]|$)", re.DOTALL)
        matches3 = pattern3.findall(text)

        # If we found matches with pattern 3, process them
        if matches3:
            logger.info(f"Found {len(matches3)} matches with timestamp pattern")
            for timestamp, speaker, content in matches3:
                structured_transcript.append({
                    "timestamp": timestamp,
                    "speaker": speaker.strip(),
                    "text": content.strip()
                })
            return structured_transcript

        # If no patterns matched, return empty list
        logger.warning("No patterns matched in the transcript")
        return structured_transcript

    def identify_roles(self, speaker_texts: Dict[str, str]) -> Dict[str, str]:
        """
        Identify roles (interviewer vs interviewee) based on text patterns.

        Args:
            speaker_texts: Dictionary mapping speakers to their combined text

        Returns:
            Dictionary mapping speakers to their roles
        """
        logger.info("Identifying roles in transcript")
        roles = {}
        
        # Count the number of entries for each speaker
        speaker_counts = {speaker: len(text.split('\n')) for speaker, text in speaker_texts.items()}
        
        # Filter out speakers with very few entries (likely noise)
        min_entries = 2  # Minimum number of entries to be considered a real speaker
        valid_speakers = {speaker: count for speaker, count in speaker_counts.items() if count >= min_entries}
        
        # If we have no valid speakers, return empty roles
        if not valid_speakers:
            logger.warning("No valid speakers found with enough entries")
            return roles
        
        # If we have exactly two speakers, assume interviewer/interviewee roles
        if len(valid_speakers) == 2:
            speakers = list(valid_speakers.keys())
            # The speaker with fewer entries is likely the interviewer
            if valid_speakers[speakers[0]] < valid_speakers[speakers[1]]:
                roles[speakers[0]] = "Interviewer"
                roles[speakers[1]] = "Interviewee"
            else:
                roles[speakers[0]] = "Interviewee"
                roles[speakers[1]] = "Interviewer"
            logger.info(f"Identified roles for exactly two speakers: {roles}")
            return roles
        
        # For more than two speakers, use more complex heuristics
        for speaker, text in speaker_texts.items():
            # Skip speakers with very few entries
            if speaker not in valid_speakers:
                continue
                
            # Check for question patterns
            question_count = len(re.findall(r'\?', text))
            text_length = len(text)
            
            # If the text has a high ratio of questions, likely an interviewer
            if question_count > 0 and question_count / text_length > 0.01:
                roles[speaker] = "Interviewer"
            # If a speaker has very few entries compared to others, they're likely the interviewer
            elif valid_speakers[speaker] < sum(valid_speakers.values()) * 0.3:
                roles[speaker] = "Interviewer"
            else:
                roles[speaker] = "Interviewee"
        
        logger.info(f"Identified roles using heuristics: {roles}")
        return roles

    def extract_name_from_text(self, text: str, default_role: str) -> str:
        """
        Extract a person's name from text.

        Args:
            text: Text to extract name from
            default_role: Default role to use if no name is found

        Returns:
            Extracted name or default role
        """
        logger.info(f"Extracting name from text for {default_role}")
        
        # Pattern 1: Look for "Name: Text" patterns
        name_pattern = re.compile(r"^([A-Z][a-z]+ [A-Z][a-z]+):", re.MULTILINE)
        name_matches = name_pattern.findall(text)
        
        if name_matches:
            # Use the most common name
            name_counts = {}
            for name in name_matches:
                name_counts[name] = name_counts.get(name, 0) + 1
            
            if name_counts:
                most_common_name = max(name_counts.items(), key=lambda x: x[1])[0]
                logger.info(f"Extracted name from text: {most_common_name}")
                return most_common_name
        
        # Pattern 2: Look for "Interview with [Name]" or similar patterns
        interview_pattern = re.compile(r"[Ii]nterview (?:with|of) ([A-Z][a-z]+ [A-Z][a-z]+)")
        interview_matches = interview_pattern.findall(text)
        
        if interview_matches:
            logger.info(f"Extracted name from interview pattern: {interview_matches[0]}")
            return interview_matches[0]
        
        # Pattern 3: Look for transcript header with names
        header_pattern = re.compile(r"^([A-Z][a-z]+ [A-Z][a-z]+) - ([A-Z][a-z]+ [A-Z][a-z]+)")
        header_matches = header_pattern.findall(text)
        
        if header_matches:
            # If we're looking for the interviewer, use the first name
            if default_role == "Interviewer":
                logger.info(f"Extracted interviewer name from header: {header_matches[0][0]}")
                return header_matches[0][0]
            # If we're looking for the interviewee, use the second name
            else:
                logger.info(f"Extracted interviewee name from header: {header_matches[0][1]}")
                return header_matches[0][1]
        
        # If no name found, use the default role
        logger.info(f"No name found, using default role: {default_role}")
        return default_role

    def split_text_by_roles(self, text: str) -> Tuple[str, str]:
        """
        Split text into interviewer and interviewee parts.

        Args:
            text: Text to split

        Returns:
            Tuple of (interviewer_text, interviewee_text)
        """
        logger.info("Splitting text by roles")
        
        # Initialize empty strings for each role
        interviewer_text = ""
        interviewee_text = ""
        
        # Try different patterns to identify speakers
        
        # Pattern 1: Lines starting with "Q:" and "A:"
        q_pattern = re.compile(r"Q:\s*(.+?)(?=\n[QA]:|$)", re.DOTALL)
        a_pattern = re.compile(r"A:\s*(.+?)(?=\n[QA]:|$)", re.DOTALL)
        
        q_matches = q_pattern.findall(text)
        a_matches = a_pattern.findall(text)
        
        if q_matches and a_matches:
            logger.info(f"Found {len(q_matches)} Q: lines and {len(a_matches)} A: lines")
            interviewer_text = "\n".join(q_matches)
            interviewee_text = "\n".join(a_matches)
            return interviewer_text, interviewee_text
        
        # Pattern 2: Look for specific speaker patterns like "Speaker: Text"
        speaker_pattern = re.compile(r"([^:]+):\s*(.+?)(?=\n[^:]+:|$)", re.DOTALL)
        speaker_matches = speaker_pattern.findall(text)
        
        if speaker_matches:
            logger.info(f"Found {len(speaker_matches)} speaker: text patterns")
            
            # Group text by speaker
            speaker_texts = {}
            for speaker, content in speaker_matches:
                speaker = speaker.strip()
                if speaker not in speaker_texts:
                    speaker_texts[speaker] = []
                speaker_texts[speaker].append(content.strip())
            
            # Identify roles
            roles = self.identify_roles({s: "\n".join(t) for s, t in speaker_texts.items()})
            
            # Combine text by role
            for speaker, role in roles.items():
                if role == "Interviewer":
                    interviewer_text += "\n".join(speaker_texts.get(speaker, []))
                else:
                    interviewee_text += "\n".join(speaker_texts.get(speaker, []))
            
            if interviewer_text and interviewee_text:
                return interviewer_text, interviewee_text
        
        # If all else fails, try a simple 20/80 split (assuming interviewer speaks less)
        words = text.split()
        split_point = int(len(words) * 0.2)  # Assume interviewer is about 20% of the text
        
        interviewer_text = " ".join(words[:split_point])
        interviewee_text = " ".join(words[split_point:])
        
        logger.info("Used simple 20/80 split as fallback")
        return interviewer_text, interviewee_text

    def group_text_by_speaker(self, transcript: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Group text by speaker from a structured transcript.

        Args:
            transcript: List of transcript entries with speaker and text fields

        Returns:
            Dictionary mapping speakers to their combined text
        """
        logger.info("Grouping text by speaker")
        speaker_texts = {}
        
        for entry in transcript:
            speaker = entry.get("speaker", "Unknown")
            text = entry.get("text", "")
            
            if speaker not in speaker_texts:
                speaker_texts[speaker] = []
            
            speaker_texts[speaker].append(text)
        
        # Combine all text for each speaker
        return {speaker: "\n".join(texts) for speaker, texts in speaker_texts.items()}
