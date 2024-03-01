import time
from src.agent.capability import Capability
from src.personality_conf import DummyCapabilityChoice


class TimerCapability(Capability):
    @classmethod
    def register_capability(cls):
        return cls(unique_name=DummyCapabilityChoice.TIMEOUT, hotwords=["delay", "timer"])

    def call(self):
        print("TIMER called")
        time.sleep(10)
