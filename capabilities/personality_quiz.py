import os
import logging
import openai
from typing import ClassVar, List
from src.agent.capability import Capability
from src.utils import timeit
from src.system_conf import (
    get_conf,
    OPENAI_TTT_MODEL,
    OPENAI_TTT_TEMPERATURE,
    OPENAI_TTT_FREQUENCY_PENALTY,
    OPENAI_TTT_PRESENCE_PENALTY,
    OPENAI_STT_MODEL,
    OPENAI_KEY,
)

# Assuming timeit.PROFILE is a decorator you have defined elsewhere in your utilities
# If not, you can replace @timeit.PROFILE with a simple function pass-through decorator

class OpenAiClient:
    def __init__(self):
        api_key = os.environ.get(OPENAI_KEY)
        if api_key is None:
            raise ValueError("OPENAI_KEY is not set")
        openai.api_key = api_key

    @timeit.PROFILE
    def ttt(self, messages_input: list[str]) -> str:
        msg = [{"role": "system", "content": "\n".join(messages_input)}]
        logging.debug(f"Sending msg to GPT: {messages_input}")

        try:
            model = get_conf(OPENAI_TTT_MODEL)
            temperature = get_conf(OPENAI_TTT_TEMPERATURE)
            frequency_penalty = get_conf(OPENAI_TTT_FREQUENCY_PENALTY)
            presence_penalty = get_conf(OPENAI_TTT_PRESENCE_PENALTY)

            completion = openai.ChatCompletion.create(
                model=model,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=msg,
            )

            chat_response = completion.choices[0].message.content
            logging.debug(f"chat_response: {chat_response}")
        except Exception as e:
            logging.error(f"Error {e}")
            chat_response = "Error generating response"

        return chat_response

class PersonalityQuizCapability(Capability):
    user_history: List[str] = []
    questions: ClassVar[List[str]] = [
        "Do you prefer to meet new people or stick with a few close friends?",
        "Do you prefer facts and details or big ideas and possibilities?",
        "Do you make decisions with your head or your heart?",
        "Halfway done. Do you plan your work in advance or decide as you go?",
        "Do you unwind by being alone or hanging out with others?",
        "Do you learn better with hands-on experience or through theories and concepts?",
        "Almost done. In relationships, is being logical or empathetic more important to you?",
        "Last question. Give me context. What would you say your biggest strengths are?"
    ]

    @classmethod
    def register_capability(cls):
        return cls(unique_name="personality_quiz", hotwords=["start personality quiz", "personality quiz"])

    def ask_question(self, agent, question: str) -> str:
        # Assuming agent.speak and agent.listen are methods you have defined to interact with the user
        agent.speak(question)
        response = agent.listen()
        logging.info(f"Question: {question} - Answer: {response}")
        return response

    def summarize_responses(self) -> str:
        summary = "Here are your responses to the personality quiz:"
        for i, response in enumerate(self.user_history, start=1):
            summary += f"\nQ{i}: {response}"
        return summary

    def generate_mbti_prediction(self, openai_client: OpenAiClient) -> str:
        prompt_lines = ["Based on the following responses to a personality quiz, what is the likely Myers-Briggs type? Each answer will correspond to one of the MBTI dichotomies: Extraversion (E) vs. Introversion (I), Sensing (S) vs. Intuition (N), Thinking (T) vs. Feeling (F), and Judging (J) vs. Perceiving (P). By assessing the tendencies shown in the responses. Respond with the 4 letters, and very briefly tell me what that personality type means in 2 short sentences."]
        for question, answer in zip(self.questions, self.user_history):
            prompt_lines.append(f"Q: {question}")
            prompt_lines.append(f"A: {answer}")

        mbti_prediction = openai_client.ttt(messages_input=prompt_lines)
        return mbti_prediction

    def call(self, agent) -> str:
        agent.speak("Starting the Personality Quiz. I will ask you 8 quick questions about your personality. You can give me more context and I can understand the spectrum.")
        
        for question in self.questions:
            response = self.ask_question(agent, question)
            self.user_history.append(response)

        openai_client = OpenAiClient()
        mbti_prediction = self.generate_mbti_prediction(openai_client)
        
        summary = self.summarize_responses()
        summary += f"\nHere is your result: {mbti_prediction}"
        agent.speak(summary)

        self.user_history.clear()
