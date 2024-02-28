import os
from collections.abc import Callable
from pydantic import BaseModel, ConfigDict
import logging
from enum import Enum
from src.agent.memory import BotAgentMemory
from src.agent.io_interface import text_to_speech, speech_to_text, text_to_text
from src.agent.capability import Capability
from src.agent.message import RoleTypes, Message
from src.utils.db import RedisConnect
from src.utils.markdown_loader import prompt_loader
from src.utils.ip import get_ip_address

db_connection = RedisConnect()

CURR_DIR = os.getcwd()
PROMPT_TEMPLATE_PATH = f"{CURR_DIR}/src/agent/llm_prompt_strategy_templates/"


class AgentNameExistsError(Exception):
    def __init__(self, name: str):
        self.name = name
        self.message = f"Agent with name {name} already exists"
        super().__init__(self.message)


class BotMemoryUpdateType(Enum):
    DAILY = "day"
    WEEKLY = "week"


class BotPersonalityDna(BaseModel):
    description: str

    purpose: str

    language: str

    information: str

    @classmethod
    def create_new_personality_dna(cls):
        return cls(
            description="",
            purpose="",
            language="",
            information="",
        )

    @classmethod
    def get_field_prompt_text(cls, field_name: str):
        question_prompts = {
            "description": "What is the personality of this character ?",
            "purpose": "What is their purpose ?",
            "language": "How do they use language ?",
            "information": "What information do they know deeply ?",
            "cababilties": "What are the capabilities of the bot (seperate with (,) ) ?",
        }
        assert (
            field_name in question_prompts.keys()
        ), f"Field {field_name} not found in BotPersonalityDna model"

        return question_prompts[field_name]


class BotMoodAxiom(BaseModel):
    axiom: str

    response: str

    @classmethod
    def load_mood_axion(cls, mood_axion: dict):
        return cls(
            mood=mood_axion["mood"],
            action=mood_axion["action"],
        )


class BotMetadata(BaseModel):
    voice_api_id: str

    personality_dna: BotPersonalityDna

    mood_dna: list[BotMoodAxiom]

    @classmethod
    def load_meta(cls, meta: dict):
        return cls(
            voice_api_id=meta["voice_api_id"],
            personality_dna=BotPersonalityDna(**meta["personality_dna"]),
            mood_dna=meta["mood_dna"],
        )


class BotAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    unique_name: str

    user_id: str

    metadata: BotMetadata

    memory: BotAgentMemory

    capabilities: list[str]

    @property
    def cold_start_prompt(self):
        cold_start_prompt = prompt_loader(
            PROMPT_TEMPLATE_PATH + "tts_cold_start.md",
            {"personality_dna": self.metadata.personality_dna.model_dump()},
        )
        logging.debug(f"cold_start_prompt: {cold_start_prompt}")

        return cold_start_prompt

    @property
    def curr_message(self):
        logging.debug(f"FULL MSG HIST: {self.memory.full_message_history}")
        for message in reversed(self.memory.full_message_history):
            if message.role == RoleTypes.USER:
                return message.model_dump()

        return None

    @property
    def last_10_messages(self):
        return [msg.model_dump() for msg in self.memory.full_message_history[-10:]]

    @property
    def mood_evolver_prompt(self):
        mood_evolve_prompt = prompt_loader(
            PROMPT_TEMPLATE_PATH + "ttt_mood_evolver.md",
            {
                "personality_dna": self.metadata.personality_dna.model_dump(),
                "mood_dna": self.metadata.mood_dna,
                "curr_message": self.curr_message,
                "last_10_messages": self.last_10_messages,
            },
        )
        logging.debug(f"mood_evolve_prompt: {mood_evolve_prompt}")

        return mood_evolve_prompt

    @property
    def response_prompt(self):
        response_prompt = prompt_loader(
            PROMPT_TEMPLATE_PATH + "tts_response.md",
            {
                "personality_dna": self.metadata.personality_dna.model_dump(),
                "mood_instructions": self.metadata.mood_dna,
                "curr_message": self.curr_message,
                "last_10_messages": self.last_10_messages,
            },
        )
        logging.debug(f"response_prompt: {response_prompt}")

        return response_prompt

    @property
    def unique_db_key(self):
        return f"agent:{self.user_id}:{self.unique_name}"

    @classmethod
    def available_bots(self):
        base_key = "agent"
        agents = db_connection.read_many(base_key)
        agent_names = [agent["unique_name"] for agent in agents]
        logging.debug(f"Found ({len(agent_names)}) Agent(s) named: {agent_names}")
        return agent_names

    @classmethod
    def create(
        cls,
        name: str,
        voice_id: str,
        personality_dna: BotPersonalityDna,
        mood_dna: list[BotMoodAxiom],
        capabilities: list[str],
    ):
        ip_address = get_ip_address()
        logging.debug(f"IP Address: {ip_address}")

        if db_connection.exists(f"agent:{ip_address}:{name}"):
            logging.warning(f"Agent with name {name} already exists")

            raise AgentNameExistsError(name=name)

        else:
            logging.info(f"Creating new agent with name {name}")

            agent = cls(
                unique_name=name,
                user_id=ip_address,
                metadata=BotMetadata(
                    voice_api_id=voice_id,
                    personality_dna=personality_dna,
                    mood_dna=mood_dna,
                ),
                memory=BotAgentMemory.create_fresh_memory(),
                capabilities=capabilities,
            )

            agent.save()

            return agent

    @classmethod
    def find_agent(cls, name: str):
        ip_address = get_ip_address()
        logging.debug(f"IP Address: {ip_address}")

        bot_key = f"agent:{ip_address}:{name}"

        if not db_connection.exists(bot_key):
            logging.error(f"Agent named {name} does not exist")

            return None

        bot = db_connection.read(bot_key)

        metadata = BotMetadata.load_meta(bot["metadata"])

        memory = BotAgentMemory.load_memory(bot["memory"])

        return cls(
            unique_name=bot["unique_name"],
            user_id=bot["user_id"],
            metadata=metadata,
            memory=memory,
            capabilities=bot["capabilities"],
        )

    def save(self):
        save_obj = self.model_dump(exclude=["model_config"])
        db_connection.write(self.unique_db_key, save_obj)

    def save_message(self, message: str, role: RoleTypes):
        logging.debug(f"saving message '{message}' with role '{role.value}'")

        self.memory.full_message_history.append(
            Message(content=message, role=role.value),
        )
        self.save()

        logging.debug("saved message")

    def memory_update(self, update_type: BotMemoryUpdateType):
        # TODO
        logging.error(f"updating memory with ({update_type.value}) update type")

    def listen(self):
        return speech_to_text()

    def speak(self, response: str):
        text_to_speech(text=response, voice_id=self.metadata.voice_api_id)

    def manage_context(
        self,
        msgs: list[str],
        cold_start: bool = False,
    ) -> str | Callable | None:
        """
        Manage the context of the conversation
            - handles cold start
            - take user message
            - detect wake word # TODO
            - match capability
            - evolve current mood
            - generate response
        """
        logging.debug(f"managing context: {msgs}")

        capability = Capability.match_capability(msgs)

        if capability is not None:
            assert isinstance(
                capability,
                Capability,
            ), f"Invalid capability type: {type(capability)}"

            return capability

        if cold_start is True:
            response_prompt = self.cold_start_prompt

        else:
            mood_evolver_strat = text_to_text(messages_input=self.mood_evolver_prompt)

            logging.debug(f"mood evolving strategy (post TTT): {mood_evolver_strat}")

            self.save_message(message=mood_evolver_strat, role=RoleTypes.SYSTEM)
            # TODO ensure no race conditions can occur between save and read
            # - may need to have async await saves
            response_prompt = self.response_prompt

        response = text_to_text(messages_input=response_prompt)

        assert isinstance(response, str), f"Invalid response type: {type(response)}"

        return response
