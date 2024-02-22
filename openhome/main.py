import os
from abc import ABC, abstractmethod
import numpy as np
import yaml
import atexit
import threading
from enum import Enum
from time import time
from colorama import Fore, Style
from pydantic import BaseModel, model_serializer
from LLM import chatgpt
from voice_input_output.text_to_voice import text_to_speech
from voice_input_output.voice_to_text import record_and_transcribe
from add_arguments import get_initial_personality
from process_user_message import process_message
from personalities_manager import load_personality
from history_files.history_manager import store_history
from history_files.user_memory_manager import update_recent_history
from history_files.history_summarizer import (
    summarize_history,
    get_summarized_conversation,
    exit_handler,
)
from conversation_manager import manage_conversation
from utility import load_json
from personalities.mood_evolver import mood_evolver, get_customized_prompt
from voice_input_output.loading_sounds import play_loading_sound
import app_globals as globals


os.environ["OPEN_AI_KEY"] = "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"
os.environ["EL_AI_KEY"] = "15dec7728128dcdc7254dcfa7c1ab947"


class Characters(Enum):
    WATTS = "Alan_watts"
    AVA = "Ava"


class RoleTypes(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class UserAgent(BaseModel):
    name: str

    likes: list[str]

    dislikes: list[str]

    personality: list[str] = ["default me to be a kind human that like star wars"]


class MoodTypes(Enum):
    ANGER = "anger"
    FEAR = "fear"
    JOY = "joy"
    SADNESS = "sadness"
    SURPRISE = "surprise"


class MoodDynamics(BaseModel):
    mood: MoodTypes

    intensity: int


class Message(BaseModel):
    role: RoleTypes

    agent_resp: str

    @model_serializer
    def serialize_to_gpt3(self):
        return {
            "user_prompt": self.user_prompt,
            "agent_resp": self.agent_resp,
        }

        # # user or assistant
        # {"role": role, "content": message}
        # messages_input = conversion.atcopy()
        # prompt = [{"role": "system", "content": chatbot}]
        # messages_input.insert(0, prompt[0])

        # completion = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     temperature=temperature,
        #     frequency_penalty=frequency_penalty,
        #     presence_penalty=presence_penalty,
        #     messages=messages_input)


mood_evolution = """
this a mood evolution part to your

you have a spectrum of emotions that you can feel at any given time.

you can feel anger, fear, joy, sadness, and surprise.

you can feel these emotions at different intensities between the levels of 0 to 10.

{mood} is at level {intensity}.
"""
# [0.2122, 0.2122, 0.1802, 0.0022, -0.2122]
base_personality: str = "i am a debate bot"

base_mood: str = "my base mood is neutral"

# NOTE HACK goal < 1 hour build capabilities

base_mood_dynamics = [
    "if the user is aggressive, be more aggressive.",
    "if the user is sad, be more empathetic.",
    "if the user is happy, be more joyful.",
    "if the user is surprised, be more surprised.",
    "if the user is fearful, be more fearful.",
]

mood_fusion = [  # 3rd party # XXX Agent - Optional
    "i want you to take by base mood dynamics",
    "fuse it with what you've learned about our previous conversations",
    "then evolve it based on the agent/player current mood.",
]

recet_memory = {
    "last_10_messages": [],
    "last_sentence_summation": "",
    "agent_current_mood": {
        "anger": 0,
        "fear": 0,
        "joy": 0,
        "sadness": 0,
        "surprise": 0,
    },
    "player_current_mood": {
        "anger": 0,
        "fear": 0,
        "joy": 0,
        "sadness": 0,
        "surprise": 0,
    },
}

lt_memory = {}

# NOTE what is memory structure


class GptPrompter(BaseModel, ABC):
    @abstractmethod
    def create_current_context(self):
        pass


# NOTE Agents
# assembly transcriber
# command run > "prompt + list of commands" (1) -> Result<Cmd, None>
# history | persona | ... | ... fetcher > "" (1) -> Result<Fetcher, None>
# mood evolution "prompt" (2) -> "mood story"
# transmitter "prompt" (3) -> "user response"

# NOTE     
# fuzzy matching
# user API keys
    


# history summarizer (D)
# user persona summarizer (D)

# NOTE UserProfile Memory Management
# Age
# Career
# Education
# Awards
# Personality Traits
# Hobbies
# Health
# Family and Relationship Details
# Investments
# Interests
# Lifestyle
# Goals and Ambitions
# Working Style
# Concerns
# Areas for Improvement

# Education: Stanford (Dropout)
# Awards: Forbes 30 under 30, Thiel Fellow
# Personality: ENTJ, Enneagram Type 8. Traits include assertiveness, high energy, charisma, and composure under stress.
# Hobbies: Drone flying, gold collecting, beach, geopolitics, news

# XXX summaries and full list[str] (1 per day updates on user)

# NOTE XXX
# Load Personality: At startup, the system loads the active personality, which influences response styles and preferences throughout the user interaction.
# Wake Word Detection: The application continuously listens for a specific wake word, activating the command processing phase upon detection.
# Speech to Text: Once activated, it captures the user's spoken command and converts it into text for analysis.
# Command Processing: This step involves parsing the transcribed text to understand the user's intent and deciding which action to take,
# - capability matching (execution time is dynamic)
# - such as fetching user history or switching personalities.
# User History Management: For commands requiring context, the system retrieves relevant user history, ensuring responses are informed by past interactions.
# Generate Personality Response: With the command understood and context in hand, the system crafts a reply using a language model, tailored by the current personality and user's history.
# Text to Speech: Finally, the crafted response is converted back into speech, mimicking the voice characteristics of the selected personality, and played back to the user.

# NOTE
# about
# intro, language, tone, words chosen, actions, style ..
# example question responses


class AgentMemory(GptPrompter):
    full_message_history: list[Message]

    last_sentence_summation: str

    last_month_summation: str

    hobby_related_summation: list[int]

    work_related_summation: list[int]
    ...

    def create_current_context(self):
        # NOTE do the correct fusion of all the memory
        # NOTE what what is memory retrieval mechanism
        return self.last_sentence_summation


class GptAgent(BaseModel):
    name: str

    memory: list[Message] = []

    mood: dict[str, int] = {}

    def __init__(self, name: str):
        for mood in MoodTypes:
            self.mood[mood] = np.random.randint(0, 10)

    def create_current_context(self):
        # final_prompt = message + personality + mood.random_shift()
        return self.memory[-1]


def initialize_system(file_data):
    personality_id = get_initial_personality()
    personality = load_personality(personality_id=personality_id)
    mood_json = load_json(path="openhome/personalities/mood.json")
    with open("openhome/personalities/mood_evolving_instruction.txt", "r") as file:
        mood_prompt_template = file.read()
    with open("openhome/personalities/emotion_detection_prompt.txt", "r") as file:
        emotion_detection_prompt = file.read()
    for emotion in mood_json:
        mood_json[emotion] = 0
    globals.mood_json = mood_json
    return personality, [], mood_prompt_template, emotion_detection_prompt


def capture_user_input(file_data):
    return record_and_transcribe(file_data["openai_api_key"])


def process_user_interaction(user_message, personality, conversation, file_data):
    print(Fore.RED + f"{user_message}" + Style.RESET_ALL, end="\n")
    conversation = manage_conversation(user_message, conversation, role="user")
    is_valid_message, action_feedback = process_message(user_message, personality)
    if action_feedback and action_feedback.get("feedback"):
        handle_action_feedback(action_feedback, conversation, personality, file_data)
    return conversation, personality


def handle_action_feedback(action_feedback, conversation, personality, file_data):
    feedback_message = action_feedback["feedback"].get("feedback", "")
    text_to_speech(
        feedback_message, personality["voice_id"], file_data["elevenlabs_api_key"]
    )
    manage_conversation(feedback_message, conversation, role="assistant")


def generate_response(
    conversation,
    personality,
    file_data,
    mood_prompt_template,
    emotion_detection_prompt,
    user_message,
):
    summarized_conversation = get_summarized_conversation()
    response = chatgpt(
        file_data["openai_api_key"],
        summarized_conversation,
        get_customized_prompt(personality["personality"]),
    )
    store_history(
        user_message, response
    )  # Adjusted to include both user and assistant messages
    return response


def handle_response(response, conversation, personality, file_data):
    print(
        Fore.YELLOW + f"{personality['name']}: {response}" + Style.RESET_ALL, end="\n"
    )
    text_to_speech(response, personality["voice_id"], file_data["elevenlabs_api_key"])
    return manage_conversation(response, conversation, role="assistant")


def main_loop(
    personality, conversation, file_data, mood_prompt_template, emotion_detection_prompt
):
    while True:
        if not conversation:  # Check if conversation is empty to play the greeting
            greeting = personality["greetings"]
            print(f"Greeting: {greeting}")
            text_to_speech(
                greeting, personality["voice_id"], file_data["elevenlabs_api_key"]
            )
            conversation = manage_conversation(
                "", conversation, role="user"
            )  # Use an empty string as placeholder

        user_message = capture_user_input(file_data)
        conversation, personality = process_user_interaction(
            user_message, personality, conversation, file_data
        )
        response = generate_response(
            conversation,
            personality,
            file_data,
            mood_prompt_template,
            emotion_detection_prompt,
            user_message,
        )
        conversation = handle_response(response, conversation, personality, file_data)


def main():
    file_data = load_configuration()
    (
        personality,
        conversation,
        mood_prompt_template,
        emotion_detection_prompt,
    ) = initialize_system(file_data)
    atexit.register(exit_handler, file_data["openai_api_key"])
    main_loop(
        personality,
        conversation,
        file_data,
        mood_prompt_template,
        emotion_detection_prompt,
    )


if __name__ == "__main__":
    main()
