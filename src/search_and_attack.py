import threading
import time

class SearchAndAttackThread:
    """
    Hilo que busca enemigos usando KEY_SEARCH y luego ataca con KEY_AUTOATTACK
    y usa habilidades según configuración y cooldowns.
    """


    def __init__(self, character):
        """
        :param character: Objeto de tipo Character (debe tener KEY_SEARCH, KEY_AUTOATTACK, AUTOATTACK_DURATION,
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
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def run(self):
        last_buff_time = 0
        while not self._stop_event.is_set():
            now = time.time()
            # Actualiza el tiempo si está buffeando
            if self.character.action == self.character.STATE_BUFFING:
                last_buff_time = now

            # Solo busca y ataca si NO está buffeando ni recuperando
            if self.character.action not in [self.character.STATE_BUFFING, self.character.STATE_RECOVERING]:
                self.character.do.press_key(self.character.KEY_SEARCH)
                print(f"[~] Searching for enemies with key: {self.character.KEY_SEARCH}")
                self.character.do.press_key(self.character.KEY_AUTOATTACK)
                print(f"[~] Attacking with key: {self.character.KEY_AUTOATTACK}")

                # Solo usa habilidades si han pasado más de 10 segundos desde el último buff
                if now - last_buff_time > 10:
                    # Skill 1
                    if getattr(self.character, "USE_SKILL1", False):
                        cooldown1 = float(getattr(self.character, "COOLDOWN_SKILL1", 0))
                        if now - self.last_skill1 >= cooldown1:
                            print(f"[~] Using Skill 1 ({self.character.KEY_SKILL1})")
                            self.character.do.press_key(self.character.KEY_SKILL1)
                            self.last_skill1 = now
                            time.sleep(float(getattr(self.character, "USE_SKILL1", 0)))  # Espera animación

                    # Skill 2
                    if getattr(self.character, "USE_SKILL2", False):
                        cooldown2 = float(getattr(self.character, "COOLDOWN_SKILL2", 0))
                        if now - self.last_skill2 >= cooldown2:
                            print(f"[~] Using Skill 2 ({self.character.KEY_SKILL2})")
                            self.character.do.press_key(self.character.KEY_SKILL2)
                            self.last_skill2 = now
                            time.sleep(float(getattr(self.character, "USE_SKILL2", 0)))  # Espera animación

                    # Skill 3
                    if getattr(self.character, "USE_SKILL3", False):
                        cooldown3 = float(getattr(self.character, "COOLDOWN_SKILL3", 0))
                        if now - self.last_skill3 >= cooldown3:
                            print(f"[~] Using Skill 3 ({self.character.KEY_SKILL3})")
                            self.character.do.press_key(self.character.KEY_SKILL3)
                            self.last_skill3 = now
                            time.sleep(float(getattr(self.character, "USE_SKILL3", 0)))  # Espera animación

            # Actualiza last_hp para la siguiente iteración
            if hasattr(self.character, "hp"):
                self.last_hp = self.character.hp
            time.sleep(self.character.AUTOATTACK_DURATION)