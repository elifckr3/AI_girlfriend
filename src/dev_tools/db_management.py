import os
import logging
import json
from pydantic import BaseModel
from agent.base import BotAgent, BotPersonalityDna, BotMoodAxiom
from utils.db import RedisConnect
from utils.markdown_loader import prompt_loader


db_connection = RedisConnect()

# CURR_DIR = os.getcwd()
DEFAULT_DATA_PATH = f"src/dev_tools/default_data/default_personalities.json"


def print_model(model: BaseModel):
    logging.debug(json.dumps(model.model_dump(exclude=["model_config"]), indent=4))


def create_new_db():
    logging.debug("erasing db + creating new defualt db")
    db_connection.erase_db()

    logging.debug("creating default bots")
    with open(DEFAULT_DATA_PATH) as file:
        bot_data = json.load(file)

    for btd in bot_data:
        personality_dna_data = _load_personality_dna(btd["personality_dna_path"])
        mood_dna = [
            BotMoodAxiom(axiom=mood, response=response)
            for mood, response in btd["mood_dna"].items()
        ]
        bot = BotAgent.create(
            name=btd["name"],
            voice_id=btd["voice_id"],
            personality_dna=BotPersonalityDna(**personality_dna_data),
            mood_dna=mood_dna,
            capabilities=btd["capabilities"],
        )

        logging.debug(bot.model_fields)
        assert bot.unique_name == btd["name"]

        logging.debug(f"testing save bot {bot.unique_name}")
        bot.save()

        bot = BotAgent.find_agent(bot.unique_name)


def _load_personality_dna(personality_dna_path: str) -> dict[str, str]:
    personality_dna = {}
    for file_name in os.listdir(personality_dna_path):
        logging.debug(f"loading personality dna from {file_name}")

        if file_name.endswith(".md"):
            # Assuming no variables are needed for the Markdown files
            content = prompt_loader(
                file_path=os.path.join(personality_dna_path, file_name)
            )
            # Use the file name without the extension as the key
            personality_dna[os.path.splitext(file_name)[0]] = content

    return personality_dna
