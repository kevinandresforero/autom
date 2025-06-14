import os

def file():
    """
    Returns the absolute path to the config_bot.txt file located in the same directory as this script.

    Returns:
        str: Absolute path to config_bot.txt
    """
    return os.path.join(os.path.dirname(__file__), "config_bot.txt")