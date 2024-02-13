import json
import os

def update_recent_history(user_message, assitant_message):
    """
    This function takes user and assistant messages and store only 4 latest messages.

    Args:
        user_message (string): user message converted from voice to text using OpenAI service.
        assitant_message (string): Assistant message converted from voice to text using OpenAI service.
    """
    # Load existing history
    if os.path.isfile('openhome/history_files/recent_history.json'):
        with open('openhome/history_files/recent_history.json', 'r') as file:
            history = json.load(file)
    else:
        history = {'messages':[]}

    # Message to be added
    new_user_message = {
        "role": "user",  # user message
        "content": user_message
    }

    new_assistant_message = {
        "role": "assistant",  # assistant message
        "content": assitant_message
    }

    # Append the new message to the history
    history['messages'].append(new_user_message)
    history['messages'].append(new_assistant_message)

    # Keep only the last four messages
    history['messages'] = history['messages'][-4:]

    # Write the updated history back to the file
    with open('openhome/history_files/recent_history.json', 'w') as file:
        json.dump(history, file, indent=4)