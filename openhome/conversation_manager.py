# It updates the ongoing conversation session with new messages.
# This is essential for keeping a record of the interaction history between the user and the assistant within a session.
# This serves as "temporary history" but is critical for generating coherent and contextually appropriate responses.
# ChatGPT normally does this. When you ask a follow up question, it has the context of the previous one.


def manage_conversation(message, conversation, role):
    """
    This function manages the current session conversation between user and assistant.

    Args:
        message (string): Message is the string passed with the corresponding role.
        conversation (list): List of dictionaries of messages.
        role (string): Role can be user or assistant.

    Returns:
        conversation (list): List of dictionaries of messages.
    """
    conversation.append({"role": role, "content": message})

    return conversation