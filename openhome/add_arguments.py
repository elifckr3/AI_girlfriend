import argparse

def get_initial_personality():
    """    
    This function add arguments to any module in which it will be called.
    you can add personality while runing main.py file using -p or --personality command.
    for example => python3 main.py -p Ava

    Returns:
        personality (string): Return a string name of personality selected by user, by default it is Alan_watts.
    """
    # Create the parser and write description for user if he/she types `python3 main.py --help`
    parser = argparse.ArgumentParser(description="Personality arguments help.",
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # add argument to allow user to select the assistant personality.
    # Personality name can be added through -p personality_name or --personality personality_name while running the main.py
    parser.add_argument("-p", "--personality", default='1', help="Personality name")

    # get the argument passed by user
    args = parser.parse_args()

    # convert to dictioanry
    config = vars(args)

    # get personality key from config dictionary
    personality = config['personality']

    return personality
