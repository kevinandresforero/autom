import time
import src.search_file
from src.load_configuration import LoadConfiguration
from src.general_actions import GeneralActions

class Build(LoadConfiguration):
    """
    The Build class is the base (or parent) class for a bot.
    It initializes configuration from a txt file and sets default values for variables
    that will be used by a specific bot implementation.

    This class acts as a central aggregator for all bot modules and configuration.
    It is intended to be used by the main process (UI) to manage and coordinate
    the bot's routines, timers, and configuration.

    This class contains timer variables to manage timing in routines
    executed by different threads.

    Possible states:
        - ALIVE: The bot is alive and ready.
        - DEAD: The bot is dead.
        - IN_COMBAT: The bot is fighting an enemy.
        - RECOVERING: The bot is recovering HP/MP or waiting.
        - PATROLLING: The bot is searching for enemies.
        - BUFFING: The bot is applying buffs.
    """
    # Possible states for the bot
    STATE_ALIVE = "alive"
    STATE_DEAD = "dead"

    STATE_IN_COMBAT = "in_combat"
    STATE_RECOVERING = "recovering"
    STATE_PATROLLING = "patrolling"
    STATE_BUFFING = "buffing"

    def __init__(self):
        # --- LOAD CONFIGURATION FROM FILE ---
        super().__init__()
        # --- TIMERS FOR THREAD ROUTINES ---
        self.last_use_hab1 = 0
        self.last_use_hab2 = 0
        self.last_use_hab3 = 0
        self.last_use_debuff = 0
        self.last_buff = 0
        self.last_low_hp = 0
        self.last_use_skill = 0
        self.last_hp = 0
        self.last_damage_received = time.time()

        # --- GENERAL ACTIONS ---
        self.do = GeneralActions()

        # --- BOT STATE ---
        self.state = Build.STATE_DEAD
        self.action = Build.STATE_BUFFING

    def summary(self):
        """
        Prints a summary of all instance variables of the Build class, including configuration, timers, state,
        and also the variables inherited from the parent class (LoadConfiguration).
        """
        print("Build instance summary:\n")
        # Print all instance variables (including inherited)
        for attr in dir(self):
            # Exclude methods and built-ins
            if not attr.startswith("__") and not callable(getattr(self, attr)):
                print(f"{attr}: {getattr(self, attr)}")

#b = Build()
#print(b.get_hp_value())