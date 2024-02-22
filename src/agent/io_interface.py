import io
import os
import logging
import tempfile
from enum import Enum
from clients.openai import chatgpt_ttt
from clients.eleven_labs import eleven_labs_tts
from clients.assembly import assembly_transcribe
from clients.local_microphone import local_transcribe
from pydub import AudioSegment
from pydub.playback import play


class STT_CLIENTS(Enum):
    INTERNAL = "internal"
    ASSEMBLY = "assembly"


class TTT_CLIENTS(Enum):
    INTERNAL = "internal"
    OPENAI = "openai"


class TTS_CLIENTS(Enum):
    INTERNAL = "internal"
    ELEVENLABS = "elevenlabs"


def speech_to_text():
    client = os.environ.get("STT_CLIENT", STT_CLIENTS.INTERNAL.value)

    text = None
    match client:
        case STT_CLIENTS.INTERNAL.value:
            text = local_transcribe()

        case STT_CLIENTS.ASSEMBLY.value:
            text = assembly_transcribe()

        case _:
            logging.error(f"Invalid client type: {client}")

    if text == "" or text is None:
        logging.error(f"Error STT: {text}")

    else:
        logging.debug(f"transcription: {text}")

    return text


def text_to_text(messages_input: str) -> str | None:
    client = os.environ.get("TTT_CLIENT", TTT_CLIENTS.OPENAI.value)

    logging.debug(f"TTT_CLIENT: {client}")

    text = None
    match client:
        case TTT_CLIENTS.INTERNAL.value:
            # TODO internal model
            pass

        case TTT_CLIENTS.OPENAI.value:
            text = chatgpt_ttt(messages_input=messages_input)

        case _:
            raise ValueError(f"Invalid client type: {client}")

    return text


def text_to_speech(text: str, voice_id: str) -> int:
    client = os.environ.get("TTS_CLIENT", TTS_CLIENTS.ELEVENLABS.value)

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
        logging.error(f"Error TTS: status={status}, content type={type(audio_bytes)}")

    elif status in (200, 1) and isinstance(audio_bytes, bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio_bytes)
            temp_file.flush()
            audio = AudioSegment.from_file(temp_file.name, format="mp3")

            play(audio)

    else:
        logging.error(f"Error TTS: {status}")

    return status
