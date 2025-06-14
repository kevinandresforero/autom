import threading
import time

class SearchAndAttackThread:
    """
    Hilo que busca enemigos usando KEY_SEARCH y luego ataca con KEY_AUTOATTACK
    y usa habilidades según configuración y cooldowns.
    """

    def __init__(self, character):
        """
        Inicializa el hilo de búsqueda y ataque.

        Args:
            character: Objeto de tipo Character (debe tener KEY_SEARCH, KEY_AUTOATTACK, AUTOATTACK_DURATION,
                      USE_SKILL1, USE_SKILL2, USE_SKILL3, KEY_SKILL1, KEY_SKILL2, KEY_SKILL3, etc.)
        """
        self.character = character
        self.character.action = self.character.STATE_IN_COMBAT
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.last_hp = getattr(character, "hp", 0)
        self.last_skill1 = 0
        self.last_skill2 = 0
        self.last_skill3 = 0

    def start(self):
        """
        Inicia el hilo de búsqueda y ataque.
        """
        self.thread.start()

    def stop(self):
        """
        Detiene el hilo de búsqueda y ataque.
        """
        self._stop_event.set()
        self.thread.join()

    def run(self):
        """
        Lógica principal del hilo: busca enemigos, ataca y usa habilidades según los cooldowns y el estado del personaje.
        Solo usa habilidades si han pasado al menos 10 segundos desde el último buff.
        """
        last_buff_time = 0
        while not self._stop_event.is_set():
            now = time.time()
            max_skill_sleep = 0  # Para saber cuánto esperar tras usar skills

            if self.character.action == self.character.STATE_BUFFING:
                last_buff_time = now

            if self.character.action not in [self.character.STATE_BUFFING, self.character.STATE_RECOVERING]:
                self.character.do.press_key(self.character.KEY_SEARCH)
                self.character.do.press_key(self.character.KEY_AUTOATTACK)

                if now - last_buff_time > 10:
                    # Skill 1
                    if getattr(self.character, "USE_SKILL1", False):
                        cooldown1 = float(getattr(self.character, "COOLDOWN_SKILL1", 0))
                        if now - self.last_skill1 >= cooldown1:
                            self.character.do.press_key(self.character.KEY_SKILL1)
                            self.last_skill1 = now
                            skill1_sleep = float(getattr(self.character, "USE_SKILL1", 0))
                            max_skill_sleep = max(max_skill_sleep, skill1_sleep)

                    # Skill 2
                    if getattr(self.character, "USE_SKILL2", False):
                        cooldown2 = float(getattr(self.character, "COOLDOWN_SKILL2", 0))
                        if now - self.last_skill2 >= cooldown2:
                            self.character.do.press_key(self.character.KEY_SKILL2)
                            self.last_skill2 = now
                            skill2_sleep = float(getattr(self.character, "USE_SKILL2", 0))
                            max_skill_sleep = max(max_skill_sleep, skill2_sleep)

                    # Skill 3
                    if getattr(self.character, "USE_SKILL3", False):
                        cooldown3 = float(getattr(self.character, "COOLDOWN_SKILL3", 0))
                        if now - self.last_skill3 >= cooldown3:
                            self.character.do.press_key(self.character.KEY_SKILL3)
                            self.last_skill3 = now
                            skill3_sleep = float(getattr(self.character, "USE_SKILL3", 0))
                            max_skill_sleep = max(max_skill_sleep, skill3_sleep)

            if hasattr(self.character, "hp"):
                self.last_hp = self.character.hp

            # Espera el mayor tiempo de animación de skill, o el tiempo de autoataque si no usó skills
            if max_skill_sleep > 0:
                time.sleep(max_skill_sleep)
            else:
                time.sleep(self.character.AUTOATTACK_DURATION)