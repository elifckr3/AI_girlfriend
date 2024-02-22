import yaml
import pytest
import sys
import os
import json
import logging
from pydantic import BaseModel
from utils.db import RedisConnect
from agent.base import BotAgent, AgentNameExistsError
from agent.capability import Capability
from agent.io_interface import STT_CLIENTS, TTS_CLIENTS, TTT_CLIENTS
from dev_tools.db_management import create_new_db

db_connection = RedisConnect()

DEFAULT_DATA_PATH = "dev_tools/default_data/default_personalities.yml"

# sys.path.append("src")


def test_agent():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

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
        len(agent.memory.full_message_history) == 4
    ), "expected 4 messages in history (3 user msgs + 1 system msg (mood_evolver_prompt))"

    # logging.debug("TESTING ttt clients")
    # # XXX test all TTT_CLIENTS
    # for client in TTT_CLIENTS:
    #     os.environ["TTT_CLIENT"] = client
    #     context = agent.manage_context(
    #         ["random fluffy word", "maybe i said something else too"]
    #     )
    #     assert isinstance(context, str), "expected context to be a string"

    # logging.debug("TESTING listening")

    # # XXX - how to test these ? > mock audio buffer
    # agent.listen()
    # # XXX test all STT_CLIENTS
    # for client in STT_CLIENTS:
    #     os.environ["STT_CLIENT"] = client
    #     agent.listen()

    # logging.debug("TESTING speaking")

    # # XXX - how to test these ? > mock audio buffer
    # # XXX say testing
    # agent.speak("hello")
    # # XXX test all TTS_CLIENTS
    # for client in TTS_CLIENTS:
    #     os.environ["TTS_CLIENT"] = client
    #     agent.speak("hello")
