from datetime import datetime
from .config import Config

class SessionManager:
    """
    Session manager for the application.

    This class provides methods to manage session state without Streamlit dependencies.
    It uses a simple dictionary-based approach for session management.
    """

    # Class-level session state dictionary
    _session_state = {}

    @classmethod
    def initialize_session(cls):
        """Initialize all session state variables"""
        # Set session ID if not already set
        if 'session_id' not in cls._session_state:
            cls._session_state['session_id'] = datetime.now().strftime('%H:%M:%S')

        # Initialize all session state variables from config
        for key, value in Config.INITIAL_SESSION_STATE.items():
            if key not in cls._session_state:
                cls._session_state[key] = value

    @classmethod
    def reset_session(cls):
        """Reset all session state variables to their initial values"""
        for key, value in Config.INITIAL_SESSION_STATE.items():
            cls._session_state[key] = value
        cls._session_state['session_id'] = datetime.now().strftime('%H:%M:%S')

    @classmethod
    def update_user_inputs(cls, inputs):
        """Update user inputs in session state"""
        cls._session_state['user_inputs'] = inputs

    @classmethod
    def autofill_demo_values(cls):
        """Autofill form with demo values"""
        for key, value in Config.DEMO_VALUES.items():
            cls._session_state[key] = value
        cls._session_state['autofilled'] = True
        cls._session_state['user_inputs'] = [
            cls._session_state.get(f'q{i}_default_val', '') for i in range(1, 8)
        ] + [None]

    @classmethod
    def clear_form(cls):
        """Clear all form values"""
        for i in range(1, 8):
            cls._session_state[f'q{i}_default_val'] = ""
        cls._session_state['user_inputs'] = []
        cls._session_state['autofilled'] = False

    @classmethod
    def get_stage_results(cls, stage):
        """Get cached results for a specific stage"""
        return cls._session_state.get(f'gpt_results_{stage}', None)

    @classmethod
    def set_stage_results(cls, stage, results):
        """Cache results for a specific stage"""
        cls._session_state[f'gpt_results_{stage}'] = results

    @classmethod
    def update_menu_option(cls, selected_step):
        """Update menu option based on selected step"""
        step_mapping = {
            "Empathise": 0,
            "Define": 1,
            "Ideate": 2,
            "Prototype": 3,
            "Test": 4
        }
        cls._session_state['menu_option'] = step_mapping.get(selected_step, 0)

    @classmethod
    def get(cls, key, default=None):
        """Get a value from session state"""
        return cls._session_state.get(key, default)

    @staticmethod
    def add_question(question):
        """Add a question to the question list"""
        if 'question_list' not in st.session_state:
            st.session_state['question_list'] = []
        st.session_state['question_list'].append(question)

    @staticmethod
    def get_questions():
        """Get all questions from the question list"""
        return st.session_state.get('question_list', [])
