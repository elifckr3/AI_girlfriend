import sys
import pytest
import logging
from prompt_toolkit.input import create_pipe_input

sys.path.append("src")


def test_user_conf():
    from personality_conf import PersonalityConfigPrompt
    from dev_tools.db_management import create_new_db

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.debug("testing user conf prompt w/ default bot")

    create_new_db()

    with create_pipe_input() as input:
        pipe = [
            "",
            "allan watts",
        ]
        for p in pipe:
            input.send_text(p)
            input.send_text("\n")

        agent = PersonalityConfigPrompt(
            test_input=input,
        ).run()

    assert agent.unique_name == "allan watts"

    # with create_pipe_input() as inp:
    #     pipe = [
    #         "\x1b[B\n",
    #         "Max",
    #         "F1 racing driver",
    #         "aggressive and short worded",
    #         "winning and racing cars",
    #         "to help me get my winning mentality",
    #         "hail an uber",
    #         " \n",
    #         "make a joke",
    #     ]
    #     for p in pipe:
    #         inp.send_text(p)
    #         inp.send_text("\n")

    #     agent = UserStartConfig(
    #         test_input=inp,
    #     ).run()
