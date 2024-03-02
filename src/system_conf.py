import typer
import os
import logging
from enum import Enum
from src.utils.prompt import Prompt, Question, QTypes
from src.utils.db import RedisConnect


db_connection = RedisConnect()

# NOTE ALL THESE ARE CONSTANTS TO DIMINISHING STRING ERROR MISTAKES

# > CLIENTS

STT_CLIENT = "STT_CLIENT"
TTT_CLIENT = "TTT_CLIENT"
TTS_CLIENT = "TTS_CLIENT"
DEEPGRAM_KEY = "deepgram_key"
# > CLIENT PARAMS

# >> LOCAL (STT)
LOCAL_RECORDING_PAUSE_THRESHOLD = "pause_threshold"
LOCAL_RECORDING_NON_SPEAKING_DURATION = "non_speaking_duration"
LOCAL_RECORDING_PHRASE_THRESHOLD = "phrase_threshold"
LOCAL_RECORDING_ENERGY_ADJUSTMENT_DURATION = "energy_adjustment_duration"
LOCAL_RECORDING_ENERGY_THRESHOLD = "energy_threshold"
LOCAL_RECORDING_DYNAMIC_ENERGY_THRESHOLD = "dynamic_energy_threshold"
LOCAL_RECORDING_DYNAMIC_ENERGY_ADJUSTMENT_DAMPING = "dynamic_energy_adjustment_damping"

# >> OPENAI (TTT)
OPENAI_TTT_MODEL = "openai_ttt_model"
OPENAI_TTT_TEMPERATURE = "temperature"
OPENAI_TTT_FREQUENCY_PENALTY = "frequency_penalty"
OPENAI_TTT_PRESENCE_PENALTY = "presence_penalty"
# OPENAI_TTT_MAX_TOKENS = "max_tokens"

# NOTE handle user keys starts here API_KEY = "api_key"
# atm no prompt as default env keys are used from Redis

# >> OPENAI (STT)
OPENAI_STT_MODEL = "openai_stt_model"

# >> ELEVEN_LABS (TTS)
EL_TTS_VOICE_STABILITY = "voice_stability"
EL_TTS_VOICE_SIMILARITY_BOOST = "voice_similarity_boost"


# KEYS
ENV_DATA = "env_data"
OPENAI_KEY = "openai_key"
ELEVEN_LABS_KEY = "eleven_labs_key"
ASSEMBLYAI_KEY = "assembly_key"


# OTHER
SPEECH_OFF = "speech_off"
WHISPER_MIC = "whisper_mic"
MIC_OFF = "mic_off"


def get_conf(var_name: str):
    """
    Get the value of an environment variable with automatic type conversion.

    Args:
        var_name (str): The name of the environment variable.

    Returns:
        The value of the environment variable after automatic type conversion
    """
    value = os.environ.get(var_name)

    if value is not None:
        # Try converting to int, float, and bool in that order
        try:
            return int(value)

        except ValueError:
            try:
                return float(value)

            except ValueError:
                if value.lower() == "true":
                    return True

                elif value.lower() == "false":
                    return False

    if value is None:
        raise ValueError(f"Error: {var_name} not found in environment")

    return value


