import yaml
import atexit
import threading
from time import time
from colorama import Fore, Style

from openhome.LLM import chatgpt
from openhome.voice_input_output.text_to_voice import text_to_speech
from openhome.voice_input_output.voice_to_text import record_and_transcribe
from openhome.add_arguments import get_initial_personality
from openhome.process_user_message import process_message
from openhome.personalities_manager import load_personality
from openhome.history_files.history_manager import store_history
from openhome.history_files.user_memory_manager import update_recent_history
from openhome.history_files.history_summarizer import summarize_history, get_summarized_conversation, exit_handler
from openhome.conversation_manager import manage_conversation
from openhome.utility import load_json
from openhome.personalities.mood_evolver import mood_evolver, get_customized_prompt
from openhome.voice_input_output.loading_sounds import play_loading_sound
import openhome.app_globals


def load_configuration():
    with open('openhome/config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def initialize_system(file_data):
    personality_id = get_initial_personality()
    personality = load_personality(personality_id=personality_id)
    mood_json = load_json(path='openhome/personalities/mood.json')
    with open('openhome/personalities/mood_evolving_instruction.txt', 'r') as file:
        mood_prompt_template = file.read()
    with open('openhome/personalities/emotion_detection_prompt.txt', 'r') as file:
        emotion_detection_prompt = file.read()
    for emotion in mood_json:
        mood_json[emotion] = 0
    openhome.app_globals.mood_json = mood_json
    return personality, [], mood_prompt_template, emotion_detection_prompt

def capture_user_input(file_data):
    return record_and_transcribe(file_data['openai_api_key'])

def process_user_interaction(user_message, personality, conversation, file_data):
    print(Fore.RED + f"{user_message}" + Style.RESET_ALL, end='\n')
    conversation = manage_conversation(user_message, conversation, role='user')
    is_valid_message, action_feedback = process_message(user_message, personality)
    if action_feedback and action_feedback.get('feedback'):
        handle_action_feedback(action_feedback, conversation, personality, file_data)
    return conversation, personality

def handle_action_feedback(action_feedback, conversation, personality, file_data):
    feedback_message = action_feedback['feedback'].get('feedback', '')
    text_to_speech(feedback_message, personality['voice_id'], file_data['elevenlabs_api_key'])
    manage_conversation(feedback_message, conversation, role='assistant')

def generate_response(conversation, personality, file_data, mood_prompt_template, emotion_detection_prompt, user_message):
    summarized_conversation = get_summarized_conversation()
    response = chatgpt(file_data['openai_api_key'], summarized_conversation, get_customized_prompt(personality['personality']))
    store_history(user_message, response)  # Adjusted to include both user and assistant messages
    return response

def handle_response(response, conversation, personality, file_data):
    print(Fore.YELLOW + f"{personality['name']}: {response}" + Style.RESET_ALL, end='\n')
    text_to_speech(response, personality['voice_id'], file_data['elevenlabs_api_key'])
    return manage_conversation(response, conversation, role='assistant')

def main_loop(personality, conversation, file_data, mood_prompt_template, emotion_detection_prompt):
    while True:
        if not conversation:  # Check if conversation is empty to play the greeting
            greeting = personality['greetings']
            print(f"Greeting: {greeting}")
            text_to_speech(greeting, personality['voice_id'], file_data['elevenlabs_api_key'])
            conversation = manage_conversation("", conversation, role='user')  # Use an empty string as placeholder

        user_message = capture_user_input(file_data)
        conversation, personality = process_user_interaction(user_message, personality, conversation, file_data)
        response = generate_response(conversation, personality, file_data, mood_prompt_template, emotion_detection_prompt, user_message)
        conversation = handle_response(response, conversation, personality, file_data)

def main():
    file_data = load_configuration()
    personality, conversation, mood_prompt_template, emotion_detection_prompt = initialize_system(file_data)
    atexit.register(exit_handler, file_data['openai_api_key'])
    main_loop(personality, conversation, file_data, mood_prompt_template, emotion_detection_prompt)

if __name__ == "__main__":
    main()