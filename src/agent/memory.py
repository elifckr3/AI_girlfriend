import datetime
from enum import Enum
import pytz
from pydantic import (
    BaseModel,
    model_serializer,
    Field,
    ConfigDict,
    SkipValidation,
    field_serializer,
)
from agent.message import Message


def default_user_memory_volume():
    return UserContextVolume(
        summary="",
        last_summarized=datetime.datetime.now(tz=pytz.UTC),
        relevant_messages=[],
    )


class UserContextVolume(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    summary: str

    last_summarized: datetime.datetime

    relevant_messages: list[Message]

    @field_serializer("last_summarized")
    def serialize_time(self, v):
        return v.isoformat()


class UserMemory(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # TODO prompt these questions if not known
    name: str = ""

    year_of_birth: int = 0

    likes: UserContextVolume = Field(
        default_factory=lambda: default_user_memory_volume()
    )

    dislikes: UserContextVolume = Field(
        default_factory=lambda: default_user_memory_volume()
    )

    @classmethod
    def load_user_memory(cls, memory: dict):
        return cls(
            name=memory["name"],
            year_of_birth=memory["year_of_birth"],
            likes=UserContextVolume(**memory["likes"]),
            dislikes=UserContextVolume(**memory["dislikes"]),
        )


class BotAgentMemory(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    full_message_history: list[Message]

    last_interaction_summation: str

    last_day_summation: str  # NOTE test within minute crons

    last_week_summation: str

    user_memory: UserMemory

    @classmethod
    def create_fresh_memory(cls):
        return cls(
            full_message_history=[],
            last_interaction_summation="",
            last_day_summation="",
            last_week_summation="",
            user_memory=UserMemory(),
        )

    @classmethod
    def load_memory(cls, memory: dict):
        user_memory = UserMemory.load_user_memory(memory["user_memory"])
        return cls(
            full_message_history=memory["full_message_history"],
            last_interaction_summation=memory["last_interaction_summation"],
            last_day_summation=memory["last_day_summation"],
            last_week_summation=memory["last_week_summation"],
            user_memory=user_memory,
        )
