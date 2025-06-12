import threading
import time

class BuffThread:
    """
    Hilo que aplica buffs al personaje usando KEY_BUFF y los números del 1 al NUM_BUFFS.
    Mientras está pulsando la tecla KEY_BUFF, el personaje está en estado BUFFING.
    Cuando termina, vuelve al estado anterior.
    """

    def __init__(self, character):
        """
        :param character: Objeto de tipo Character (debe tener KEY_BUFF, NUM_BUFFS, STATE_BUFFING, action)
        """
        self.character = character
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.previous_action = None

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def run(self):
        # Al iniciar el hilo, buffearse inmediatamente
        while not self._stop_event.is_set():
            # Guarda el estado anterior y cambia a BUFFING
            self.previous_action = self.character.action
            self.character.action = self.character.STATE_BUFFING
            print("[~] Buffing...")

            # Pulsa la combinación KEY_BUFF + número para cada buff
            for i in range(1, int(self.character.NUM_BUFFS) + 1):
                key_num = str(i)
                print(f"[~] Buffing with {self.character.KEY_BUFF} + {key_num}")
                self.character.do.press_combo(self.character.KEY_BUFF, key_num)
                # Durante USE_BUFF segundos, el personaje está ocupado buffeando
                time.sleep(float(self.character.USE_BUFF))

            print("[✓] Buffing finished.")

            # Vuelve al estado anterior
            self.character.action = self.previous_action

            # Espera hasta el próximo ciclo de buff (el temporizador inicia después de buffear)
            time.sleep(float(self.character.BUFF_INTERVAL) * 60)