import threading
import time

class SearchAndAttackThread:
    """
    Hilo que busca enemigos usando KEY_SEARCH y luego ataca con KEY_AUTOATTACK
    cada AUTOATTACK_DURATION segundos.
    """


    def __init__(self, character):
        """
        :param character: Objeto de tipo Character (debe tener KEY_SEARCH, KEY_AUTOATTACK y AUTOATTACK_DURATION)
        """
        self.character = character
        self.character.action = self.character.STATE_IN_COMBAT
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.last_hp = getattr(character, "hp", 0)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def run(self):
        while not self._stop_event.is_set():
            # Si recibe daño, puede contraatacar con 'f' (KEY_AUTOATTACK) incluso si está buffeando
            if hasattr(self.character, "hp"):
                if self.character.hp < getattr(self, "last_hp", self.character.hp):
                    print("[!] Damage received! Counter-attacking with key:", self.character.KEY_AUTOATTACK)
                    self.character.do.press_key(self.character.KEY_AUTOATTACK)
            # Solo busca y ataca si NO está buffeando ni recuperando
            if self.character.action not in [self.character.STATE_BUFFING, self.character.STATE_RECOVERING]:
                self.character.do.press_key(self.character.KEY_SEARCH)
                print(f"[~] Searching for enemies with key: {self.character.KEY_SEARCH}")
                self.character.do.press_key(self.character.KEY_AUTOATTACK)
                print(f"[~] Attacking with key: {self.character.KEY_AUTOATTACK}")
            # Actualiza last_hp para la siguiente iteración
            if hasattr(self.character, "hp"):
                self.last_hp = self.character.hp
            time.sleep(self.character.AUTOATTACK_DURATION)