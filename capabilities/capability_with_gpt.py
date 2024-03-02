from src.agent.capability import Capability
import os
import logging
from datetime import datetime
from src.agent.io_interface import text_to_text



class SystemstatsCapability(Capability):
    @classmethod
    def register_capability(cls):
        return cls(unique_name="system_stats_gpt", hotwords=["rate my machine","describe my machine"])

    def call(self,agent):
        initial_message = "Getting system stats, please wait."
        agent.speak(response=initial_message)

        # Get system stats
        num_cpu_cores = os.cpu_count()
        os_uname = os.uname()
        os_name = os_uname.nodename
        machine = os_uname.machine

        # Get the current date and time
        current_date = datetime.now()

        # Format the date as a string if needed
        formatted_date = current_date.strftime("%B %d, %Y %H:%M:%S")

        message = "OS is %s\n"%os_name
        message += "Machine is %s\n"%machine
        message += "Number of CPU Cores are %s\n"%num_cpu_cores
        message += "Current Date :%s\n"%formatted_date

        logging.info("System Stats: %s"%message)

        prompt = "Can describe the following machine: \n\n" + message
        
        logging.info("Sending Prompt to Agent: %s"%prompt)
        
        response = text_to_text(prompt)

        logging.debug(response)

        return response