class SystemConfigPrompt(Prompt):
    def default_config(self):
        from src.clients.openai import OpenAITTTModels, OpenAISTTModels

        """
        Set the default configuration for the system
        """
        from src.agent.io_interface import STT_CLIENTS, TTS_CLIENTS, TTT_CLIENTS

        # clients
        os.environ[STT_CLIENT] = STT_CLIENTS.INTERNAL.value
        os.environ[TTT_CLIENT] = TTT_CLIENTS.OPENAI.value
        os.environ[TTS_CLIENT] = TTS_CLIENTS.ELEVENLABS.value

        # local recording
        os.environ[LOCAL_RECORDING_PAUSE_THRESHOLD] = "0.8"
        os.environ[LOCAL_RECORDING_NON_SPEAKING_DURATION] = "0.5"
        os.environ[LOCAL_RECORDING_PHRASE_THRESHOLD] = "0.3"
        os.environ[LOCAL_RECORDING_ENERGY_ADJUSTMENT_DURATION] = "1"
        os.environ[LOCAL_RECORDING_ENERGY_THRESHOLD] = "300"
        os.environ[LOCAL_RECORDING_DYNAMIC_ENERGY_THRESHOLD] = "True"
        os.environ[LOCAL_RECORDING_DYNAMIC_ENERGY_ADJUSTMENT_DAMPING] = "0.15"

        # openai TTT
        os.environ[OPENAI_TTT_MODEL] = OpenAITTTModels.GPT_3_5_TURBO.value
        os.environ[OPENAI_TTT_TEMPERATURE] = "0.9"
        os.environ[OPENAI_TTT_FREQUENCY_PENALTY] = "0.2"
        os.environ[OPENAI_TTT_PRESENCE_PENALTY] = "0"

        # openai STT
        os.environ[OPENAI_STT_MODEL] = OpenAISTTModels.WHISPER_1.value

        # elevenlabs TTS
        os.environ[EL_TTS_VOICE_STABILITY] = "0.5"
        os.environ[EL_TTS_VOICE_SIMILARITY_BOOST] = "0.5"

        return os.environ

    def run(self):
        """
        Prompt clients chosen and their respective parameters
        """
        from src.agent.io_interface import STT_CLIENTS, TTS_CLIENTS, TTT_CLIENTS

        typer.secho("\n Configure OpenHome System settings: \n", fg=typer.colors.GREEN)

        clients_chosen = self.prompt(
            [
                Question(
                    name=STT_CLIENT,
                    qtype=QTypes.SELECT,
                    message="Speech-to-Text (STT) client",
                    enum_struct=STT_CLIENTS,
                    default=STT_CLIENTS.INTERNAL,
                ),
                Question(
                    name=TTT_CLIENT,
                    qtype=QTypes.SELECT,
                    message="Text-to-Text (TTT) client",
                    enum_struct=TTT_CLIENTS,
                    default=TTT_CLIENTS.OPENAI,
                ),
                Question(
                    name=TTS_CLIENT,
                    qtype=QTypes.SELECT,
                    message="Text-to-Speech (TTS) client",
                    enum_struct=TTS_CLIENTS,
                    default=TTS_CLIENTS.ELEVENLABS,
                ),
            ],
        )

        for client in clients_chosen:
            os.environ[client] = clients_chosen[client].value

        self._set_stt_params(clients_chosen[STT_CLIENT])

        self._set_ttt_params(clients_chosen[TTT_CLIENT])

        self._set_tts_params(clients_chosen[TTS_CLIENT])

        typer.secho("\n System config setup successfully \n", fg=typer.colors.GREEN)

        return os.environ

    def _set_stt_params(self, client):
        from src.agent.io_interface import STT_CLIENTS
        from src.clients.openai import OpenAISTTModels

        typer.secho(
            f"\n Configuring {STT_CLIENTS.INTERNAL.value} client \n",
            fg=typer.colors.GREEN,
        )
        match client:
            case STT_CLIENTS.INTERNAL:
                local_recording_params = self.prompt(
                    [
                        Question(
                            name=LOCAL_RECORDING_PAUSE_THRESHOLD,
                            qtype=QTypes.FLOAT,
                            message="Pause threshold",
                            default=0.8,
                        ),
                        Question(
                            name=LOCAL_RECORDING_NON_SPEAKING_DURATION,
                            qtype=QTypes.FLOAT,
                            message="Non-speaking duration",
                            default=0.5,
                        ),
                        Question(
                            name=LOCAL_RECORDING_PHRASE_THRESHOLD,
                            qtype=QTypes.FLOAT,
                            message="Phrase threshold",
                            default=0.3,
                        ),
                        Question(
                            name=LOCAL_RECORDING_ENERGY_ADJUSTMENT_DURATION,
                            qtype=QTypes.INT,
                            message="Energy adjustment duration",
                            default=1,
                        ),
                        Question(
                            name=LOCAL_RECORDING_ENERGY_THRESHOLD,
                            qtype=QTypes.INT,
                            message="Energy threshold",
                            default=300,
                        ),
                        Question(
                            name=LOCAL_RECORDING_DYNAMIC_ENERGY_THRESHOLD,
                            qtype=QTypes.CONFIRM,
                            message="Dynamic energy threshold",
                            default=True,
                        ),
                        Question(
                            name=LOCAL_RECORDING_DYNAMIC_ENERGY_ADJUSTMENT_DAMPING,
                            qtype=QTypes.FLOAT,
                            message="Dynamic energy adjustment damping",
                            default=0.15,
                        ),
                    ],
                )
                self._set_env(local_recording_params)

                gpt_model = self.prompt(
                    [
                        Question(
                            name=OPENAI_STT_MODEL,
                            qtype=QTypes.SELECT,
                            message="Model",
                            enum_struct=OpenAISTTModels,
                            default=OpenAISTTModels.WHISPER_1,
                        ),
                    ],
                )
                self._set_env(gpt_model)

            case STT_CLIENTS.ASSEMBLY:
                logging.debug("Assembly conf")

            case _:
                raise ValueError(f"Invalid client type: {client}")

    def _set_ttt_params(self, client):
        from src.agent.io_interface import TTT_CLIENTS
        from src.clients.openai import OpenAITTTModels

        typer.secho(
            f"\n Configuring {TTT_CLIENTS.OPENAI.value} client \n",
            fg=typer.colors.GREEN,
        )
        match client:
            case TTT_CLIENTS.INTERNAL:
                logging.debug("Internal conf")
            case TTT_CLIENTS.OPENAI:
                openai_ttt_params = self.prompt(
                    [
                        Question(
                            name=OPENAI_TTT_MODEL,
                            qtype=QTypes.SELECT,
                            message="Model",
                            enum_struct=OpenAITTTModels,
                            default=OpenAITTTModels.GPT_3_5_TURBO,
                        ),
                        Question(
                            name=OPENAI_TTT_TEMPERATURE,
                            qtype=QTypes.FLOAT,
                            message="Temperature",
                            default=0.9,
                        ),
                        Question(
                            name=OPENAI_TTT_FREQUENCY_PENALTY,
                            qtype=QTypes.FLOAT,
                            message="Frequency penalty",
                            default=0.2,
                        ),
                        Question(
                            name=OPENAI_TTT_PRESENCE_PENALTY,
                            qtype=QTypes.FLOAT,
                            message="Presence penalty",
                            default=0,
                        ),
                    ],
                )
                self._set_env(openai_ttt_params)
            case _:
                raise ValueError(f"Invalid client type: {client}")

    def _set_tts_params(self, client):
        from src.agent.io_interface import TTS_CLIENTS

        typer.secho(
            f"\n Configuring {TTS_CLIENTS.ELEVENLABS.value} client \n",
            fg=typer.colors.GREEN,
        )
        match client:
            case TTS_CLIENTS.INTERNAL:
                logging.debug("Internal conf")
            case TTS_CLIENTS.ELEVENLABS:
                el_tts_params = self.prompt(
                    [
                        Question(
                            name=EL_TTS_VOICE_STABILITY,
                            qtype=QTypes.FLOAT,
                            message="Voice stability",
                            default=0.5,
                        ),
                        Question(
                            name=EL_TTS_VOICE_SIMILARITY_BOOST,
                            qtype=QTypes.FLOAT,
                            message="Voice similarity boost",
                            default=0.5,
                        ),
                    ],
                )
                self._set_env(el_tts_params)

            case _:
                raise ValueError(f"Invalid client type: {client}")

    def _set_env(self, promt_response: dict):
        for var_name, value in promt_response.items():
            if isinstance(value, Enum):
                os.environ[var_name] = value.value

            else:
                os.environ[var_name] = str(value)

        # db_connection.set_var(var_name, value)
