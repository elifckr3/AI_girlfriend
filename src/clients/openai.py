import os
import tempfile
from enum import Enum
import logging
import openai
from src.utils import timeit

from src.system_conf import (
    get_conf,
    OPENAI_TTT_MODEL,
    OPENAI_TTT_TEMPERATURE,
    OPENAI_TTT_FREQUENCY_PENALTY,
    OPENAI_TTT_PRESENCE_PENALTY,
    OPENAI_STT_MODEL,
    OPENAI_KEY,
)


class OpenAITTTModels(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"


class OpenAISTTModels(Enum):
    WHISPER_1 = "whisper-1"


class OpenAiClient:
    def __init__(self):
        api_key = os.environ.get(OPENAI_KEY)

        if api_key is None:
            raise ValueError("OPENAI_KEY is not set")

        openai.api_key = api_key

    @timeit.PROFILE
    def ttt(self, messages_input: list[str]):
        msg = [{"role": "system", "content": messages_input}]
        logging.debug("Sending msg to GPT: %s"%msg)
        try:
            model = get_conf(OPENAI_TTT_MODEL)
            logging.debug(f"OPENAI TTT model: {model}")

            temperature = get_conf(OPENAI_TTT_TEMPERATURE)
            logging.debug(f"OPENAI TTT temperature: {temperature}")

            frequency_penalty = get_conf(OPENAI_TTT_FREQUENCY_PENALTY)
            logging.debug(f"OPENAI TTT frequency_penalty: {frequency_penalty}")

            presence_penalty = get_conf(OPENAI_TTT_PRESENCE_PENALTY)
            logging.debug(f"OPENAI TTT presence_penalty: {presence_penalty}")

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

    @timeit.PROFILE
    def stt(self, mp3_buffer: bytes):
        transcription = None
        try:
            logging.debug("Transcription started Whisper-1 online ...")

            model = get_conf(OPENAI_STT_MODEL)

            logging.debug(f"OPENAI STT model: {model}")

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
                temp_file.write(mp3_buffer)

                temp_file.flush()

                temp_file.seek(0)

                result = openai.Audio.translate(model=model, file=temp_file)

            transcription = result["text"]

        except Exception as e:
            logging.error("Error %s" % e)

        else:
            if transcription is None:
                logging.error(f"Error OpenAI STT: {transcription}")

            elif isinstance(transcription, str):
                logging.debug(
                    f"OpenAI STT (transcription) empty string: {transcription}",
                )

            else:
                logging.debug(f"OpenAI STT (transcription): {transcription}")

        return transcription
