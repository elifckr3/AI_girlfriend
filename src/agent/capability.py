import os
import logging
import importlib
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Union
from collections.abc import Callable
from pydantic import BaseModel


class Capability(BaseModel, ABC):
    unique_name: str

    hotwords: list[str]  # TODO solve unique matching problem

    @abstractclassmethod
    def register_capability(cls) -> Union["Capability", None]:
        raise NotImplementedError

    @abstractmethod
    def call(self):
        raise NotImplementedError

    @classmethod
    def match_capability(cls, msg: str) -> Union["Capability", None]:
        assert isinstance(msg, str), "msg must be a string"

        for file_name in os.listdir("capabilities"):
            if file_name.endswith(".py") and file_name != "__init__.py":
                module_name = f"capabilities.{file_name[:-3]}"
                module = importlib.import_module(module_name)

                for name in dir(module):
                    obj = getattr(module, name)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, Capability)
                        and obj != Capability
                    ):
                        capability = obj.register_capability()

                        logging.debug(f"checking capability for hotwords: {capability}")

                        if capability is not None:
                            # Check if any of the hotwords match the input messages
                            # TODO fuzzy matching
                            # TODO hotword registration uniqueness
                            for hotword in capability.hotwords:
                                if any(hotword.lower() in msg.lower() for msg in msg):
                                    logging.debug(f"matched capability: {capability}")
                                    return capability

        #     # TODO find from db ?
        return None
