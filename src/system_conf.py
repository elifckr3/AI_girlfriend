import typer
import logging
from enum import Enum
from utils.prompt import Prompt, Question, QTypes
from agent.base import BotAgent, BotPersonalityDna, BotMoodAxiom
from utils.db import RedisConnect

db_connection = RedisConnect()

DEFAULT_SYS_CONF = {"FOO": "BAR"}


class SystemConfigPrompt(Prompt):
    def run(self) -> BotAgent:
        typer.secho("\n Configure OpenHome System settings: \n", fg=typer.colors.GREEN)

        # personality_type = self.prompt(
        #     [
        #         Question(
        #             name="start",
        #             qtype=QTypes.SELECT,
        #             message="Personality config type",
        #             enum_struct=PersonalityChoice,
        #         ),
        #         Question(
        #             name="existing chars",
        #             qtype=QTypes.SELECT,
        #             message="Chose available personality",
        #             choices=agents_available,
        #             when=lambda x: x["start"] == PersonalityChoice.COMMUNITY,
        #         ),
        #     ]
        # )

        typer.secho(
            f"\n Config successful \n",
            fg=typer.colors.GREEN,
        )

        return {}
