from openhome.LLM import chatgpt
from openhome.voice_input_output.text_to_voice import text_to_speech

from openhome.voice_input_output.voice_to_text import record_and_transcribe

# add_arguments file adds argumnets to our script.
from openhome.add_arguments import get_initial_personality

# import process_user_message modeule to make decisions
from openhome.process_user_message import process_message

# import personalties manager
from openhome.personalities_manager import load_personality

# all time history manager
from openhome.history_files.history_manager import store_history

# recent two chats storage maanger
from openhome.history_files.user_memory_manager import update_recent_history

# import conversation manager to manage and converge messages
from openhome.conversation_manager import manage_conversation

# import utilities load json function to load json
from openhome.utility import load_json

# for mood customization import mood eveloer function.
from openhome.personalities.mood_evolver import mood_evolver, get_customized_prompt
from openhome.voice_input_output.loading_sounds import play_loading_sound
# import global variable for playing loading sound
import openhome.app_globals
import re
from colorama import Fore, Style
import yaml
import json
from time import time
import threading


# Open the yaml file
with open('openhome/config.yaml', 'r', encoding='utf-8') as file:
    # Load all the data from the YAML file
    file_data = yaml.safe_load(file)

# call the function for adding arguments to this script and get arguments value passed from user.
personality_id =  get_initial_personality()

# get the personality dictioanry.
personality = load_personality(personality_id=personality_id)


