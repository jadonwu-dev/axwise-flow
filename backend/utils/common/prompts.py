# utils/prompts.py

def generate_dt_prompt(stage, user_inputs=None, testing=False):
    """
    Generate a design thinking prompt based on the stage and user inputs.

    Args:
        stage (str): The design thinking stage
        user_inputs (dict, optional): Dictionary of user inputs
        testing (bool, optional): Whether this is a test

    Returns:
        str: The generated prompt
    """
    if testing:
        prompt = "What is the capital of France?"
    else:
        # Default empty values if no user inputs provided
        if user_inputs is None:
            user_inputs = {}

        # Get user inputs with defaults
        q1 = user_inputs.get('q1_default_val', '')
        q2 = user_inputs.get('q2_default_val', '')
        q3 = user_inputs.get('q3_default_val', '')
        q4 = user_inputs.get('q4_default_val', '')
        q5 = user_inputs.get('q5_default_val', '')
        q6 = user_inputs.get('q6_default_val', '')
        q7 = user_inputs.get('q7_default_val', '')

        prompt = f"""
            Imagine you are a digital design thinking companion to help users with design thinking. There are 5 stages: EMPATHIZE, DEFINE, IDEATE, PROTOTYPE, TEST.

            We are now at the {stage} stage of the Design Thinking process.

            You have received the following inputs from a user:
            {q1}
            {q2}
            {q3}
            {q4}
            {q5}
            {q6}
            {q7}

            Specific to the {stage} stage, provide some commentary about the importance of this step and guiding questions the participant should think about.

            ONLY if I say that we are at the DEFINE step, include 5 possible problem statements based on the information provided.
            IF We are in the other 4 stages, do not include possible problem statements.

            Suggest common design thinking frameworks that may be relevant to the {stage} stage. Your commentary can leverage this framework.
        """
    return prompt

def generate_prototype_img_prompt(testing=False):
    if testing:
        prompts = ["Cat", "Dog", "Fish", "Mouse"]
    else:
        prompts = f"""
            Imagine you are a digital design thinking companion to help users with design thinking. There are 5 stages: EMPATHIZE, DEFINE, IDEATE, PROTOTYPE, TEST.

            You have received the following inputs from a user:
            {st.session_state.get('q1_default_val', '')}
            {st.session_state.get('q2_default_val', '')}
            {st.session_state.get('q3_default_val', '')}
            {st.session_state.get('q4_default_val', '')}
            {st.session_state.get('q5_default_val', '')}
            {st.session_state.get('q6_default_val', '')}
            {st.session_state.get('q7_default_val', '')}

            We are now at the PROTOTYPE stage.

            Give me a prompt for a text-to-image model to generate mock-ups of the possible PRODUCT.

            Your reply will only contain this prompt and no other additional info or explanation.
        """
    return prompts

def generate_user_journey_prompt(user_inputs=None):
    """
    Generate a user journey prompt based on user inputs.

    Args:
        user_inputs (dict, optional): Dictionary of user inputs

    Returns:
        str: The generated prompt
    """
    # Default empty values if no user inputs provided
    if user_inputs is None:
        user_inputs = {}

    # Get user inputs with defaults
    q1 = user_inputs.get('q1_default_val', '')
    q2 = user_inputs.get('q2_default_val', '')
    q3 = user_inputs.get('q3_default_val', '')
    q4 = user_inputs.get('q4_default_val', '')
    q5 = user_inputs.get('q5_default_val', '')
    q6 = user_inputs.get('q6_default_val', '')
    q7 = user_inputs.get('q7_default_val', '')

    prompt = f"""
        You are an AI assistant specialized in design thinking. Generate a user journey diagram based on the following user inputs.

        User Inputs:
        Q1: {q1}
        Q2: {q2}
        Q3: {q3}
        Q4: {q4}
        Q5: {q5}
        Q6: {q6}
        Q7: {q7}

        Current Stage: EMPATHISE

        Generate a user journey diagram in Mermaid syntax. Your response should contain only the Mermaid code starting with "flowchart LR" and nothing else. Keep the diagram concise and focused on key journey points to ensure it fits well horizontally.
    """
    return prompt

def generate_interview_prompt(question, context):
    prompt = f"""
        This is for a design thinking interview.

        Pretend you are being interviewed by a UX researcher. You have been asked: {question}

        You are to base your reply based on the following real-world user comments: {context}

        You can make up some examples, including stories.

        Sound casual and polite. Answer as though you are speaking from the perspective of a user.
    """
    return prompt
