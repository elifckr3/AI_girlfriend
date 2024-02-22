import os
import openai
import sounddevice as sd
import soundfile as sf
import logging

import speech_recognition as sr
from time import time

API_KEY = "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"
DURATION = 1

CURR_DIR = os.getcwd()


def local_transcribe():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=DURATION)
        logging.debug("Recording.")

        transcription = r.listen(source)
        recording = transcription.get_wav_data()

        logging.debug("Recording Complete.")

    start_time = time()

    logging.debug("Transcription started...")

    with open(f"{CURR_DIR}/openhome/recordings/myrecording.wav", "wb") as file:
        file.write(recording)

    with open(f"{CURR_DIR}/openhome/recordings/myrecording.wav", "rb") as file:
        openai.api_key = API_KEY
        result = openai.Audio.translate("whisper-1", file)

    transcription = result["text"]
    end_time = time()
    total_time = end_time - start_time

    logging.debug(f"Transcription completed in {total_time} seconds")

    return transcription
