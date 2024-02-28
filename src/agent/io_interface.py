import os
import logging
import tempfile
from enum import Enum
from src.clients.openai import OpenAiClient
from src.clients.eleven_labs import eleven_labs_tts
from src.clients.assembly import assembly_transcribe
from src.clients.local_microphone import local_record_online_transcribe
from src.system_conf import get_conf, STT_CLIENT, TTT_CLIENT, TTS_CLIENT, SPEECH_OFF
from pydub import AudioSegment
from pydub.playback import play

# new imports dor deepgram
from src.clients.deepgram_test import DeepGram
from threading import Event

class STT_CLIENTS(Enum):
    INTERNAL = "internal"
    ASSEMBLY = "assembly"


class TTT_CLIENTS(Enum):
    INTERNAL = "internal"
    OPENAI = "openai"


class TTS_CLIENTS(Enum):
    INTERNAL = "internal"
    ELEVENLABS = "elevenlabs"


def get_client_from_env():
    def wrapper(client_type: str):
        return os.environ.get(client_type, None)

    return wrapper


def speech_to_text():
    client = get_conf(STT_CLIENT)

    logging.debug(f"STT_CLIENT: {client}")

    text = None
    match client:
        case STT_CLIENTS.INTERNAL.value:
            # text = local_record_online_transcribe()
            result_event = Event()
            # Create an instance of DeepGram
            deepgram_instance = DeepGram()
            recording = deepgram_instance.deepgram_trascription(result_event)
            print('recording', recording)
            result_event.wait() # Wait for the transcription to complete

        case STT_CLIENTS.ASSEMBLY.value:
            text = assembly_transcribe()

        case _:
            logging.error(f"Invalid client type: {client}")

    if text is None:
        logging.error(f"I/O Error STT: {text}")

    else:
        logging.debug(f"I/O STT transcription: {text}")

    return text


def text_to_text(messages_input: str) -> str | None:
    client = get_conf(TTT_CLIENT)

    logging.debug(f"TTT_CLIENT: {client}")

    text = None
    match client:
        case TTT_CLIENTS.INTERNAL.value:
            # TODO internal model
            pass

        case TTT_CLIENTS.OPENAI.value:
            text = OpenAiClient().ttt(messages_input=messages_input)

        case _:
            raise ValueError(f"Invalid client type: {client}")

    return text


def text_to_speech(text: str, voice_id: str) -> int:
    if os.environ.get(SPEECH_OFF):
        logging.debug("Speech is off")
        return 200

    client = get_conf(TTS_CLIENT)

    logging.debug(f"TTS_CLIENT: {client}")

    status = 0
    audio_bytes = None
    match client:
        case TTS_CLIENTS.INTERNAL.value:
            pass

        case TTS_CLIENTS.ELEVENLABS.value:
            status, audio_bytes = eleven_labs_tts(
                text=text,
                voice_id=voice_id,
            )

        case _:
            logging.error(f"Invalid client type: {client}")
            return

    if audio_bytes is None or not isinstance(audio_bytes, bytes):
        logging.error(
            f"I/O Error TTS: status={status}, content type={type(audio_bytes)}",
        )

    elif status in (200, 1) and isinstance(audio_bytes, bytes):
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_file:
            temp_file.write(audio_bytes)

            temp_file.flush()

            audio = AudioSegment.from_file(temp_file.name, format="mp3")

            play(audio)

    else:
        logging.error(f"I/O ERROR TTS: {status}")

    return status
