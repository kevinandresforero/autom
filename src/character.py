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
        pass

    def isAlive(self):
        """
        Checks if the character is alive and updates the state accordingly.

        Returns:
            bool: True if the character is dead, False if alive.
        """
        if self.state == Build.STATE_DEAD:
            return True
        else:
            self.state = Build.STATE_ALIVE
            return False

    def set_hp(self):
        """
        Updates the character's HP value from memory and updates the state.
        Also updates the maximum HP and MP values seen so far.
        """
        self.hp = self.get_hp_value()
        self.actualizar_maximos(self.hp, self.mp)
        if self.hp <= 0:
            self.state = Build.STATE_DEAD
        else:
            self.state = Build.STATE_ALIVE

    def set_mp(self):
        """
        Updates the character's MP value from memory.
        Also updates the maximum HP and MP values seen so far.
        """
        self.mp = self.get_mp_value()
        self.actualizar_maximos(self.hp, self.mp)

    def actualizar_maximos(self, hp_actual, mp_actual):
        """
        Updates the maximum HP and MP values if the current values are higher.

        Args:
            hp_actual (int): Current HP value.
            mp_actual (int): Current MP value.
        """
        if hp_actual > self.max_hp:
            self.max_hp = hp_actual
        if mp_actual > self.max_mp:
            self.max_mp = mp_actual

    def buscar_enemigos(self):
        """
        Busca enemigos solo si el personaje NO está en estado de buffeo.
        """
        if self.action != self.STATE_BUFFING:
            self.do.hold_key('a')
            self.do.press_key(self.KEY_SEARCH)
            self.do.press_key('w')

