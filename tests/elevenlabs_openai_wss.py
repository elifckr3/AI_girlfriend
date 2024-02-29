import asyncio
import websockets
import json
import base64
import shutil
import os
import subprocess
# from openai import AsyncOpenAI
from time import time
import sys
import logging

# Define API keys and voice ID
# OPENAI_API_KEY = ''
ELEVENLABS_API_KEY = ''
VOICE_ID = 'r5MkZndaqAG50VL1H2fz'

# Set OpenAI API key
# aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

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
    print("Elevenlabs Audio Stream Started")
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

    print("Started streaming audio")
    async for chunk in audio_stream:
        print("%s: Audio chunk received from elevenlabs websocket: %s KBs..."%(time(),sys.getsizeof(chunk)/1000))
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
            "xi_api_key": ELEVENLABS_API_KEY,
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
                    print("Connection closed")
                    break

        listen_task = asyncio.create_task(stream(listen()))
        print("%s: Receiving Chat GPT Response"%time())
        async for text in text_chunker(text_iterator):
            print(text, end="")
            await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))
        print()
        await websocket.send(json.dumps({"text": ""}))

        await listen_task


async def chat_completion(query):
    """Retrieve text from OpenAI and pass it to the text-to-speech function."""
    # response = await aclient.chat.completions.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': query}],
    # temperature=1, stream=True)
    response = "Hi, how are you, I am Allan Watts. Nice to meet you."
    response = response.split(" ")
    async def text_iterator():
        for chunk in response:
            delta = chunk + " "
            yield delta

    await text_to_speech_input_streaming(VOICE_ID, text_iterator())


# Main execution
if __name__ == "__main__":
    user_query = "Hello, tell me a short story of 50 words."
    print(user_query)
    asyncio.run(chat_completion(user_query))
    print("End")


