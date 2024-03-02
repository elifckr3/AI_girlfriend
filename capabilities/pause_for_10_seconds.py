import time
from src.agent.capability import Capability
import logging


class TimerCapability(Capability):
    @classmethod
    def register_capability(cls):
        return cls(unique_name="timeout", hotwords=["pause for 10 seconds", "pause for ten seconds"])

    def call(self,agent):
        message = "Pause for 10 seconds Capability Called!"

        logging.info(message)

        agent.speak(response=message)
        time.sleep(10)
        return