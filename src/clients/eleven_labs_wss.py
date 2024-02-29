import asyncio
import websockets
import json
import base64
import shutil
import subprocess
import logging
from time import time
import sys
import os
from src.utils import timeit
from src.system_conf import ELEVEN_LABS_KEY
print(ELEVEN_LABS_KEY)


def is_installed(lib_name):
    return shutil.which(lib_name) is not None


async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if not text is None:
            if buffer.endswith(splitters):
                yield buffer + " "
                buffer = text
            elif text.startswith(splitters):
                yield buffer + text[0] + " "
                buffer = text[1:]
            else:
                buffer += text

    if buffer:
        yield buffer + " "


async def stream(audio_stream):
    logging.debug("Elevenlabs Audio Stream Started")
    """Stream audio data using mpv player."""
    if not is_installed("mpv"):
        raise ValueError(
            "mpv not found, necessary to stream audio. "
            "Install instructions: https://mpv.io/installation/"
        )

    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    logging.debug("Started streaming audio")
    async for chunk in audio_stream:

        logging.debug("Audio chunk received from elevenlabs websocket: %s KBs..."%(sys.getsizeof(chunk)/1000))

        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()


async def text_to_speech_input_streaming(voice_id, text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_turbo_v2"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.85},
            "xi_api_key": os.environ.get(ELEVEN_LABS_KEY),
        }))

        async def listen():
            """Listen to the websocket for audio data and stream it."""
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get('isFinal'):
                        break
                except websockets.exceptions.ConnectionClosed:
                    logging.warn("Connection closed")
                    break

        listen_task = asyncio.create_task(stream(listen()))
        logging.debug("Start Audio Stream from Eleven Labs")
        async for text in text_chunker(text_iterator):
            await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))
        
        await websocket.send(json.dumps({"text": ""}))
        await listen_task


@timeit.PROFILE
async def eleven_labs_wss_tts(text: str, voice_id: str) -> tuple[int, bytes] | None:
    response = text.split(" ")
    async def text_iterator():
        for chunk in response:
            delta = chunk + " "
            yield delta

    await text_to_speech_input_streaming(voice_id, text_iterator())

