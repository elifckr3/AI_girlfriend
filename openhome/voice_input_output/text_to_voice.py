# import requests to call apis and links
import requests
from pydub import AudioSegment
from pydub.playback import play
# for safely parsing an expression node or a Unicode
from ast import literal_eval

# function to convert text to speech
def text_to_speech(text, voice_id, api_key):
    """    
    This function takes text message voice id in which we have to convert using eleven labs api
    and eleven labs api key. It returns nothing it only plays the text to speech audio.

    Args:
        text (string): Text message to convert to speech using eleven labs service.
        voice_id (string): A string stored in yaml file for each agent.
        api_key (string): A string key for eleven labs service.
    """
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }
    response = ''
    # this try blocks check if the eleven lab api returns desired response or not.
    try:
        response = requests.post(url, headers=headers, json=data)
        with open('openhome/recordings/output.mp3', 'wb') as f:
            f.write(response.content)
        audio = AudioSegment.from_mp3('openhome/recordings/output.mp3')
        play(audio)
    # if there is error in api response code will fire except.
    except:   
        message = ''
        # decode response to get error details
        response_dictionary = literal_eval(response.content.decode('utf-8'))
        if "detail" in response_dictionary:
            message = response_dictionary["detail"]["message"]
        print(message)
