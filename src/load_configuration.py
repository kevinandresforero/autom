from pymem import Pymem
from pymem.process import module_from_name
import src.search_file as search_file

# --- LOAD CONFIGURATION FROM TXT ---
class LoadConfiguration:
    """
    Class to load configuration from a text file and scan memory for HP/MP values.
    """

    def __init__(self):
        """
        Initializes the LoadConfiguration class, loads the configuration,
        and prepares for memory scanning.
        """
        config_path = search_file.file()
        config = self.load_configuration(config_path)

        # --- CONFIGURATION FROM FILE ---
        self.PROCESS_NAME = config["PROCESS_NAME"]
        self.OFFSET_HP = int(config["OFFSET_HP"])
        self.OFFSET_MP = int(config["OFFSET_MP"])

        # Scan memory for HP and MP values using pymem (separated)
        self.HP_VALUE = self.scan_memory(self.PROCESS_NAME, self.OFFSET_HP)
        self.MP_VALUE = self.scan_memory(self.PROCESS_NAME, self.OFFSET_MP)

        self.COOLDOWN_SKILL1 = config["COOLDOWN_SKILL1"]
        self.COOLDOWN_SKILL2 = config["COOLDOWN_SKILL2"]
        self.COOLDOWN_SKILL3 = config["COOLDOWN_SKILL3"]
        self.COOLDOWN_DEBUFF = config["COOLDOWN_DEBUFF"]
        self.BUFF_INTERVAL = config["BUFF_INTERVAL"]
        self.NUM_BUFFS = int(config.get("NUM_BUFFS", 1))

        self.USE_SKILL1 = config["USE_SKILL1"]
        self.USE_SKILL2 = config["USE_SKILL2"]
        self.USE_SKILL3 = config["USE_SKILL3"]
        self.USE_DEBUFF = config["USE_DEBUFF"]
        self.AUTOATTACK_DURATION = config["AUTOATTACK_DURATION"]
        self.USE_BUFF = config.get("USE_BUFF", 2)

        self.KEY_SKILL1 = config.get("KEY_SKILL1", "1")
        self.KEY_SKILL2 = config.get("KEY_SKILL2", "2")
        self.KEY_SKILL3 = config.get("KEY_SKILL3", "3")
        self.KEY_BUFF = config.get("KEY_BUFF", "alt")
        self.KEY_POTION_HP = config.get("KEY_POTION_HP", "9")
        self.KEY_POTION_MP = config.get("KEY_POTION_MP", "0")
        self.KEY_AUTOATTACK = config.get("KEY_AUTOATTACK", "f")
        self.KEY_PICKUP = config.get("KEY_PICKUP", "v")
        self.KEY_PAUSE_COMBAT = config.get("KEY_PAUSE_COMBAT", "x")
        self.KEY_SEARCH = config.get("KEY_SEARCH", "tab")

    def scan_memory(self, process_name, address):
        """
        Reads a value from the given memory address of the specified process.

        Args:
            process_name (str): Name of the process.
            address (int): Memory address (in decimal).

        Returns:
            int: Value read from memory, or None if failed.
        """
        try:
            pm = Pymem(process_name)
            value = pm.read_int(address)
            return value
        except Exception as e:
            return None

    def load_configuration(self, file_path):
        """
        Loads configuration from a text file.

        Args:
            file_path (str): Path to the configuration file.

        Returns:
            dict: Dictionary with configuration keys and values.
        """
        config = {}
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # For OFFSET_HP and OFFSET_MP, always interpret as hexadecimal
                    if key in ("OFFSET_HP", "OFFSET_MP"):
                        try:
                            config[key] = int(value, 16)
                        except ValueError:
                            config[key] = value
                    else:
                        try:
                            config[key] = int(value)
                        except ValueError:
                            try:
                                config[key] = float(value)
                            except ValueError:
                                config[key] = value
        return config
    
    def get_hp_value(self):
        """
        Returns the current HP value from memory.

        Returns:
            int: Current HP value, or None if failed.
        """
        self.HP_VALUE = self.scan_memory(self.PROCESS_NAME, self.OFFSET_HP)
        self.MP_VALUE = self.scan_memory(self.PROCESS_NAME, self.OFFSET_MP)
        return self.HP_VALUE
    
    def get_mp_value(self): 
        """
        Returns the current MP value from memory.

        Returns:
            int: Current MP value, or None if failed.
        """
        self.MP_VALUE = self.scan_memory(self.PROCESS_NAME, self.OFFSET_MP)
        return self.MP_VALUE
    
#lc = LoadConfiguration()
#print(lc.get_hp_value())