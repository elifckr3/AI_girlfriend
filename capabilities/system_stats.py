import time
from src.agent.capability import Capability
import os
import logging
from datetime import datetime


class TimerCapability(Capability):
    @classmethod
    def register_capability(cls):
        return cls(unique_name="system_stats", hotwords=["get system stats","system stats"])

    def call(self):

        # Get system stats
        num_cpu_cores = os.cpu_count()
        os_uname = os.uname()
        os_name = os_uname.nodename
        machine = os_uname.machine

        # Get the current date and time
        current_date = datetime.now()

        # Format the date as a string if needed
        formatted_date = current_date.strftime("%B %d, %Y %H:%M:%S")

        message = "OS is %s"%os_name
        message += " and machine is %s"%machine
        message += " and Number of CPU Cores are %s"%num_cpu_cores
        message += ", Current Date :%s"%formatted_date

        logging.debug(message)
        return message

