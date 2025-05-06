from pathlib import Path

def create_pdf(title: str, content: str, output_file: str) -> None:
    """
    Create a markdown report (PDF generation temporarily disabled)
    
    Args:
        title: Title of the report
        content: Markdown formatted content
        output_file: Path to save the file
    """
    # Convert PDF output path to markdown
    output_md = Path(output_file).with_suffix('.md')
    
    # Add title to content if not already present
    if not content.startswith(f'# {title}'):
        content = f'# {title}\n\n{content}'
    
    # Write markdown file
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(content)
