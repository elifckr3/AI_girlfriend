import time
from src.agent.capability import Capability


class TimerCapability(Capability):
    @classmethod
    def register_capability(cls):
        return cls(unique_name="timer", hotwords=["call", "timer"])

    def call(self):
        print("TIMER called")
        time.sleep(10)
