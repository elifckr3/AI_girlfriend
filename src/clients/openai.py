import io
import os
import tempfile
from enum import Enum
import logging
import openai
from pydub import AudioSegment
from utils import timeit

from system_conf import (
    get_conf,
    OPENAI_TTT_MODEL,
    OPENAI_TTT_TEMPERATURE,
    OPENAI_TTT_FREQUENCY_PENALTY,
    OPENAI_TTT_PRESENCE_PENALTY,
    OPENAI_STT_MODEL,
)

API_KEY = "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"


class OpenAITTTModels(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"


class OpenAISTTModels(Enum):
    WHISPER_1 = "whisper-1"


class OpenAiClient:
    def __init__(self):
        openai.api_key = API_KEY  # TODO

    @timeit.PROFILE
    def ttt(self, messages_input: list[str]):
        msg = [{"role": "system", "content": messages_input}]
        try:
            model = get_conf(OPENAI_TTT_MODEL)
            logging.debug(f"OPENAI TTT model: {model}")

            temperature = get_conf(OPENAI_TTT_TEMPERATURE)
            logging.debug(f"OPENAI TTT temperature: {temperature}")

            frequency_penalty = get_conf(OPENAI_TTT_FREQUENCY_PENALTY)
            logging.debug(f"OPENAI TTT frequency_penalty: {frequency_penalty}")

            presence_penalty = get_conf(OPENAI_TTT_PRESENCE_PENALTY)
            logging.debug(f"OPENAI TTT presence_penalty: {presence_penalty}")

            openai.api_key = API_KEY
            completion = openai.ChatCompletion.create(
                model=model,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=msg,
            )

            chat_response = completion["choices"][0]["message"]["content"]

        except Exception as e:
            logging.error("Error %s" % e)

        logging.debug(f"chat_response: {chat_response}")

        return chat_response

    # @timeit.PROFILE
    def stt(self, mp3_buffer: bytes):
        transcription = None
        try:
            logging.debug("Transcription started Whisper-1 online ...")

            model = get_conf(OPENAI_STT_MODEL)

            logging.debug(f"OPENAI STT model: {model}")

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
                temp_file.write(mp3_buffer)

                result = openai.Audio.translate(model=model, file=temp_file)

                temp_file.flush()

            transcription = result["text"]

        except Exception as e:
            logging.error("Error %s" % e)

        else:
            if transcription is None or transcription == "":
                logging.error(f"Error OpenAI STT: {transcription}")

            else:
                logging.debug(f"OpenAI STT (transcription): {transcription}")

        return transcription
