# Processes history.json to extract trends and relevant information.
import json
from openhome.utility import load_json, load_txt_file
import openhome.LLM
import openai
import openhome.app_globals
import openhome.LLM


def summarize_history(api_key):
    """
    This function summarizes the user history by reading history.json file after extracting
    only user messages from history.

    Args:
        api_key (str): api key for openAI service.

    Returns:
        0: Returns nothing return 0 is ritten to terminate the function execution.
    """
    try:
        # Load existing history
        history = load_json(path="openhome/history_files/history.json")
        # get the messages list from dictionary.
        history_list = history['messages']
        user_messsages = []
        for message in history_list:
            if message['role'] == 'user':
                user_messsages.append(message)
        # load the history summarizer prompt.
        summarizer_prompt = load_txt_file('openhome/history_files/history_summarizer_prompt.txt')
        # call chatgpt function for history summarization.
        summary = openhome.LLM.chatgpt(api_key, user_messsages, summarizer_prompt)
        # write data into the text file.
        with open('openhome/history_files/summarized_history.txt', 'w') as file:
            # Read the entire contents of the file into a variable
            file.write(summary)
    except Exception as e:
        print(e)
    return 0

def get_summarized_conversation():
    """
    This funcytion reads conversation from global variable and inserts summarized hisory at first index
    for history logging.
    Returns:
        conversation (list): current conversation with history summary insrted at first index
    """
    # load the history summarizer prompt.
    with open('openhome/history_files/summarized_history.txt', 'r') as file:
        # Read the entire contents of the file into a variable
        summarized_history = file.read()
    # prepare the tidct template for summarized_history to provide it to chatgpt
    summarized_conversation = [{'role': 'user', "content": summarized_history}]
    # get conversation from global variable
    conversation = openhome.app_globals.conversation
    # insert summarized_history at first index of our conversation copied list.
    conversation.insert(0, summarized_conversation[0])
    return conversation 

def exit_handler(api_key):
    """
    This is the function that will execute on exiting the whole process.

    Args:
        api_key (str): api key for openAI service.

    Returns:
        0: Returns nothing return 0 is ritten to terminate the function execution.
    """
    print('Saving summary of recent conversation.')
    conversation = openhome.app_globals.conversation
    # load the history summarizer prompt.
    summarizer_prompt = load_txt_file('openhome/history_files/history_summarizer_prompt.txt')
    # call chatgpt function for history summarization.
    summary = openhome.LLM.chatgpt(api_key, conversation, summarizer_prompt)
    # write data into the text file.
    with open('openhome/history_files/recent_summarized_history.txt', 'w') as file:
        # Read the entire contents of the file into a variable
        file.write(summary)
    return 0