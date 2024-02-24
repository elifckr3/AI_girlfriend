import os
from src.clients.base_api_request import push_request
from src.utils import timeit
from src.system_conf import ELEVEN_LABS_KEY

BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"

# TODO bring to user or system config
VOICE_STABILITY = 0.6
VOICE_SIMILARITY_BOOST = 0.85

CURR_DIR = os.getcwd()


@timeit.PROFILE
def eleven_labs_tts(text: str, voice_id: str) -> tuple[int, bytes] | None:
    url = f"{BASE_URL}{voice_id}"

    api_key = os.environ.get(ELEVEN_LABS_KEY)

    if api_key is None:
        raise ValueError("ELEVEN_LABS_KEY is not set")

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": os.environ.get(ELEVEN_LABS_KEY),
        "Content-Type": "application/json",
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.85},
    }

    response = push_request(api_key, url, headers, data)

    return response.status_code, response.content
