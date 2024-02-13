from openhome.capabilities.capabilities_manager import check_and_perform_action

def process_message(message, personality):
    """
    This function takes a user message and processes it to figure out the event to trigger.
    It now also requires the personality context to pass to capabilities manager.

    Args:
        message (str): String message of user generated from speech to text openai service.
        personality (dict): The current personality context.

    Returns:
        is_valid_message (bool): A boolean flag to indicate if the user has spoken something meaningful.
    """
    # Execute check and perform action with personality context
    action_feedback = check_and_perform_action(message, personality)
    
    # Assuming user message is valid if it triggers an action
    is_valid_message = bool(action_feedback)

    # Check if user message is empty or a simple trigger without meaningful content
    if message in ['.', '', 'you']:
        is_valid_message = False

    return is_valid_message, action_feedback
