"""
PRD generation prompt templates for LLM services.
"""

from typing import Dict, Any
from backend.services.llm.prompts.industry_guidance import IndustryGuidance
import logging

logger = logging.getLogger(__name__)


class PRDGenerationPrompts:
    """
    PRD generation prompt templates.
    """

    @staticmethod
    def get_prompt(data: Dict[str, Any]) -> str:
        """
        Get PRD generation prompt.

        Args:
            data: Request data

        Returns:
            Prompt string
        """
        # Add support for direct PRD prompts if provided
        if "prompt" in data and data["prompt"]:
            # Use the prompt provided directly
            return data["prompt"]

        # Extract data for PRD generation
        text = data.get("text", "")
        personas = data.get("personas", [])
        patterns = data.get("patterns", [])
        insights = data.get("insights", [])
        themes = data.get("themes", [])
        industry = data.get("industry")
        prd_type = data.get("prd_type", "both")  # "operational", "technical", or "both"

        # Create context from available data
        context = PRDGenerationPrompts._create_context(
            text, personas, patterns, insights, themes
        )

        # Get industry-specific guidance if available
        if industry:
            industry_guidance = IndustryGuidance.get_prd_guidance(industry)
            return PRDGenerationPrompts.industry_specific_prompt(
                industry, industry_guidance, context, prd_type
            )

        # Fallback to standard PRD generation prompt
        return PRDGenerationPrompts.standard_prompt(context, prd_type)

    @staticmethod
    def _create_context(
        text: str, personas: list, patterns: list, insights: list, themes: list
    ) -> str:
        """
        Create context for PRD generation.

        Args:
            text: Interview text
            personas: List of personas
            patterns: List of patterns
            insights: List of insights
            themes: List of themes

        Returns:
            Context string
        """
        context = ""

        # Add personas summary
        if personas:
            context += "\n## PERSONAS\n"
            for i, persona in enumerate(
                personas[:2]
            ):  # Limit to 2 personas for context
                # Handle both dictionary and Pydantic object formats
                if hasattr(persona, "dict") and callable(getattr(persona, "dict")):
                    # It's a Pydantic model
                    persona_dict = persona.dict()
                    name = persona_dict.get("name", "Unnamed")
                    description = persona_dict.get("description", "No description")
                elif isinstance(persona, dict):
                    # It's a dictionary
                    persona_dict = persona
                    name = persona.get("name", "Unnamed")
                    description = persona.get("description", "No description")
                else:
                    # It's some other object, try to get attributes directly
                    name = getattr(persona, "name", "Unnamed")
                    description = getattr(persona, "description", "No description")
                    # Create a dictionary representation for consistent access below
                    persona_dict = {}
                    for field in [
                        "challenges_and_frustrations",
                        "needs_and_desires",
                        "pain_points",
                        "patterns",
                    ]:
                        if hasattr(persona, field):
                            persona_dict[field] = getattr(persona, field)

                context += f"\nPersona {i+1}: {name}\n"
                context += f"Description: {description}\n"

                # Add key fields
                for field in [
                    "challenges_and_frustrations",
                    "needs_and_desires",
                    "pain_points",
                ]:
                    if field in persona_dict:
                        field_data = persona_dict[field]
                        if isinstance(field_data, dict) and "value" in field_data:
                            context += f"{field.replace('_', ' ').title()}: {field_data['value']}\n"

                # Add patterns if available
                if "patterns" in persona_dict and isinstance(
                    persona_dict["patterns"], list
                ):
                    context += "Key Patterns:\n"
                    for pattern in persona_dict["patterns"][:5]:  # Limit to 5 patterns
                        context += f"- {pattern}\n"

        # Add patterns summary
        if patterns:
            context += "\n## PATTERNS\n"
            for pattern in patterns[:10]:  # Limit to 10 patterns
                if isinstance(pattern, dict):
                    context += f"- {pattern.get('pattern', pattern.get('name', 'Unnamed pattern'))}\n"
                elif isinstance(pattern, str):
                    context += f"- {pattern}\n"

        # Add insights summary
        if insights:
            context += "\n## INSIGHTS\n"
            for insight in insights[:10]:  # Limit to 10 insights
                if isinstance(insight, dict):
                    context += f"- {insight.get('topic', 'Unnamed')}: {insight.get('observation', '')}\n"
                    if "implication" in insight:
                        context += f"  Implication: {insight['implication']}\n"
                    if "recommendation" in insight:
                        context += f"  Recommendation: {insight['recommendation']}\n"
                    if "priority" in insight:
                        context += f"  Priority: {insight['priority']}\n"

        # Add themes summary
        if themes:
            context += "\n## THEMES\n"
            for theme in themes[:10]:  # Limit to 10 themes
                if isinstance(theme, dict):
                    context += f"- {theme.get('name', 'Unnamed')}: {theme.get('definition', '')}\n"

        return context

    @staticmethod
    def industry_specific_prompt(
        industry: str, industry_guidance: str, context: str, prd_type: str
    ) -> str:
        """
        Get industry-specific PRD generation prompt.

        Args:
            industry: Industry name
            industry_guidance: Industry-specific guidance
            context: Analysis context
            prd_type: Type of PRD to generate

        Returns:
            Prompt string
        """
        base_prompt = PRDGenerationPrompts.standard_prompt(context, prd_type)

        # Add industry-specific guidance
        industry_section = f"""
        INDUSTRY CONTEXT: {industry.upper()}

        {industry_guidance}

        Ensure all requirements and user stories are tailored to the specific needs and constraints of the {industry} industry.
        """

        # Insert industry guidance before the final instructions
        return base_prompt.replace(
            "FORMAT YOUR RESPONSE AS JSON",
            f"{industry_section}\n\nFORMAT YOUR RESPONSE AS JSON",
        )

    @staticmethod
    def standard_prompt(context: str, prd_type: str) -> str:
        """
        Get standard PRD generation prompt (domain-agnostic master blueprint).

        Args:
            context: Analysis context
            prd_type: Type of PRD to generate ("operational", "technical", or "both")

        Returns:
            Prompt string
        """
        # Base prompt with analysis context
        base_prompt = f"""
        You are a world-class strategic consultant and product manager.
        Based on the following research analysis context, generate a comprehensive, domain-agnostic PRD that can guide
        the creation of a new product, service, or initiative. Maintain explicit traceability from stakeholder problems
        to specifications and ensure prioritization is driven by business impact.

        {context}

        PHASE 1: STRATEGIC ANALYSIS & SYNTHESIS
        1) Thematic Analysis:
           - Identify core themes with BOTH a Frequency score (0.0–1.0) AND an Impact Score (Low | Medium | High).
             A 'High' Impact Score means direct and significant loss of revenue, client trust, operational capacity, or brand value.
        2) Stakeholder Synthesis:
           - Synthesize 2–4 stakeholder personas (from provided data), with concise goals and primary frustrations.
        3) Needs Assessment:
           - Split into two categories:
             a) Solution Requirements: what the solution must do or be
             b) Relationship Requirements: how we must communicate, train, support, and build trust while delivering

        PHASE 2: PROJECT DEFINITION DOCUMENT GENERATION
        - Produce two parts:
          Part A: Business Requirements Document (BRD) – the WHAT and WHY
          Part B: Implementation Blueprint – the HOW

        Part A (BRD) must include:
          1. Objectives: Clear, measurable objectives.
          2. Scope: Explicit Included and Excluded items for the initial version.
          3. Stakeholder Scenarios / Use Cases: Write scenarios (As a [persona], I need [goal], so that [benefit]).
             Each scenario MUST include a Justification section that links to a high-impact theme or persona pain point.
          4. Core Specifications: Non-technical specifications derived from scenarios.
             The priority of each specification MUST be determined by Impact Score × Frequency of the underlying need.
          5. Success Metrics: Specific, quantifiable metrics with targets and measurement methods.

        Part B (Implementation Blueprint) must include:
          1. Solution Overview: Overall approach to building and delivering.
          2. System/Solution Structure: Core components and how they interact (for services: delivery phases; for products: modules/components).
          3. Core Components & Methodology: Key materials, technologies, or methodologies.
          4. Key Implementation Tasks: Primary technical/operational tasks.
          5. Quality Assurance & Validation: Testing/validation plan to ensure fitness for purpose.

        PHASE 3: STRATEGIC & RELATIONAL REFINEMENTS
          1. Stakeholder Success Plan (Relationship Requirements): Concrete actions/features to build trust, ensure smooth
             adoption, and provide support (e.g., training workshops, transparent dashboards, dedicated contacts).
          2. Tiered Solution Models: If stakeholder scale/needs vary, propose tiered models with clear differences in
             scope, complexity, and likely investment.

        IMPORTANT CONSTRAINTS
        - Preserve explicit traceability: Every scenario must include a Justification linking back to specific high-impact
          themes or persona pain points. Specifications must reference the scenarios they satisfy.
        - Prioritization must be driven by Impact × Frequency (include the numeric frequency and categorical impact used).
        - Keep language domain-agnostic (no software-only jargon) while remaining concrete and actionable.
        - Only include content supportable by the provided analysis context.
        """

        # Tailor instructions by PRD type without changing the overall JSON shape
        if prd_type == "operational":
            base_prompt += """
            Generate an Operational PRD focusing on BRD and Implementation Blueprint. Include all PHASES and constraints.
            """
        elif prd_type == "technical":
            base_prompt += """
            Generate a Technical PRD emphasizing Implementation Blueprint details (structure, components, tasks, QA),
            while still summarizing BRD objectives/scope to maintain traceability. Include all PHASES and constraints.
            """
        else:
            base_prompt += """
            Generate BOTH Operational and Technical PRDs, ensuring consistency and shared traceability across parts.
            Include all PHASES and constraints.
            """

        # Strict JSON formatting with schema that preserves existing consumers and adds BRD/Blueprint containers
        base_prompt += """
        FORMAT YOUR RESPONSE AS JSON with the following structure (do not include markdown):
        {
          "prd_type": "operational" | "technical" | "both",
          "operational_prd": { // include if prd_type is "operational" or "both"
            // Part A: BRD – the WHAT and WHY
            "brd": {
              "objectives": [ { "title": "...", "description": "..." } ],
              "scope": { "included": ["..."], "excluded": ["..."] },
              "stakeholder_scenarios": [
                {
                  "scenario": "As a [persona], I need [goal], so that [benefit]",
                  "acceptance_criteria": ["Given ...", "When ...", "Then ..."],
                  "justification": {
                    "linked_theme": "Name of high-impact theme or persona pain point",
                    "impact_score": "High" | "Medium" | "Low",
                    "frequency": 0.0,
                    "evidence_quotes": ["verbatim quote 1", "verbatim quote 2"]
                  }
                }
              ],
              "core_specifications": [
                {
                  "id": "REQ-001",
                  "specification": "Non-technical specification statement",
                  "priority": "High" | "Medium" | "Low",
                  "weighting": {
                    "impact_score": "High" | "Medium" | "Low",
                    "frequency": 0.0,
                    "priority_basis": "Impact x Frequency"
                  },
                  "related_scenarios": ["scenario reference or id"]
                }
              ],
              "success_metrics": [
                { "metric": "...", "target": "...", "measurement_method": "..." }
              ]
            },

            // Part B: Implementation Blueprint – the HOW
            "implementation_blueprint": {
              "solution_overview": "High-level approach",
              "solution_structure": [
                { "component": "...", "role": "...", "interactions": ["..."] }
              ],
              "core_components_and_methodology": [
                { "name": "...", "details": "materials/technologies/methodologies" }
              ],
              "key_implementation_tasks": [
                { "task": "...", "dependencies": ["..."] }
              ],
              "quality_assurance_and_validation": [
                { "test_type": "...", "success_criteria": "..." }
              ],
              "stakeholder_success_plan": {
                "relationship_requirements": [
                  { "need": "trust/communication/training", "actions": ["..."] }
                ],
                "adoption_support": ["..."]
              },
              "tiered_solution_models": [
                { "tier": "Basic|Pro|Enterprise", "target_stakeholder": "SMB|Enterprise|...", "scope": "...", "complexity": "...", "investment": "relative" }
              ]
            },

            // Backward compatibility: mirror key BRD fields at top-level for existing UIs
            "objectives": [ { "title": "...", "description": "..." } ],
            "scope": { "included": ["..."], "excluded": ["..."] },
            "user_stories": [ // mirror: transform stakeholder_scenarios into user stories if needed
              {
                "story": "As a [persona], I want to [goal] so that [benefit]",
                "acceptance_criteria": ["Given ...", "When ...", "Then ..."],
                "what": "Feature/requirement (from specification)",
                "why": "Business/user value (from justification)",
                "how": "High-level approach"
              }
            ],
            "requirements": [ // mirror: map from core_specifications
              {
                "id": "REQ-001",
                "title": "Specification title",
                "description": "Spec description",
                "priority": "High|Medium|Low",
                "related_user_stories": ["..."]
              }
            ],
            "success_metrics": [ { "metric": "...", "target": "...", "measurement_method": "..." } ]
          },

          "technical_prd": { // include if prd_type is "technical" or "both"
            "objectives": [ { "title": "...", "description": "..." } ],
            "scope": { "included": ["..."], "excluded": ["..."] },
            "architecture": {
              "overview": "High-level architecture/structure",
              "components": [ { "name": "...", "purpose": "...", "interactions": ["..."] } ],
              "data_flow": "..."
            },
            "implementation_requirements": [
              { "id": "TECH-001", "title": "...", "description": "...", "priority": "High|Medium|Low", "dependencies": ["..."] }
            ],
            "testing_validation": [ { "test_type": "...", "description": "...", "success_criteria": "..." } ],
            "success_metrics": [ { "metric": "...", "target": "...", "measurement_method": "..." } ]
          }
        }

        STRICTNESS:
        - Output MUST be a single valid JSON object (no markdown). Use the exact field names above.
        - MANDATORY: Include operational_prd.brd and operational_prd.implementation_blueprint when operational_prd is present.
        - Do NOT omit keys; if a section has no content, include the key with an empty array/object rather than removing it.
        - Populate all fields that are applicable given the analysis context.
        - For prioritization, always include the Impact × Frequency rationale within weighting/priority.
        """

        return base_prompt
