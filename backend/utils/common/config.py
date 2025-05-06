# Configuration management for the application

class Config:
    # Demo values
    DEMO_VALUES = {
        'q1_default_val': "I'm a Product Designer with a focus on developing assistive technology tools to enhance the daily lives of individuals with disabilities.",
        'q2_default_val': "Our primary target audience includes individuals with physical impairments, specifically those who have mobility challenges. This ranges from elderly individuals with reduced dexterity to younger individuals who might have been born with or acquired physical limitations.",
        'q3_default_val': "Many daily tasks are challenging for our audience due to a lack of accessible devices. This hinders their independence and confidence daily.",
        'q4_default_val': "Mainstream design often overlooks disability needs, perceptions of high development costs, and a lack of empathy for unique challenges.",
        'q5_default_val': "Modular tools for customization, voice and gesture-controlled devices, and partnerships with therapists for insight.",
        'q6_default_val': "Yes, but they were often too specialized, expensive, or lacked aesthetics and durability.",
        'q7_default_val': "Increased user independence, high adoption rates, and positive user feedback indicating enhanced daily living."
    }

    # Design Thinking stages
    DT_STAGES = ["EMPATHISE", "DEFINE", "IDEATE", "PROTOTYPE", "TEST"]

    # Navigation emojis
    NAV_EMOJI = {
        "Empathise": "❤️",
        "Define": "🖊️",
        "Ideate": "💡",
        "Prototype": "🔧",
        "Test": "✅"
    }

    # Initial session state
    INITIAL_SESSION_STATE = {
        'menu_option': 0,
        'generated': 0,
        'autofilled': False,
        'persona_loaded': False,
        'session_id': None,  # Will be set at runtime
        'fwd_btn': False,
        'q1_default_val': "",
        'q2_default_val': "",
        'q3_default_val': "",
        'q4_default_val': "",
        'q5_default_val': "",
        'q6_default_val': "",
        'q7_default_val': "",
        'user_inputs': [],
        'generated_image': None,
        'question_list': []
    }

    # File paths
    SAMPLE_DATA_PATH = "sample-data/user_comments.json"

    # Mermaid configuration
    MERMAID_VALID_KEYWORDS = ["graph", "sequenceDiagram", "classDiagram", "flowchart"]
    MERMAID_HEIGHT = 600
    MERMAID_WIDTH = 1200

    # PDF configuration
    PDF_MARGIN_LEFT = 20
    PDF_MARGIN_TOP = 20
    PDF_TITLE_FONT = ("Helvetica", 'B', 16)
    PDF_HEADING_FONT = ("Helvetica", 'U', 14)
    PDF_BODY_FONT = ("Helvetica", '', 11)
