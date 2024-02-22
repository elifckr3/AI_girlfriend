import logging
import openai

API_KEY = "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"
TEMPERATURE = 0.9
FREQUENCY_PENALTY = 0.2
PRESENCE_PENALTY = 0


def chatgpt_ttt(messages_input: list[str]):
    # chat_response = None
    # logging.error(f"FOOO: {messages_input}")
    # logging.error(f"TYPE: {type(messages_input)}")
    msg = [{"role": "system", "content": messages_input}]
    try:
        openai.api_key = API_KEY
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=TEMPERATURE,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
            messages=msg,
        )

        chat_response = completion["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error("Error %s" % e)

    logging.debug(f"chat_response: {chat_response}")

    return chat_response
