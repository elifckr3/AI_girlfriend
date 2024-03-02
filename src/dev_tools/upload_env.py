import logging
from src.system_conf import OPENAI_KEY, ELEVEN_LABS_KEY, ASSEMBLYAI_KEY, ENV_DATA, DEEPGRAM_KEY
from src.utils.db import RedisConnect


db = RedisConnect()


def upload_env():
    logging.basicConfig(level=logging.DEBUG)

    logging.debug("uploading env vars")

    enviroment = {
        OPENAI_KEY: "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",
        ELEVEN_LABS_KEY: "15dec7728128dcdc7254dcfa7c1ab947",
        ASSEMBLYAI_KEY: "e3127d96f3274285b250f528b7818bb9",
        DEEPGRAM_KEY: "0479795b99af48e055385c27ecbdc89c9775949e",
    }

    db.write(key=ENV_DATA, data=enviroment)

    logging.debug(f"env vars uploaded - keys: {enviroment.keys()}")
