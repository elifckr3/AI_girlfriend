import yaml
import pytest
import sys
import os
import io
import logging

# import pyttsx
from gtts import gTTS
from pydantic import BaseModel
from utils.db import RedisConnect
from agent.base import BotAgent, AgentNameExistsError
from agent.capability import Capability
from agent.io_interface import STT_CLIENTS, TTS_CLIENTS, TTT_CLIENTS
from dev_tools.db_management import create_new_db
from system_conf import SystemConfigPrompt
from unittest.mock import patch

db_connection = RedisConnect()

DEFAULT_DATA_PATH = "dev_tools/default_data/default_personalities.yml"

# sys.path.append("src")


def test_agent():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    sys_conf = SystemConfigPrompt().default_config()

    logging.info(f"Initializing system with conf: {sys_conf}")

    for key, value in sys_conf.items():
        # logging.error(f"setting env var: {key} to {value}")
        os.environ[key] = value

    create_new_db()

    logging.debug("TESTING non unique name bot")
    with pytest.raises(AgentNameExistsError):
        BotAgent.create(
            "Allan Watts",
            voice_id="1",
            personality_dna={},
            mood_dna={},
            capabilities=[],
        )

    agent = BotAgent.find_agent("Allan Watts")

    assert agent.memory.full_message_history == [], "expected empty message history"

    logging.debug("TESTING manage context - on cold start")
    context = agent.manage_context([], cold_start=True)
    logging.debug(f"cold start context: {context}")
    assert isinstance(context, str), "expected cold start context to be a string"

    logging.debug("TESTING manage context - with capability match")
    context = agent.manage_context(["call"])
    assert isinstance(context, Capability), "expected context to be a Capability"
    logging.debug(f"capability context: {context.unique_name}")

    logging.debug("TESTING manage context - with mood evolver + multi words")
    context = agent.manage_context(
        ["random fluffy word", "maybe i said something else too"]
    )
    logging.debug(f"mood evolver final prompt: {context}")
    assert isinstance(context, str), "expected context to be a string"

    assert (
        len(agent.memory.full_message_history) == 1
    ), "expected 4 messages in history (3 user msgs + 1 system msg (mood_evolver_prompt))"

    logging.debug("TESTING ttt clients")

    for client in TTT_CLIENTS:
        # TODO
        if client == TTT_CLIENTS.INTERNAL:
            continue

        os.environ["TTT_CLIENT"] = client.value
        context = agent.manage_context(
            ["random fluffy word", "maybe i said something else too"]
        )
        assert isinstance(context, str), "expected context to be a string"

    logging.debug("TESTING listening")

    # agent.listen()
    for client in STT_CLIENTS:
        os.environ["STT_CLIENT"] = client.value

        if client == STT_CLIENTS.INTERNAL:
            tts = gTTS("hello")
            speech_bytes = io.BytesIO()
            tts.write_to_fp(speech_bytes)

            speech_bytes.seek(0)
            mp3_data = speech_bytes.read()

            with patch("clients.local_microphone._speech_recon_lib") as mock_inner:
                mock_inner.return_value = mp3_data

                agent.listen()
        else:
            agent.listen()

    logging.debug("TESTING speaking")

    for client in TTS_CLIENTS:
        # TODO
        if client == TTS_CLIENTS.INTERNAL:
            continue

        os.environ["TTS_CLIENT"] = client.value
        agent.speak("testing, testing 1, 2, 3... Allan out!")
