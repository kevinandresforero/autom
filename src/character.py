from src.build import Build

class Character(Build):
    """
    The Character class is a specialized bot that extends the Build class.
    It is designed to manage character-specific actions and states in the game.
    """

    def __init__(self):
        super().__init__()
        self.name = "Character"
        self.description = "A bot that manages character actions."
        self.max_hp, self.max_mp = 0, 0
        self.hp = 0
        self.mp = 0
        self.set_hp()
        self.set_mp()
        self.isAlive()

    def summary(self):
        """
        Prints a summary of all instance variables of the Character class, including configuration, timers, and state.
        """

    def isAlive(self):
        """
        Checks if the character is alive and updates the state accordingly.
        """
        if self.state == Build.STATE_DEAD:
            print("[X] Character is dead.")
            return True
        else:
            print("[✓] Character is alive.")
            self.state = Build.STATE_ALIVE
            return False
        
    def set_hp(self):
        self.hp = self.get_hp_value()
        self.actualizar_maximos(self.hp, self.mp)
        if self.hp <= 0:
            self.state = Build.STATE_DEAD
        else:
            self.state = Build.STATE_ALIVE

    def set_mp(self):
        self.mp = self.get_mp_value()
        self.actualizar_maximos(self.hp, self.mp)

    def actualizar_maximos(self, hp_actual, mp_actual):
        if hp_actual > self.max_hp:
            self.max_hp = hp_actual
            print(f"[+] Nuevo HP máximo registrado: {self.max_hp}")
        if mp_actual > self.max_mp:
            self.max_mp = mp_actual
            print(f"[+] Nuevo MP máximo registrado: {self.max_mp}")