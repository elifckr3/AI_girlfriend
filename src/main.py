import os
import time
import pytz
from datetime import datetime, timedelta
import typer
import threading
import logging
from src.personality_conf import PersonalityConfigPrompt
from src.system_conf import SystemConfigPrompt, ENV_DATA
from src.agent.base import BotAgent, BotMemoryUpdateType
from src.agent.message import RoleTypes
from src.agent.capability import Capability
from src.utils import timeit, pretty_console
from src.utils.db import RedisConnect
from src.dev_tools.db_management import create_new_db
from typing import Annotated
from queue import Queue

app = typer.Typer()

db = RedisConnect()

# TODO test race conditions > in Rust concurrency will be garuanteed


class ThreadManager:
    def __init__(self, agent: BotAgent, debug: bool = False, cold_start: bool = False):
        launch_time = datetime.now(pytz.UTC)
        self.agent = agent
        self.debug = debug
        self.cold_start = cold_start
        self.listen_queue = Queue()
        self.response_queue = Queue()
        self.interupt_queue = Queue()
        self.last_day_summation_time = launch_time
        self.last_week_summation_time = launch_time

    def listen_forvever(self):
        while True:
            if self.debug:
                time.sleep(2)

            # if self.interupt_queue.get() is False or self.interupt_queue.empty():
            msgs = self.agent.listen()

            self.listen_queue.put(msgs)

            # saves after thread hands over to manage_context
            self.agent.save_message(msgs, role=RoleTypes.USER)

    def manage_context_forever(self):
        while True:
            if not self.listen_queue.empty():
                msgs = self.listen_queue.get()

                context = self.agent.manage_context(msgs)

                if isinstance(context, Capability):
                    # call a capability
                    context.call()

                    # NOTE save to system
                    message = f"Calling capability: {context.name}"

                    self.save_message(message, role=RoleTypes.SYSTEM)

                elif isinstance(context, str):
                    # context is now the prompt itself
                    self.response_queue.put(context)

                    # save message after handover to response
                    self.agent.save_message(context, role=RoleTypes.ASSISTANT)

                    # NOTE any subsequent processing / gpt calls / db saves here

                else:
                    logging.error(f"Invalid context: {context}")

            elif self.cold_start is True:
                self.cold_start = False
                context = self.agent.manage_context(msgs=[], cold_start=True)
                self.response_queue.put(context)

    def respond_forever(self):
        while True:
            if not self.response_queue.empty():
                # TODO interupt listening ?
                self.interupt_queue.put(True)

                response = self.response_queue.get()

                if self.debug is True:
                    with timeit.Timer() as _:
                        self.agent.speak(response=response)

                else:
                    self.agent.speak(response=response)

                self.interupt_queue.put(False)

    def background_update_forever(self):
        while True:
            time_now = datetime.now(pytz.UTC)

            if self.debug is True:
                day_delta = timedelta(seconds=10)
                week_delta = timedelta(seconds=20)

            else:
                day_delta = timedelta(days=1)
                week_delta = timedelta(weeks=1)

            if time_now - self.last_day_summation_time > day_delta:
                self.last_day_summation_time = time_now
                self.agent.memory_update(update_type=BotMemoryUpdateType.DAILY)

            if time_now - self.last_week_summation_time > week_delta:
                self.last_week_summation_time = time_now
                self.agent.memory_update(update_type=BotMemoryUpdateType.WEEKLY)

    def start(self):
        threading.Thread(target=self.listen_forvever).start()
        threading.Thread(target=self.manage_context_forever).start()
        threading.Thread(target=self.respond_forever).start()
        threading.Thread(target=self.background_update_forever).start()

    def single_thread(self):
        
        if self.cold_start:
            logging.debug("Flushing old msges")
            self.agent.memory.full_message_history = []
            
        elif self.agent.memory.full_message_history == []:
            self.cold_start = True

        context = self.agent.manage_context(msgs='', cold_start=self.cold_start)

        self.agent.speak(response=context)

        time.sleep(0.1)

        while True:
            msgs = self.agent.listen()

            logging.info(f"msgs: {msgs}")

            self.agent.save_message(msgs, role=RoleTypes.USER)

            context = self.agent.manage_context(msgs)

            self.agent.save_message(context, role=RoleTypes.ASSISTANT)

            if isinstance(context, Capability):
                logging.info(f"Calling capability: {context.name}")
                context.call()

            elif isinstance(context, str):
                self.agent.speak(response=context)


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", help="Debug mode with DEBUG level logging"),
    default_bot: bool = typer.Option(False, "--default", help="Use default bot (Allan Watts)"),
    update_conf: bool = typer.Option(False, "--config", help="Toggle prompts to update system configuration"),
    speach_off: bool = typer.Option(False, "--speech-off", help="Toggle speach off for debugging"),
    cold_start: bool = typer.Option(False, "--cold-start", help="Toggle speach off for debugging"),
    # local_db: bool = False,
    # mock_api: bool = False,
):
    pretty_console.pretty_logger(debug=debug)

    conf_settr = SystemConfigPrompt()

    if update_conf is True:
        # create config models and run strat
        sys_conf = conf_settr.run()

    else:
        sys_conf = conf_settr.default_config()

    logging.info(f"Initializing system with conf: {sys_conf}")

    for key, value in sys_conf.items():
        logging.debug(f"setting env var: {key} to {value}")

        os.environ[key] = value

    env_data = db.read(key=ENV_DATA)

    if env_data is None:
        # Creating Default DB because env variables were not found in redis
        create_new_db()
        env_data = db.read(key=ENV_DATA)

        # Toggle cold start if db resets
        cold_start = True

    for key, value in env_data.items():
        logging.debug(f"setting API keys: {key} to xxx ")
        os.environ[key] = value

    if speach_off is True:
        os.environ["SPEECH_OFF"] = "True"

    if default_bot is True:
        agent = BotAgent.find_agent("Allan Watts")

    else:
        agent = PersonalityConfigPrompt().run()

    logging.info(f"Initializing agent bot: {agent.unique_name}")

    ThreadManager(agent=agent, debug=debug, cold_start=cold_start).single_thread()


# if __name__ == "__main__":
#     app()
