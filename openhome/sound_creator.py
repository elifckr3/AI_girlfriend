# from openhome.personalities_manager import load_personality
from utility import load_json
import requests
import yaml
from pydub import AudioSegment
from pydub.playback import play
import os
# Open the yaml file
with open('openhome/config.yaml', 'r', encoding='utf-8') as file:
    # Load all the data from the YAML file
    file_data = yaml.safe_load(file)


def generate_sounds(api_key, personality):
        voice_id = personality['voice_id']
        sounds = ['hmmm...', 'ok...', 'uh...']
        print(voice_id)
        for sound in sounds:
            url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
            headers = {
                'Accept': 'audio/mpeg',
                'xi-api-key': api_key,
                'Content-Type': 'application/json'
            }
            data = {
                'text': sound,
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
                with open('openhome/sounds/'+personality['name']+'/'+sound+'.mp3', 'wb') as f:
                    f.write(response.content)
                audio = AudioSegment.from_mp3('openhome/sounds/'+personality['name']+'/'+sound+'.mp3')
                play(audio)
            except Exception as e:
                print(e)
                continue


personalities = load_json('openhome/personalities/personalities.json')
for p_key in personalities:
    personality  = personalities[p_key]
    # Ensure the directory exists
    directory_path = 'openhome/sounds/' + personality['name']
    os.makedirs(directory_path, exist_ok=True)
    generate_sounds(file_data['elevenlabs_api_key'], personality)