# define the main function to call all functions pressetn in modules
def main(personality, conversation, mood_prompt_template, emotion_detection_prompt):
    """
    Main function takes personality, consersation,mood json and mood instructions to run the whole proceses for the passed conversation using specified 
    personality.

    Args:
        personality (str): Personality entered by user while running the main script.
        conversation (list): List of messages from user and asistant as a history.
        mood_prompt_template (str): Instructions string from mood evolving instruction text file.

    Returns:
        conversation (list): Updated list of messages from user and asistant as a history.
    """
    # if conversation has something record user data else say greetings.
    if conversation:
        # call record_and_transcribe to record user and convert it to text
        user_message = record_and_transcribe(file_data['openai_api_key'])

        # call the conversation manager to maintain conversation
        conversation = manage_conversation(user_message, conversation, role='user')


        # Adjusted to receive action feedback including pause control
        print('Processing message to check capabilities triggers and validity...')
        start_time = time()
        is_valid_message, action_feedback = process_message(user_message, personality)  # Updated to include personality
        end_time = time()
        print(f'Message processing completed in {end_time - start_time} seconds')

        # Handle action feedback for pausing and user feedback
        if action_feedback and action_feedback.get('feedback'):
            if action_feedback['command'] == "Switch Personality" and action_feedback['feedback']['result'] is not None:
                personality = dict(action_feedback['feedback']['result'])
            # Check if feedback is in expected dict format and extract message
            feedback_message = action_feedback['feedback']['feedback'] if isinstance(action_feedback['feedback'], dict) else action_feedback['feedback']
            # Check if feedback_message is a list or a single message, then iterate or directly convert to speech
            if isinstance(feedback_message, list):
                for message in feedback_message:
                    print(f'Action Feedback: {message}')
                    # Convert this feedback to speech
                    text_to_speech(str(message), personality['voice_id'], file_data['elevenlabs_api_key'])
                    # call the conversation manager to mantin conversation
                    conversation = manage_conversation(str(message),conversation, role='assistant')
                    return conversation, personality
            else:
                # convert message in str may other types can cause errors.
                feedback_message = str(feedback_message)
                print(f'Action Feedback: {feedback_message}')
                # Convert this feedback to speech
                text_to_speech(feedback_message, personality['voice_id'], file_data['elevenlabs_api_key'])
                # call the conversation manager to mantin conversation
                conversation = manage_conversation(feedback_message,conversation, role='assistant')
                return conversation, personality
            if action_feedback.get('pauseMain'):
                print('Pausing main conversation loop as requested by action.')
                # Assuming action_feedback includes a 'resumeEvent' to wait on
                if 'resumeEvent' in action_feedback:
                    action_feedback['resumeEvent'].wait()  # Wait for the capability script to signal completion
                print('Resuming main conversation loop.')

        # Check if the message was valid to continue processing
        if not is_valid_message:
            return conversation, personality
 
        # mood evolver function and the rest of your logic follows here...


        # if we want to set cusotmzied mood propmt set this global vairbale in globals to True.
        if openhome.app_globals.MOOD_EVOLVER_ENABLED and len(conversation) >= 4:
            mood_evolving_thread = threading.Thread(target=mood_evolver, args=(mood_prompt_template,file_data['openai_api_key'], emotion_detection_prompt))
            mood_evolving_thread.daemon = True
            mood_evolving_thread.start()
            # combine the initial and mood customized prompts
            openhome.app_globals.MOOD_EVOLVER_ENABLED = False
        prompt = get_customized_prompt(initial_prompt=personality['personality'])

        print(Fore.RED + f"prompt: {prompt}" + Style.RESET_ALL, end="'\n")
        # Start the loading function that runs till the chatgpt function's response  in a separate thread
        loading_thread = threading.Thread(target=play_loading_sound, args=(personality['loading_sounds'],))
        loading_thread.daemon = True
        loading_thread.start()

        start_time = time()
        print('Generating chatgpt response.')
        # call chatgpt function
        response = chatgpt(file_data['openai_api_key'], conversation, prompt)
        # Wait for the continuous thread to finish
        loading_thread.join()
        # set again the global variable to true to play sond again till the geenration of customized prompt.
        openhome.app_globals.play_loading_sound_global = False
        # update the global conversation variable to be used in mood evolving.
        openhome.app_globals.conversation = conversation
        end_time = time()
        total_time = end_time - start_time
        print('Chatgpt response generation completed in', total_time)
        print(Fore.YELLOW + f"{personality['name']}: {response}" + Style.RESET_ALL, end="'\n")

        print('Storing History')
        start_time = time()
        # log all history
        store_history(user_message, response)
        # update recent history
        update_recent_history(user_message, response)
        end_time = time()
        total_time = end_time - start_time
        print('History storage completed in', total_time)
        # call the conversation manager to mantin conversation
        conversation = manage_conversation(response,conversation, role='assistant')

        # format the mesage to remove unsed characters from the chat gpt response.
        formatted_message = re.sub(r'(Response:|Narration:|Image: generate_image:.*|)', '',response).strip()
    else:
        # on first iteration this code runs to say the greesting stored in yaml file
        formatted_message = personality['greetings']
        # adding a empty propmt in conversation just to signify the first iteration.
        conversation.append({"role": "user", "content": ''})

    


    # call text to speech function to convert returned text to speech
    print('Text to Speech conversion started.')
    start_time = time()
    text_to_speech(formatted_message, personality['voice_id'], file_data['elevenlabs_api_key'])
    end_time = time()
    total_time =  end_time - start_time
    print('Text to Speech conversion completed in', total_time)
    return conversation, personality


# get current mood from json
mood_json = load_json(path='openhome/personalities/mood.json')
# assign mood json to a global variable as we are implementing threading and we cannot get back values  from threaded function so easily.
openhome.app_globals.mood_json = mood_json
# read instructions file.
mood_prompt_template = ''
with open('openhome/personalities/mood_evolving_instruction.txt', 'r') as file:
    # Read the entire contents of the file into a variable
    mood_prompt_template = file.read()
# read the prompt to pass on to chatgpt for emotion detection.   
with open('openhome/personalities/emotion_detection_prompt.txt', 'r') as file:
    # Read the entire contents of the file into a variable
    emotion_detection_prompt = file.read()
conversation = []
while True:
    print('Starting')
    conversation, personality = main(personality, conversation, mood_prompt_template, emotion_detection_prompt)
