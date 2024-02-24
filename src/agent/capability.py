import logging
from typing import Union
from collections.abc import Callable
from pydantic import BaseModel


class Capability(BaseModel):
    unique_name: str

    func: Callable

    @classmethod
    def match_capability(cls, msgs: list[str]) -> Union["Capability", None]:
        unique_name = None

        # TODO fuzzy matching
        for msg in msgs:
            if "call" in msg:
                unique_name = "pronto"

        if unique_name:
            # TODO find from db
            logging.debug(f"matched capability: {unique_name}")
            dummy_func = lambda: print("did you just butt dial me ?")
            return cls(unique_name=unique_name, func=dummy_func)

        return None

    def call(self):
        self.func()
