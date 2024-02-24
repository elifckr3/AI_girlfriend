import os
import tempfile
import logging
from io import BytesIO
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.playback import play
from clients.base_api_request import push_request
from utils import timeit

API_KEY = "15dec7728128dcdc7254dcfa7c1ab947"
BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"

# TODO bring to user or system config
VOICE_STABILITY = 0.6
VOICE_SIMILARITY_BOOST = 0.85

CURR_DIR = os.getcwd()


# @timeit.PROFILE
def eleven_labs_tts(text: str, voice_id: str) -> tuple[int, bytes] | None:
    url = f"{BASE_URL}{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.85},
    }

    response = push_request(API_KEY, url, headers, data)

    return response.status_code, response.content
