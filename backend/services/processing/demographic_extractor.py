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
        # Gender patterns - only match explicit gender mentions
        self.gender_patterns = {
            "female": [
                "female",
                "woman",
                "women",
                "lady",
                "ladies",
                "girl",
                "she is",
                "her background",
                "herself",
            ],
            "male": [
                "male",
                "man",
                "men",
                "guy",
                "guys",
                "boy",
                "he is",
                "his background",
                "himself",
            ],
            "non-binary": [
                "non-binary",
                "non binary",
                "non-gendered",
                "genderqueer",
                "gender fluid",
                "they are",
                "their background",
            ],
        }

        # Known tools and software that should not be treated as locations
        self.known_tools = {
            "jira",
            "slack",
            "github",
            "confluence",
            "trello",
            "asana",
            "notion",
            "figma",
            "sketch",
            "adobe",
            "photoshop",
            "illustrator",
            "zoom",
            "teams",
            "skype",
            "salesforce",
            "hubspot",
            "tableau",
            "power bi",
            "excel",
            "word",
            "powerpoint",
            "google docs",
            "google sheets",
            "google slides",
            "dropbox",
            "onedrive",
            "aws",
            "azure",
            "docker",
            "kubernetes",
            "jenkins",
            "git",
            "visual studio",
            "intellij",
            "eclipse",
            "xcode",
            "android studio",
            "react",
            "angular",
            "vue",
        }

        # Experience level patterns
        self.experience_patterns = {
            "entry-level": [
                "entry level",
                "junior",
                "beginner",
                "novice",
                "starting",
                "entry",
                "new grad",
                "graduate",
            ],
            "mid-level": [
                "mid level",
                "intermediate",
                "mid-career",
                "experienced",
                "mid",
                "middle",
            ],
            "senior": [
                "senior",
                "lead",
                "expert",
                "advanced",
                "principal",
                "sr",
                "staff",
            ],
            "executive": [
                "executive",
                "director",
                "chief",
                "head of",
                "vp",
                "c-level",
                "cxo",
                "ceo",
                "cto",
                "cfo",
            ],
        }

        # Age range patterns
        self.age_patterns = {
            "18-24": [
                "early twenties",
                "college age",
                "university age",
                "18-24",
                "early 20s",
                "20-24",
                "young adult",
            ],
            "25-34": [
                "late twenties",
                "early thirties",
                "25-34",
                "late 20s",
                "early 30s",
                "young professional",
            ],
            "35-44": [
                "mid thirties",
                "early forties",
                "35-44",
                "mid 30s",
                "early 40s",
                "mid-career",
            ],
            "45-54": [
                "mid forties",
                "early fifties",
                "45-54",
                "mid 40s",
                "early 50s",
                "established",
            ],
            "55-64": [
                "mid fifties",
                "early sixties",
                "55-64",
                "mid 50s",
                "early 60s",
                "senior",
            ],
            "65+": [
                "retired",
                "senior citizen",
                "65+",
                "late 60s",
                "70s",
                "elderly",
                "retiree",
            ],
        }

        # Education patterns
        self.education_patterns = {
            "high school": ["high school", "secondary education", "ged", "diploma"],
            "associate": [
                "associate degree",
                "associate's",
                "associates",
                "community college",
                "technical school",
            ],
            "bachelor": [
                "bachelor",
                "bachelor's",
                "bachelors",
                "undergraduate",
                "college",
                "university",
                "bs",
                "ba",
                "bfa",
            ],
            "master": [
                "master",
                "master's",
                "masters",
                "graduate degree",
                "ms",
                "ma",
                "mfa",
                "mba",
            ],
            "doctorate": [
                "phd",
                "doctorate",
                "doctoral",
                "doctor of",
                "postdoctoral",
                "post-doctoral",
            ],
        }

        # Industry patterns
        self.industry_patterns = {
            "tech": [
                "tech",
                "technology",
                "software",
                "it",
                "computer",
                "digital",
                "web",
                "app",
                "startup",
            ],
            "design": [
                "design",
                "creative",
                "art",
                "graphic",
                "ux",
                "ui",
                "user experience",
                "visual",
                "product design",
                "design community",
                "designer",
                "design work",
            ],
            "healthcare": [
                "healthcare",
                "medical",
                "health",
                "hospital",
                "doctor",
                "nurse",
                "patient",
                "clinical",
            ],
            "finance": [
                "finance",
                "financial",
                "banking",
                "investment",
                "accounting",
                "bank",
                "fintech",
            ],
            "education": [
                "education",
                "teaching",
                "academic",
                "school",
                "university",
                "college",
                "student",
                "professor",
            ],
            "retail": [
                "retail",
                "ecommerce",
                "e-commerce",
                "shop",
                "store",
                "consumer",
                "customer",
            ],
            "manufacturing": [
                "manufacturing",
                "factory",
                "production",
                "industrial",
                "assembly",
                "fabrication",
            ],
        }

        # Career stage patterns
        self.career_stage_patterns = {
            "student": [
                "student",
                "studying",
                "in school",
                "in college",
                "in university",
                "learning",
            ],
            "early career": [
                "early career",
                "just started",
                "new to",
                "beginning",
                "first job",
                "recent graduate",
            ],
            "mid career": [
                "mid career",
                "established",
                "experienced",
                "several years",
                "5-10 years",
            ],
            "late career": [
                "late career",
                "veteran",
                "seasoned",
                "long-time",
                "10+ years",
                "15+ years",
                "20+ years",
            ],
            "transitioning": [
                "transitioning",
                "changing careers",
                "pivoting",
                "switching",
                "moved from",
                "career change",
            ],
        }

    def extract_demographics(
        self, text_data: Dict[str, Any], all_evidence: List[str]
    ) -> Dict[str, Any]:
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
        logger.info(
            f"Evidence count: {len(demo_evidence)}, All evidence count: {len(all_evidence)}"
        )

        # Combine all text for analysis
        all_text = " ".join([demo_value] + demo_evidence + all_evidence)

        # Extract basic demographic information from lowercase text
        all_text_lower = all_text.lower()
        extracted_info = {
            "gender": self._extract_gender_carefully(all_text_lower),
            "experience_level": self._extract_pattern(
                all_text_lower, self.experience_patterns
            ),
            "age_range": self._extract_pattern(all_text_lower, self.age_patterns),
            "education": self._extract_pattern(all_text_lower, self.education_patterns),
            "industry": self._extract_pattern(all_text_lower, self.industry_patterns),
            "career_stage": self._extract_pattern(
                all_text_lower, self.career_stage_patterns
            ),
        }

        # Log extracted basic information
        logger.info(f"Extracted basic demographic information: {extracted_info}")

        # Extract work experience information (needs case-sensitive text for company names)
        work_experience = self._extract_work_experience(all_text)
        logger.info(
            f"Extracted work experience: companies={len(work_experience['companies'])}, roles={len(work_experience['roles'])}"
        )

        # Add company information if available
        if work_experience["companies"]:
            companies_str = ", ".join(
                work_experience["companies"][:3]
            )  # Limit to top 3
            extracted_info["companies"] = companies_str
            logger.info(f"Extracted companies: {companies_str}")

        # Add role information if available
        if work_experience["roles"]:
            roles_str = ", ".join(work_experience["roles"][:3])  # Limit to top 3
            extracted_info["roles"] = roles_str
            logger.info(f"Extracted roles: {roles_str}")

        # Add industry information if not already extracted
        if not extracted_info["industry"] and work_experience["industries"]:
            industries_str = ", ".join(
                work_experience["industries"][:2]
            )  # Limit to top 2
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

            logger.info(
                f"Mapped {years_of_experience} years to experience level: {extracted_info['experience_level']}"
            )

        # Extract location information
        location = self._extract_location(all_text)
        if location:
            extracted_info["location"] = location
            logger.info(f"Extracted location: {location}")

        # Format into structured output
        structured_demo = []

        # Order of importance for demographic categories
        priority_categories = [
            "gender",
            "experience_level",
            "career_stage",
            "roles",
            "companies",
            "industry",
            "age_range",
            "education",
            "location",
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
        if demo_value and not any(
            demo_value.lower() in item.lower() for item in structured_demo
        ):
            # Check if the original value has any information not already captured
            has_new_info = True
            for category, value in extracted_info.items():
                if value and value.lower() in demo_value.lower():
                    has_new_info = False
                    break

            if has_new_info:
                structured_demo.append(f"Profile: {demo_value}")

        # Create the final value with bullet points
        final_value = (
            "\n".join([f"• {item}" for item in structured_demo])
            if structured_demo
            else demo_value
        )

        logger.info(f"Final demographic value: {final_value}")

        # Add relevant evidence if not already present
        if not demo_evidence or len(demo_evidence) < 3:
            # Look for evidence related to demographics
            demographic_evidence = self._extract_demographic_evidence(all_evidence)
            if demographic_evidence:
                demo_evidence.extend(demographic_evidence)
                demo_evidence = list(set(demo_evidence))  # Remove duplicates
                logger.info(
                    f"Added {len(demographic_evidence)} demographic evidence items"
                )

        # Add work experience statements as evidence
        for company in work_experience["companies"]:
            # Find sentences containing this company
            sentences = re.split(r"(?<=[.!?])\s+", all_text)
            for sentence in sentences:
                if company in sentence and sentence not in demo_evidence:
                    demo_evidence.append(sentence)
                    break

        return {
            "value": final_value,
            "confidence": confidence,
            "evidence": demo_evidence,
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
            r"(\d+)\+?\s*years?\s*(of)?\s*(experience|in the field|in the industry)",
            r"(\d+)\+?\s*years?\s*(of)?\s*(work|professional)",
            r"worked\s*(for)?\s*(\d+)\+?\s*years",
            r"experience\s*(of)?\s*(\d+)\+?\s*years",
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

        # Common location patterns - improved to catch more variations
        patterns = [
            r"based\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"located\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"living\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"working\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"In\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # "In Italy"
            r"in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+we",  # "in Italy, we"
            r"([A-Z][a-z]+)\s+professional",  # "Italian professional"
        ]

        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches and matches.group(1):
                location = matches.group(1).strip()
                # Filter out known tools and software
                if location.lower() not in self.known_tools:
                    return location

        return None

    def _extract_gender_carefully(self, text: str) -> str:
        """
        Extract gender information more carefully to avoid false positives.

        Args:
            text: Text to extract from

        Returns:
            Gender or empty string if not found
        """
        # Only return gender if there's EXPLICIT and CLEAR evidence
        # Require strong contextual evidence, not just pronouns
        explicit_gender_indicators = {
            "female": [
                "i am a woman",
                "i am female",
                "as a woman",
                "being a woman",
                "woman in",
                "female professional",
                "she identifies as",
                "identifies as female",
            ],
            "male": [
                "i am a man",
                "i am male",
                "as a man",
                "being a man",
                "man in",
                "male professional",
                "he identifies as",
                "identifies as male",
            ],
            "non-binary": [
                "i am non-binary",
                "i identify as non-binary",
                "non-binary person",
                "they/them pronouns",
                "identifies as non-binary",
            ],
        }

        # Check for explicit gender statements only
        for gender, patterns in explicit_gender_indicators.items():
            for pattern in patterns:
                if pattern in text:
                    return gender.title()

        return ""  # Return empty string - do not infer gender from pronouns alone

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
            "work_experience": [],
        }

        # Common company name patterns (improved to capture complete company descriptions)
        company_patterns = [
            # Complete company descriptions
            r"\b(?:at|for|with)\s+(?:a\s+)?((?:small|medium|mid-sized|large|big|major|global|international|local|regional|startup|established|leading|top|Fortune\s+\d+)\s+(?:tech|technology|software|consulting|marketing|financial|healthcare|retail|manufacturing|automotive|aerospace|pharmaceutical|biotech|fintech|edtech|healthtech|insurtech|proptech|regtech|legaltech|adtech|martech|hrtech|cleantech|agtech|foodtech|fashiontech|traveltech|realtech|sportstech|musictech|gametech|arttech|designtech|archtech|constructech|energytech|watertech|wastetech|recycletech|greentech|climatetech|carbontech|renewabletech|solartech|windtech|hydrotech|nucleartech|fossiltech|oiltech|gastech|coaltech|miningtech|metaltech|chemtech|materialtech|nanotech|biotech|medtech|pharmatech|devicetech|diagnostech|therapeutech|vaccinetech|drugtech|clinicaltech|hospitaltech|nursingtech|dentaltech|veterinarytech|mentaltech|behaviortech|cognitivetech|neurotech|braintech|mindtech|emotech|socialtech|communitytech|familytech|parenttech|childtech|babytech|pettech|animaltech|wildlifetech|conservationtech|environmentech|sustainabilitytech|circulartech|sharingtech|collaborativetech|cooperativetech|collectivetech|distributedtech|decentralizedtech|blockchaintech|cryptotech|defitech|nfttech|metaversetech|vrtech|artech|mrtech|xrtech|aitech|mltech|dltech|nlptech|cvtech|robotech|autotech|dronetech|spacetech|satellitetech|rockettech|launchtech|orbittech|planetech|moontech|marstech|solartech|stellartech|galaxytech|universetech|cosmostech|quantumtech|atomtech|particletech|physicstech|chemistrytech|biologytech|genetech|genomtech|proteomtech|metabolomtech|microbiomtech|immunotech|stemtech|regentech|longevitytech|agingtech|deathtech|cryotech|transhumantech|cyborgtech|enhancementtech|augmentationtech|implanttech|prosthetictech|exoskeletontech|wearabletech|iottech|sensortech|actuatortech|controltech|automationtech|industrialtech|manufacturingtech|3dprinttech|additivetech|subtractivetech|machiningtech|toolingtech|moldingtech|castingtech|forgingtech|weldingtech|cuttingtech|drillingtech|millingtech|turningtech|grindingtech|polishingtech|finishingtech|coatingtech|paintingtech|platingtech|anodizingtech|galvanizingtech|chrometech|nickeltech|goldtech|silvertech|coppertech|aluminumtech|steeltech|irontech|titaniumtech|carbontech|fibertech|compositetech|plastictech|polymertech|rubbertech|elastomertech|foamtech|geltech|liquidtech|gastech|solidtech|crystaltech|ceramictech|glasstech|silicontech|semiconductortech|chiptech|processortech|memorytech|storagetech|displaytech|screentech|touchtech|keyboardtech|mousetech|trackpadtech|speakertech|microphonetech|cameratech|lenstech|projectortech|printertech|scannertech|faxtech|copiertech|shreddertech|laminertech|bindertech|staplertech|papertech|inktech|tonertech|ribbontech|labeltech|stickertech|tapetech|gluetech|adhesivetech|fastenertech|screwtech|bolttech|nuttech|washertech|springtech|bearingtech|geartech|motortech|enginetech|turbinetech|generatortech|batterytech|fuelcelltech|solartech|windtech|hydrotech|geothermaltech|nucleartech|fusiontech|fissiontech|reactortech|acceleratortech|collidertech|detectortech|telescopetech|microscopetech|spectrometertech|chromatographtech|electrophoresistech|centrifugetech|incubatortech|bioreactortech|fermentertech|distillationtech|extractiontech|purificationtech|separationtech|filtrationtech|membranetech|catalysttech|enzymetech|proteintech|peptidetech|aminoacidtech|nucleotidetech|dnatech|rnatech|genetech|chromosometech|celltech|tissuetech|organtech|bodytech|humantech|animaltech|planttech|microbialtech|viraltech|bacterialtech|fungaltech|algaltech|protozoaltech|archaealtech|extremophiletech|synbiotech|bioengtech|biotechtech|biopharmatech|biomaterialtech|biomimetictech|bioinspiredtech|biocompatibletech|biodegradabletech|biorenewabletech|biosustainabletech|biocirculartech|bioeconomytech|biorefiningtech|bioprocessingtech|bioconversiontech|biotransformationtech|biocatalysistech|bioremediation)\s+(?:company|corporation|corp|inc|llc|ltd|firm|business|enterprise|organization|startup|venture|group|team|lab|laboratory|institute|center|foundation|agency|bureau|department|division|unit|branch|office|facility|plant|factory|mill|shop|store|market|exchange|platform|network|system|service|solution|product|brand|label|line|series|suite|package|bundle|kit|set|collection|library|database|repository|archive|registry|catalog|directory|index|list|table|chart|graph|map|model|framework|architecture|infrastructure|stack|pipeline|workflow|process|procedure|protocol|standard|specification|guideline|policy|rule|regulation|law|act|bill|statute|code|ordinance|bylaw|charter|constitution|agreement|contract|treaty|pact|accord|deal|arrangement|partnership|alliance|coalition|consortium|syndicate|cartel|monopoly|oligopoly|duopoly|triopoly|quadropoly|quintopoly|sextopoly|septopoly|octopoly|nonopoly|decopoly|hendecapoly|dodecapoly|tridecapoly|tetradecapoly|pentadecapoly|hexadecapoly|heptadecapoly|octadecapoly|enneadecapoly|icosapoly|henicosapoly|docosapoly|tricosapoly|tetracosapoly|pentacosapoly|hexacosapoly|heptacosapoly|octacosapoly|enneacosapoly|triacontapoly))(?:\b|\.|\,)",
            # Specific company mentions
            r"\b(?:work(?:ed|ing)?|job|position|role|career|employ(?:ed|ee|er|ment)?|hired|join(?:ed)?)\s+(?:at|for|with)\s+(?:a\s+)?([A-Z][a-zA-Z0-9\s&\-\.]{2,30}?)(?:\s+(?:company|corp|inc|llc|ltd))?\s*(?:\b|\.|\,|\s(?:where|when|as|and|which|that))",
            # Company with legal suffixes
            r"\b([A-Z][a-zA-Z0-9\s&\-\.]{2,20})\s+(?:Inc|LLC|Ltd|GmbH|Corp|Corporation|Company|Co|Group|AG|SE|SA|SRL|BV|NV|PLC|LLP)(?:\b|\.|\,)",
        ]

        # Role patterns - improved to capture complete job titles
        role_patterns = [
            # Complete job titles with common endings
            r"\b(?:as|was|am|being|been|worked as|position as|role as|job as) (?:a |an |the )?((?:senior|junior|lead|principal|chief|head|staff|associate|assistant)?\s*(?:software|web|mobile|data|product|project|marketing|sales|business|technical|user experience|ux|ui|quality assurance|qa|devops|security|network|systems|database|full stack|front end|back end|frontend|backend)?\s*(?:development|developer|engineer|manager|director|lead|designer|researcher|analyst|consultant|specialist|architect|strategist|coordinator|administrator|supervisor|executive|officer|scientist|technician))(?:\b|\.|\,)",
            # Job titles at the beginning of sentences
            r"\b((?:senior|junior|lead|principal|chief|head|staff|associate|assistant)\s+(?:software|web|mobile|data|product|project|marketing|sales|business|technical|user experience|ux|ui|quality assurance|qa|devops|security|network|systems|database|full stack|front end|back end|frontend|backend)?\s*(?:development|developer|engineer|manager|director|lead|designer|researcher|analyst|consultant|specialist|architect|strategist|coordinator|administrator|supervisor|executive|officer|scientist|technician))(?:\s+(?:at|for|with|in))",
            # Team Lead and similar compound titles
            r"\b((?:team|technical|project|product|development|engineering|marketing|sales|business|data|security)\s+(?:lead|leader|manager|director|head|coordinator))(?:\b|\.|\,)",
        ]

        # Industry patterns
        industry_patterns = [
            r"\b(?:in|at|for) the ([a-zA-Z\s\-]+? industry)(?:\b|\.|\,)",
            r"\b([a-zA-Z\s\-]+? sector)(?:\b|\.|\,)",
            r"\b(?:work(?:ed|ing)? in|experience in|background in) ([a-zA-Z\s\-]+?)(?:\b|\.|\,)",
        ]

        # Work experience patterns (more general statements)
        experience_patterns = [
            r"\b(?:I have|with) (\d+(?:\.\d+)?) years? (?:of )?(?:work )?experience(?:\b|\.|\,)",
            r"\bworked (?:for|at) (?:a |an |the )?([a-zA-Z\s\-]+? company|startup|organization|agency|firm)(?:\b|\.|\,)",
            r"\b(?:started|beginning|early) (?:of )?(?:my|the) career(?:\b|\.|\,)",
            r"\b(?:transitioned|moved|switched) (?:from|to|into) ([a-zA-Z\s\-]+?)(?:\b|\.|\,)",
        ]

        # Extract companies
        for pattern in company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and match.group(1):
                    company = match.group(1).strip()
                    # Filter out common false positives and very short names
                    if (
                        company not in ["I", "We", "They", "The", "A", "An"]
                        and len(company) > 2
                        and company not in results["companies"]
                    ):
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
                    if (
                        len(experience) > 2
                        and experience not in results["work_experience"]
                    ):
                        results["work_experience"].append(experience)

        # Look for sentences containing work experience keywords
        work_keywords = [
            "career",
            "job",
            "position",
            "employment",
            "work",
            "professional",
        ]
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in work_keywords):
                # Check if this sentence contains information not already captured
                if not any(
                    item in sentence
                    for item in results["companies"]
                    + results["roles"]
                    + results["industries"]
                    + results["work_experience"]
                ):
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
            "background",
            "education",
            "degree",
            "graduated",
            "university",
            "college",
            "school",
            "experience",
            "years",
            "career",
            "job",
            "position",
            "role",
            "level",
            "senior",
            "junior",
            "mid",
            "age",
            "gender",
            "male",
            "female",
            "man",
            "woman",
            "location",
            "based in",
            "living in",
            "from",
            "moved",
            "transition",
            "industry",
            "company",
            "organization",
            "firm",
            "employer",
            "startup",
            "corporation",
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
                if re.search(r"\b" + re.escape(pattern) + r"\b", text):
                    return value.capitalize()
        return ""
