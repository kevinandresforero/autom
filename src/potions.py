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
        Inicializa el hilo de pociones.

        :param character: Objeto de tipo Character
        :param interval: Intervalo de actualización en segundos
        """
        self.character = character
        self.interval = interval
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        """
        Inicia el hilo de pociones.
        """
        self.thread.start()

    def stop(self):
        """
        Detiene el hilo de pociones.
        """
        self._stop_event.set()
        self.thread.join()

    def run(self):
        """
        Lógica principal del hilo: actualiza el valor de HP y usa poción si el porcentaje de vida es menor o igual a 45%.
        """
        while not self._stop_event.is_set():
            self.character.set_hp()
            if self.character.isAlive():
                pass
            else:
                porcentaje = 0
                if self.character.max_hp > 0:
                    porcentaje = (self.character.hp / self.character.max_hp) * 100
                if porcentaje <= 45:
                    self.character.do.press_key(self.character.KEY_POTION_HP)
            time.sleep(0.005)