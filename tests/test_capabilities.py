import pytest
import sys
import os
import logging
from src.utils.db import RedisConnect
from src.agent.capability import Capability

db_connection = RedisConnect()


def test_agent():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    capability = Capability.match_capability(msgs=["call"])

    assert capability is not None, "expected capability to be found"

    logging.debug(f"TESTING calling capability: {capability.unique_name}")

    capability.call()
