"""
Demographic extractor module for extracting demographic information from text.
"""
import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DemographicExtractor:
    """
    Extracts demographic information from text.
    """

    def __init__(self):
        """
        Initialize the demographic extractor.
        """
        # Gender patterns
        self.gender_patterns = {
            "female": ["female", "woman", "women", "she", "her", "herself", "lady", "ladies", "girl"],
            "male": ["male", "man", "men", "he", "him", "himself", "guy", "guys", "boy"],
            "non-binary": ["non-binary", "non binary", "they", "them", "themselves", "non-gendered", "genderqueer", "gender fluid"]
        }

        # Experience level patterns
        self.experience_patterns = {
            "entry-level": ["entry level", "junior", "beginner", "novice", "starting", "entry", "new grad", "graduate"],
            "mid-level": ["mid level", "intermediate", "mid-career", "experienced", "mid", "middle"],
            "senior": ["senior", "lead", "expert", "advanced", "principal", "sr", "staff"],
            "executive": ["executive", "director", "chief", "head of", "vp", "c-level", "cxo", "ceo", "cto", "cfo"]
        }

        # Age range patterns
        self.age_patterns = {
            "18-24": ["early twenties", "college age", "university age", "18-24", "early 20s", "20-24", "young adult"],
            "25-34": ["late twenties", "early thirties", "25-34", "late 20s", "early 30s", "young professional"],
            "35-44": ["mid thirties", "early forties", "35-44", "mid 30s", "early 40s", "mid-career"],
            "45-54": ["mid forties", "early fifties", "45-54", "mid 40s", "early 50s", "established"],
            "55-64": ["mid fifties", "early sixties", "55-64", "mid 50s", "early 60s", "senior"],
            "65+": ["retired", "senior citizen", "65+", "late 60s", "70s", "elderly", "retiree"]
        }

        # Education patterns
        self.education_patterns = {
            "high school": ["high school", "secondary education", "ged", "diploma"],
            "associate": ["associate degree", "associate's", "associates", "community college", "technical school"],
            "bachelor": ["bachelor", "bachelor's", "bachelors", "undergraduate", "college", "university", "bs", "ba", "bfa"],
            "master": ["master", "master's", "masters", "graduate degree", "ms", "ma", "mfa", "mba"],
            "doctorate": ["phd", "doctorate", "doctoral", "doctor of", "postdoctoral", "post-doctoral"]
        }

        # Industry patterns
        self.industry_patterns = {
            "tech": ["tech", "technology", "software", "it", "computer", "digital", "web", "app", "startup"],
            "design": ["design", "creative", "art", "graphic", "ux", "ui", "user experience", "visual", "product design"],
            "healthcare": ["healthcare", "medical", "health", "hospital", "doctor", "nurse", "patient", "clinical"],
            "finance": ["finance", "financial", "banking", "investment", "accounting", "bank", "fintech"],
            "education": ["education", "teaching", "academic", "school", "university", "college", "student", "professor"],
            "retail": ["retail", "ecommerce", "e-commerce", "shop", "store", "consumer", "customer"],
            "manufacturing": ["manufacturing", "factory", "production", "industrial", "assembly", "fabrication"]
        }

        # Career stage patterns
        self.career_stage_patterns = {
            "student": ["student", "studying", "in school", "in college", "in university", "learning"],
            "early career": ["early career", "just started", "new to", "beginning", "first job", "recent graduate"],
            "mid career": ["mid career", "established", "experienced", "several years", "5-10 years"],
            "late career": ["late career", "veteran", "seasoned", "long-time", "10+ years", "15+ years", "20+ years"],
            "transitioning": ["transitioning", "changing careers", "pivoting", "switching", "moved from", "career change"]
        }

    def extract_demographics(self, text_data: Dict[str, Any], all_evidence: List[str]) -> Dict[str, Any]:
        """
        Extract demographic information from text data.

        Args:
            text_data: Dictionary containing demographic data
            all_evidence: List of evidence strings from other fields

        Returns:
            Dictionary with enhanced demographic information
        """
        # Get existing data
        demo_value = text_data.get("value", "")
        demo_evidence = text_data.get("evidence", [])
        confidence = text_data.get("confidence", 0.7)

        logger.info(f"Extracting demographics from value: {demo_value[:100]}...")
        logger.info(f"Evidence count: {len(demo_evidence)}, All evidence count: {len(all_evidence)}")

        # Combine all text for analysis
        all_text = " ".join([demo_value] + demo_evidence + all_evidence)

        # Extract basic demographic information from lowercase text
        all_text_lower = all_text.lower()
        extracted_info = {
            "gender": self._extract_pattern(all_text_lower, self.gender_patterns),
            "experience_level": self._extract_pattern(all_text_lower, self.experience_patterns),
            "age_range": self._extract_pattern(all_text_lower, self.age_patterns),
            "education": self._extract_pattern(all_text_lower, self.education_patterns),
            "industry": self._extract_pattern(all_text_lower, self.industry_patterns),
            "career_stage": self._extract_pattern(all_text_lower, self.career_stage_patterns)
        }

        # Log extracted basic information
        logger.info(f"Extracted basic demographic information: {extracted_info}")

        # Extract work experience information (needs case-sensitive text for company names)
        work_experience = self._extract_work_experience(all_text)
        logger.info(f"Extracted work experience: companies={len(work_experience['companies'])}, roles={len(work_experience['roles'])}")

        # Add company information if available
        if work_experience["companies"]:
            companies_str = ", ".join(work_experience["companies"][:3])  # Limit to top 3
            extracted_info["companies"] = companies_str
            logger.info(f"Extracted companies: {companies_str}")

        # Add role information if available
        if work_experience["roles"]:
            roles_str = ", ".join(work_experience["roles"][:3])  # Limit to top 3
            extracted_info["roles"] = roles_str
            logger.info(f"Extracted roles: {roles_str}")

        # Add industry information if not already extracted
        if not extracted_info["industry"] and work_experience["industries"]:
            industries_str = ", ".join(work_experience["industries"][:2])  # Limit to top 2
            extracted_info["industry"] = industries_str
            logger.info(f"Extracted industries: {industries_str}")

        # Extract additional information using regex patterns
        years_of_experience = self._extract_years_of_experience(all_text)
        if years_of_experience and not extracted_info["experience_level"]:
            # Map years to experience level
            if years_of_experience <= 2:
                extracted_info["experience_level"] = "Entry-level"
            elif years_of_experience <= 5:
                extracted_info["experience_level"] = "Mid-level"
            elif years_of_experience <= 10:
                extracted_info["experience_level"] = "Senior"
            else:
                extracted_info["experience_level"] = "Executive"

            logger.info(f"Mapped {years_of_experience} years to experience level: {extracted_info['experience_level']}")

        # Extract location information
        location = self._extract_location(all_text)
        if location:
            extracted_info["location"] = location
            logger.info(f"Extracted location: {location}")

        # Format into structured output
        structured_demo = []

        # Order of importance for demographic categories
        priority_categories = [
            "gender", "experience_level", "career_stage", "roles", "companies",
            "industry", "age_range", "education", "location"
        ]

        # Add categories in priority order
        for category in priority_categories:
            value = extracted_info.get(category)
            if value:
                formatted_category = category.replace("_", " ").title()
                structured_demo.append(f"{formatted_category}: {value}")

        # Add any remaining categories not in priority list
        for category, value in extracted_info.items():
            if category not in priority_categories and value:
                formatted_category = category.replace("_", " ").title()
                structured_demo.append(f"{formatted_category}: {value}")

        # Add general work experience statements if available
        if work_experience["work_experience"]:
            work_exp_str = work_experience["work_experience"][0]  # Use the first one
            if not any(work_exp_str in item for item in structured_demo):
                structured_demo.append(f"Work Experience: {work_exp_str}")

        # Add original value if it contains information not captured in structured fields
        if demo_value and not any(demo_value.lower() in item.lower() for item in structured_demo):
            # Check if the original value has any information not already captured
            has_new_info = True
            for category, value in extracted_info.items():
                if value and value.lower() in demo_value.lower():
                    has_new_info = False
                    break

            if has_new_info:
                structured_demo.append(f"Profile: {demo_value}")

        # Create the final value
        final_value = " | ".join(structured_demo) if structured_demo else demo_value

        logger.info(f"Final demographic value: {final_value}")

        # Add relevant evidence if not already present
        if not demo_evidence or len(demo_evidence) < 3:
            # Look for evidence related to demographics
            demographic_evidence = self._extract_demographic_evidence(all_evidence)
            if demographic_evidence:
                demo_evidence.extend(demographic_evidence)
                demo_evidence = list(set(demo_evidence))  # Remove duplicates
                logger.info(f"Added {len(demographic_evidence)} demographic evidence items")

        # Add work experience statements as evidence
        for company in work_experience["companies"]:
            # Find sentences containing this company
            sentences = re.split(r'(?<=[.!?])\s+', all_text)
            for sentence in sentences:
                if company in sentence and sentence not in demo_evidence:
                    demo_evidence.append(sentence)
                    break

        return {
            "value": final_value,
            "confidence": confidence,
            "evidence": demo_evidence
        }

    def _extract_years_of_experience(self, text: str) -> Optional[int]:
        """
        Extract years of experience from text.

        Args:
            text: Text to extract from

        Returns:
            Years of experience or None
        """
        import re

        # Look for patterns like "X years of experience" or "X+ years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(of)?\s*(experience|in the field|in the industry)',
            r'(\d+)\+?\s*years?\s*(of)?\s*(work|professional)',
            r'worked\s*(for)?\s*(\d+)\+?\s*years',
            r'experience\s*(of)?\s*(\d+)\+?\s*years'
        ]

        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                # Extract the number from the first capturing group
                for group in matches.groups():
                    if group and group.isdigit():
                        return int(group)

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location information from text.

        Args:
            text: Text to extract from

        Returns:
            Location or None
        """
        import re

        # Common location patterns
        patterns = [
            r'based\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'located\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'living\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'working\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]

        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches and matches.group(1):
                return matches.group(1)

        return None

    def _extract_work_experience(self, text: str) -> Dict[str, Any]:
        """
        Extract comprehensive work experience information from text.

        Args:
            text: Text to extract from

        Returns:
            Dictionary with companies, roles, and work experience
        """
        import re

        # Initialize results
        results = {
            "companies": [],
            "roles": [],
            "industries": [],
            "work_experience": []
        }

        # Common company name patterns (with word boundaries)
        company_patterns = [
            r'\b(?:work(?:ed|ing)?|job|position|role|career|employ(?:ed|ee|er|ment)?|hired|join(?:ed)?|at|for|with|in) (?:at|by|for|with|in)? (?:a |an |the )?([A-Z][a-zA-Z0-9\s&\-\.]+?)(?:\b|\.|\,|\s(?:for|where|when|as|and|which|that))',
            r'\b(?:my|the|our|their|previous|current|last|first) (?:company|employer|organization|workplace|firm) (?:is|was|called|named)? (?:a |an |the )?([A-Z][a-zA-Z0-9\s&\-\.]+?)(?:\b|\.|\,|\s(?:for|where|when|as|and|which|that))',
            r'\b([A-Z][a-zA-Z0-9]+?(?:\s[A-Z][a-zA-Z0-9]*?){0,2})(?:\s(?:Inc|LLC|Ltd|GmbH|Corp|Corporation|Company|Co|Group|AG|SE|SA|SRL|BV|NV|PLC|LLP))(?:\b|\.|\,)',
            r'\bstartup (?:called|named)? ([A-Z][a-zA-Z0-9\s&\-\.]+?)(?:\b|\.|\,)',
            r'\b(?:left|quit|resigned from) (?:a |an |the )?([A-Z][a-zA-Z0-9\s&\-\.]+?)(?:\b|\.|\,)'
        ]

        # Role patterns
        role_patterns = [
            r'\b(?:as|was|am|being|been|worked as|position as|role as|job as) (?:a |an |the )?([a-zA-Z\s\-]+?(?:designer|developer|manager|director|lead|engineer|researcher|analyst|consultant|specialist|architect|strategist))(?:\b|\.|\,)',
            r'\b(?:my|the|our|their|previous|current|last|first) (?:role|position|job|title) (?:is|was|as)? (?:a |an |the )?([a-zA-Z\s\-]+?)(?:\b|\.|\,)',
            r'\b((?:senior|junior|lead|principal|chief|head|staff) [a-zA-Z\s\-]+?)(?:\b|\.|\,)'
        ]

        # Industry patterns
        industry_patterns = [
            r'\b(?:in|at|for) the ([a-zA-Z\s\-]+? industry)(?:\b|\.|\,)',
            r'\b([a-zA-Z\s\-]+? sector)(?:\b|\.|\,)',
            r'\b(?:work(?:ed|ing)? in|experience in|background in) ([a-zA-Z\s\-]+?)(?:\b|\.|\,)'
        ]

        # Work experience patterns (more general statements)
        experience_patterns = [
            r'\b(?:I have|with) (\d+(?:\.\d+)?) years? (?:of )?(?:work )?experience(?:\b|\.|\,)',
            r'\bworked (?:for|at) (?:a |an |the )?([a-zA-Z\s\-]+? company|startup|organization|agency|firm)(?:\b|\.|\,)',
            r'\b(?:started|beginning|early) (?:of )?(?:my|the) career(?:\b|\.|\,)',
            r'\b(?:transitioned|moved|switched) (?:from|to|into) ([a-zA-Z\s\-]+?)(?:\b|\.|\,)'
        ]

        # Extract companies
        for pattern in company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and match.group(1):
                    company = match.group(1).strip()
                    # Filter out common false positives and very short names
                    if (company not in ["I", "We", "They", "The", "A", "An"] and
                        len(company) > 2 and
                        company not in results["companies"]):
                        results["companies"].append(company)

        # Extract roles
        for pattern in role_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and match.group(1):
                    role = match.group(1).strip()
                    if len(role) > 3 and role not in results["roles"]:
                        results["roles"].append(role)

        # Extract industries
        for pattern in industry_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and match.group(1):
                    industry = match.group(1).strip()
                    if len(industry) > 3 and industry not in results["industries"]:
                        results["industries"].append(industry)

        # Extract general work experience statements
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and match.group(1):
                    experience = match.group(1).strip()
                    if len(experience) > 2 and experience not in results["work_experience"]:
                        results["work_experience"].append(experience)

        # Look for sentences containing work experience keywords
        work_keywords = ["career", "job", "position", "employment", "work", "professional"]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in work_keywords):
                # Check if this sentence contains information not already captured
                if not any(item in sentence for item in results["companies"] + results["roles"] + results["industries"] + results["work_experience"]):
                    # Add the sentence as general work experience
                    results["work_experience"].append(sentence.strip())

        return results

    def _extract_demographic_evidence(self, all_evidence: List[str]) -> List[str]:
        """
        Extract evidence related to demographics.

        Args:
            all_evidence: List of all evidence strings

        Returns:
            List of demographic evidence
        """
        demographic_evidence = []

        # Keywords related to demographics
        demographic_keywords = [
            "background", "education", "degree", "graduated", "university",
            "college", "school", "experience", "years", "career", "job",
            "position", "role", "level", "senior", "junior", "mid", "age",
            "gender", "male", "female", "man", "woman", "location", "based in",
            "living in", "from", "moved", "transition", "industry", "company",
            "organization", "firm", "employer", "startup", "corporation"
        ]

        # Check each evidence item for demographic keywords
        for evidence in all_evidence:
            evidence_lower = evidence.lower()
            for keyword in demographic_keywords:
                if keyword in evidence_lower:
                    demographic_evidence.append(evidence)
                    break

        return demographic_evidence[:5]  # Limit to 5 most relevant evidence items

    def _extract_pattern(self, text: str, pattern_dict: Dict[str, List[str]]) -> str:
        """
        Extract a pattern from text.

        Args:
            text: Text to extract from
            pattern_dict: Dictionary of patterns to match

        Returns:
            Extracted value or empty string
        """
        for value, patterns in pattern_dict.items():
            for pattern in patterns:
                # Use word boundary to match whole words
                if re.search(r'\b' + re.escape(pattern) + r'\b', text):
                    return value.capitalize()
        return ""
