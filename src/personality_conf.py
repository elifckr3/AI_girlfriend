import os
import typer
import logging
from enum import Enum
from src.utils.prompt import Prompt, Question, QTypes
from src.agent.base import BotAgent, BotPersonalityDna, BotMoodAxiom
from src.agent.io_interface import TTS_CLIENTS, text_to_speech_wss
from src.utils.db import RedisConnect

db_connection = RedisConnect()


class PersonalityChoice(Enum):
    COMMUNITY = "COMMUNITY personalities"
    NEW = "NEW personality"


# TODO add db id to capability function
class DummyCapabilityChoice(Enum):
    TIMEOUT = "timeout"
    SYSTEM_STATS = "system_stats"


# TODO - generalizing this will require a lot of user instructions
class PersonalityMoodAxioms(Enum):
    HAPPY = "Happiness"
    POSITIVE = "Positivity"
    SAD = "Sadness"
    ANGRY = "Angriness"
    FEARFUL = "Fearfullness"


class PersonalityConfigPrompt(Prompt):
    def run(self) -> BotAgent:
        typer.secho(
            "\n Welcome to OpenHome's Personality configuration: \n",
            fg=typer.colors.GREEN,
        )

        agent = None
        agents_available = BotAgent.available_bots()
        personality_type = self.prompt(
            [
                Question(
                    name="start",
                    qtype=QTypes.SELECT,
                    message="Personality config type",
                    enum_struct=PersonalityChoice,
                ),
                Question(
                    name="existing chars",
                    qtype=QTypes.SELECT,
                    message="Chose available personality",
                    choices=agents_available,
                    when=lambda x: x["start"] == PersonalityChoice.COMMUNITY,
                ),
            ],
        )

        if personality_type["start"] == PersonalityChoice.NEW:
            # prompt for NEW personality
            name = self._prompt_new_agent_name()
            voice = self._prompt_new_agent_voice()
            personality_dna = self._prompt_new_agent_personality()
            mood_dna = self._prompt_new_agent_mood()
            capabilities = self._prompt_new_agent_capabilities()

            agent = BotAgent.create(
                name=name,
                voice_id=voice,
                personality_dna=personality_dna,
                mood_dna=mood_dna,
                capabilities=capabilities,
            )

        else:
            # find COMMUNITY personality
            typer.secho(
                f"\n You have selected to spawn ({personality_type['existing chars']})\n",
                fg=typer.colors.GREEN,
            )

            agent = BotAgent.find_agent(personality_type["existing chars"])

        return agent

    def _prompt_new_agent_name(self):
        agents_available = BotAgent.available_bots()
        while True:
            # name must be unique - will retry forever
            name = self.prompt(
                [
                    Question(
                        name="name",
                        qtype=QTypes.TEXT,
                        message="Character's name ?",
                    ),
                ],
            )["name"]
            logging.debug(f"checking if {name} is available")
            if name in agents_available:
                typer.secho(
                    f"\n {name} already exists, please choose another name \n",
                    fg=typer.colors.RED,
                )

            else:
                break
        return name

    def _prompt_new_agent_voice(self):
        while True:
            # voice_id must be available on the API account (external or internal)
            voice = self.prompt(
                [
                    Question(
                        name="voice",
                        qtype=QTypes.TEXT,
                        message="Character's ElevenLabs voice id ?",
                    ),
                ],
            )["voice"]
            if voice is None:
                typer.secho(
                    f"\n {voice} no voice found in Eleven Labs account.\n",
                    fg=typer.colors.RED,
                )
                continue

            # check if voice exists on with client
            os.environ["TTS_CLIENT"] = TTS_CLIENTS.ELEVENLABS.value
            status = text_to_speech_wss(text="testing", voice_id=voice)
            api_voice_exists = lambda x, status=status: status in (200, 1)
            if not api_voice_exists(voice):
                typer.secho(
                    f"\n no voice_id ({voice}) found with Eleven Labs account. \n",
                    fg=typer.colors.RED,
                )

            else:
                break
        return voice

    def _prompt_new_agent_personality(self):
        typer.secho("\n Base Personality Description \n", fg=typer.colors.GREEN)

        personality_dna = self.prompt(
            [
                Question(
                    name=field_name,
                    qtype=QTypes.TEXT,
                    message=BotPersonalityDna.get_field_prompt_text(field_name),
                    multiline=True,
                )
                for field_name in BotPersonalityDna.model_fields.keys()
            ],
        )
        return BotPersonalityDna(**personality_dna)

    def _prompt_new_agent_mood(self):
        typer.secho("\n Base Mood Description \n", fg=typer.colors.GREEN)

        typer.secho("\n (Select axioms and then how the agent evolves) \n")

        moods_axioms = self.prompt(
            [
                Question(
                    name="mood_axioms",
                    qtype=QTypes.CHECK,
                    enum_struct=PersonalityMoodAxioms,
                    message="Choose mood categories for agent to engage with: ",
                ),
            ],
        )

        if moods_axioms is not None:
            mood_axiom_responses = self.prompt(
                [
                    Question(
                        name=f"{m}",
                        qtype=QTypes.TEXT,
                        message=f"Describe how the agent will evolve when they sense your {m.value.upper()}:",
                        multiline=True,
                    )
                    for m in moods_axioms["mood_axioms"]
                ],
            )

        mood_dna = [
            BotMoodAxiom(axiom=axiom, response=description)
            for axiom, description in zip(
                moods_axioms,
                mood_axiom_responses,
                strict=False,
            )
        ]
        return mood_dna

    def _prompt_new_agent_capabilities(self):
        capabilities = self.prompt(
            [
                Question(
                    name="capabilities",
                    qtype=QTypes.CHECK,
                    enum_struct=DummyCapabilityChoice,
                    message="Choose bot capabilities: ",
                ),
            ],
        )["capabilities"]
        return capabilities


# UserStartConfig().run()
