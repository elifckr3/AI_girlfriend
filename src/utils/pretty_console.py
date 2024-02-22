import logging
from colorlog import ColoredFormatter

formatter = ColoredFormatter(
    "%(log_color)s%(levelname)s-%(asctime)s-%(name)s: %(white)s%(message)s",
    datefmt="%m/%d-%H:%M:%S",
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)


# def disable_venv_loggers():
#     # Iterate through all loggers
#     for name, logger in logging.Logger.manager.loggerDict.items():
#         # Check if the logger name contains './venv'
#         if isinstance(logger, logging.PlaceHolder) and "./venv" in name:
#             # Check if the logger is not already disabled
#             if logger.level != logging.CRITICAL:
#                 logger.setLevel(logging.CRITICAL)


def pretty_logger(debug: bool = False):
    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    logging.getLogger().addHandler(console)

    # disable_venv_loggers()
