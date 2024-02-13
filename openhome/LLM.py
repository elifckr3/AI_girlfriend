# import openai 
import openai
import asyncio
from openhome.voice_input_output.loading_sounds import play_loading_sound

# import global variable for playing loading sound
import openhome.app_globals


# define the function to comminiucate with chatgpt.
def chatgpt(api_key, conversation, chatbot, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    """    
    This function calls chat gpt to get response for user query.
    This function take openai api key, conversation history, chatbot prompt and three other variables, temparatue,
    frequency_penalty and presence_penalty for openai configration.
    It returns assistant repsonse.

    Args:
        api_key (sting): Api key for open ai service.
        conversation (list): List of conversation history dictionaries of user and assistant.
        chatbot (string): String store in yaml file to be used as prompt for chat get.
        temperature (float, optional): A parameter taken by chatgpt. Defaults to 0.9.
        frequency_penalty (float, optional):  A parameter taken by chatgpt. Defaults to 0.2.
        presence_penalty (int, optional):  A parameter taken by chatgpt. Defaults to 0.

    Returns:
        chat_response (string): Assistant message to be converted to speech by TTS
    """
    chat_response = ''
    try:
        openai.api_key = api_key
        messages_input = conversation.copy()
        prompt = [{"role": "system", "content": chatbot}]
        messages_input.insert(0, prompt[0])
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=messages_input)
        chat_response = completion['choices'][0]['message']['content']
    except Exception as e:
        print('Error %s' %e)
    openhome.app_globals.play_loading_sound_global = False
    return chat_response




