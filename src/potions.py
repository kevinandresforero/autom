import threading
import time

class PotionThread:
    """
    Clase que crea un hilo para actualizar constantemente el valor de la vida del personaje.

    Uso:
        from character import Character
        from potions import PotionThread

        personaje = Character()
        hilo_pociones = PotionThread(personaje, interval=0.5)
        hilo_pociones.start()

        # ... tu lógica principal ...

        hilo_pociones.stop()
    """

    def __init__(self, character, interval=0.1):
        """
        :param character: Objeto de tipo Character
        :param interval: Intervalo de actualización en segundos
        """
        self.character = character
        self.interval = interval
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def run(self):
        while not self._stop_event.is_set():
            self.character.set_hp()
            if self.character.isAlive():
                print("[X] Character is dead.")
            else:
                porcentaje = 0
                if self.character.max_hp > 0:
                    porcentaje = (self.character.hp / self.character.max_hp) * 100
                print(f"[✓] Character is alive. HP: {self.character.hp}/{self.character.max_hp} ({porcentaje:.2f}%)")
                if porcentaje <= 45:
                    print(f"[!] HP is below 45%: {porcentaje:.2f}%. Trying to use potion key: {self.character.KEY_POTION_HP}")
                    self.character.do.press_key(self.character.KEY_POTION_HP)
                else:
                    print(f"[i] HP is above 45%. No potion used.")
            time.sleep(0.005)