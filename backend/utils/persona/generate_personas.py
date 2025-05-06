import json
from pathlib import Path
from typing import Dict, Any, List
from .persona_analyzer import create_personas_from_interviews, PersonaAnalyzer
from backend.utils.report.report_generation import create_pdf
from backend.utils.data.data_transformer import transform_interview_data

def format_persona_for_display(persona: Dict[str, Any]) -> str:
    """Format persona data into a readable markdown structure"""
    # Handle both field names for backward compatibility
    persona_type = persona.get('persona_type', persona.get('persona', 'Unknown'))
    md = f"# {persona_type} Persona\n\n"

    # Core Attributes
    md += "## Core Attributes\n\n"
    core = persona['core_attributes']

    md += "### Tools & Methods\n"
    for tool in core['tools_used']:
        md += f"- {tool['pattern']} (Mentioned {tool['frequency']} times)\n"

    md += "\n### Planning Patterns\n"
    for pattern in core['planning_patterns']:
        md += f"- {pattern['pattern']}\n"

    md += "\n### Key Responsibilities\n"
    for resp in core['key_responsibilities']:
        md += f"- {resp['pattern']}\n"

    # Pain Points
    md += "\n## Pain Points & Needs\n\n"
    pain = persona['pain_points']

    md += "### Key Challenges\n"
    for challenge in pain['key_challenges']:
        # Show main keyword and related keywords
        title = f"- {challenge['keyword'].title()}"
        if challenge.get('related_keywords'):
            related = [k for k in challenge['related_keywords'] if k != challenge['keyword']]
            if related:
                title += f" (Related: {', '.join(related)})"
        md += f"{title}\n"

        # Show main statement first
        if challenge['statements']:
            md += f"  * {challenge['statements'][0]}\n"
            # Show supporting statements
            for stmt in challenge['statements'][1:]:
                md += f"    - {stmt}\n"

    md += "\n### Automation Needs\n"
    for need in pain['automation_needs']:
        md += f"- {need['pattern']}\n"

    # Collaboration Patterns
    md += "\n## Collaboration Style\n\n"
    collab = persona['collaboration_patterns']

    for theme_id, theme in collab['collaboration_patterns'].items():
        md += f"### Pattern {int(theme_id) + 1}\n{theme}\n\n"

    # Supporting Quotes
    md += "\n## Supporting Evidence\n\n"
    quotes = persona['supporting_quotes']

    if 'positive_experiences' in quotes:
        md += "### Positive Experiences\n"
        for quote in quotes['positive_experiences']:
            md += f"- \"{quote['quote']}\"\n  *(Context: {quote['context']})*\n"

    if 'challenges' in quotes:
        md += "\n### Challenge Quotes\n"
        for quote in quotes['challenges']:
            md += f"- \"{quote}\"\n"

    if 'automation' in quotes:
        md += "\n### Automation Desires\n"
        for quote in quotes['automation']:
            md += f"- \"{quote}\"\n"

    if 'flexibility' in quotes:
        md += "\n### Flexibility & Customization\n"
        for quote in quotes['flexibility']:
            md += f"- \"{quote}\"\n"

    # Metadata
    md += f"\n---\n*Analysis based on {persona['metadata']['num_respondents']} respondents "
    md += f"and {persona['metadata']['total_responses']} total responses.*\n"

    return md

def save_persona_files(persona: Dict[str, Any], output_dir: str) -> None:
    """Save persona data to markdown and JSON files"""
    try:
        # Get persona type consistently
        persona_type = persona.get('persona_type', persona.get('persona', 'Unknown'))
        base_name = persona_type.lower().replace(' ', '_')

        # Create markdown file
        md_path = Path(output_dir) / f'{base_name}_persona.md'
        md_content = format_persona_for_display(persona)
        md_path.write_text(md_content)

        # Create JSON file
        json_path = Path(output_dir) / f'{base_name}_persona.json'
        json_path.write_text(json.dumps(persona, indent=2))

        # Create PDF report
        create_pdf(
            title=f"{persona_type} Persona Profile",
            content=md_content,
            output_file=str(md_path)
        )

    except Exception as e:
        print(f"Error saving files for persona {persona_type}: {str(e)}")
        raise

def generate_persona_report(data: List[Dict[str, Any]], output_dir: str = 'personas') -> List[Dict[str, Any]]:
    """Generate persona profiles and save as reports"""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    try:
        # Transform data and generate personas
        transformed_data = transform_interview_data(data)
        personas = []

        for segment in transformed_data:
            try:
                # Generate persona profile
                analyzer = PersonaAnalyzer(segment)
                persona = analyzer.generate_persona_profile()
                personas.append(persona)

                # Save files immediately after generating each persona
                save_persona_files(persona, output_dir)

            except Exception as e:
                print(f"Error processing persona {segment.get('persona_type', 'Unknown')}: {str(e)}")
                continue

        if not personas:
            raise ValueError("No personas could be generated from the data")

        return personas

    except Exception as e:
        print(f"Error in persona generation: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        # Load and generate personas from sample data
        with open('sample-data/edu_interviews_syntethic.json', 'r') as f:
            data = json.load(f)
        personas = generate_persona_report(data, 'personas')
        print(f"Successfully generated {len(personas)} personas")
    except Exception as e:
        print(f"Error: {str(e)}")
