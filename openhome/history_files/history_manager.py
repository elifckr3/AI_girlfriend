import json
import os

def store_history(user_message, assitant_message):
    """
    This function takes user message and assistant response to store them in history.json.

    Args:
        user_message (string): user message converted from voice to text using OpenAI service.
        assitant_message (string): Assistant message converted from voice to text using OpenAI service.
    """
    new_user_message = {
        "role": "user",  # user message
        "content": user_message
    }

    new_assitant_message = {
        "role": "assistant",  # assistant message
        "content": assitant_message
    }
    try:
        # Load existing history
        if os.path.isfile('openhome/history_files/history.json'):
            with open('openhome/history_files/history.json', 'r') as file:
                history = json.load(file)
        else:
            history = {'messages':[]}

        # Append the new message to the existing history
        history['messages'].append(new_user_message)
        history['messages'].append(new_assitant_message)

        # Write the updated history back to the file
        with open('openhome/history_files/history.json', 'w') as file:
            json.dump(history, file, indent=4)
    except Exception as e:
        print(e)
        print(history)
