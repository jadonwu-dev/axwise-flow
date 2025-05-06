import logging
from typing import Optional, List, Dict
from backend.utils.common.config import Config

class MermaidDiagram:
    """
    Class to handle Mermaid diagram generation with validation.

    This version is designed to work without Streamlit dependencies,
    focusing on diagram validation and HTML generation.
    """

    def __init__(self):
        self.valid_keywords = Config.MERMAID_VALID_KEYWORDS
        self.height = Config.MERMAID_HEIGHT
        self.width = Config.MERMAID_WIDTH
        self.errors: List[Dict[str, str]] = []

    def validate_syntax(self, code: str) -> bool:
        """
        Validate Mermaid diagram syntax.

        Args:
            code (str): Mermaid diagram code to validate

        Returns:
            bool: True if syntax is valid, False otherwise
        """
        if not code or not isinstance(code, str):
            self.errors.append({
                "type": "invalid_input",
                "message": "Diagram code must be a non-empty string"
            })
            return False

        code = code.strip()
        if not any(code.startswith(keyword) for keyword in self.valid_keywords):
            self.errors.append({
                "type": "invalid_syntax",
                "message": f"Diagram must start with one of: {', '.join(self.valid_keywords)}"
            })
            return False

        # Check for common syntax errors
        if code.count("{") != code.count("}"):
            self.errors.append({
                "type": "syntax_error",
                "message": "Mismatched curly braces"
            })
            return False

        if code.count("[") != code.count("]"):
            self.errors.append({
                "type": "syntax_error",
                "message": "Mismatched square brackets"
            })
            return False

        if code.count("(") != code.count(")"):
            self.errors.append({
                "type": "syntax_error",
                "message": "Mismatched parentheses"
            })
            return False

        return True

    def generate_html(self, code: str) -> str:
        """
        Generate HTML for Mermaid diagram.

        Args:
            code (str): Validated Mermaid diagram code

        Returns:
            str: HTML code for rendering the diagram
        """
        return f"""
        <div class="mermaid-container">
            <pre class="mermaid">
                {code}
            </pre>
        </div>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }}
            }});
        </script>
        """

    def render(self, code: str) -> Optional[bool]:
        """
        Validate and generate HTML for a Mermaid diagram.

        This version doesn't actually render the diagram (no UI dependencies),
        but validates the code and generates the HTML that could be used to render it.

        Args:
            code (str): Mermaid diagram code to validate

        Returns:
            Optional[bool]: True if validation successful, False if failed, None if validation failed
        """
        self.errors = []  # Reset errors

        # Validate syntax
        if not self.validate_syntax(code):
            for error in self.errors:
                logging.error(f"{error['type']}: {error['message']}")
            logging.error(f"Mermaid syntax validation failed: {self.errors}")
            return None

        try:
            # Generate HTML (but don't render it)
            html = self.generate_html(code)
            logging.info("Mermaid diagram HTML generated successfully")
            return True

        except Exception as e:
            error_msg = f"Error generating Mermaid diagram HTML: {str(e)}"
            logging.error(error_msg)
            return False

def render_mermaid(code: str) -> Optional[bool]:
    """
    Wrapper function to validate Mermaid diagrams.

    This version doesn't actually render the diagram (no UI dependencies),
    but validates the code and generates the HTML that could be used to render it.

    Args:
        code (str): Mermaid diagram code

    Returns:
        Optional[bool]: True if validation successful, False if failed, None if validation failed
    """
    diagram = MermaidDiagram()
    return diagram.render(code)
