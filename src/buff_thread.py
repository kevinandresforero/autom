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
        """
        Inicia el hilo de buffeo.
        """
        self.thread.start()

    def stop(self):
        """
        Detiene el hilo de buffeo y espera a que termine.
        """
        self._stop_event.set()
        self.thread.join()

    def run(self):
        """
        Lógica principal del hilo: aplica los buffs pulsando las teclas F1 a Fn, 
        cambiando el estado a BUFFING mientras lo hace, y espera el intervalo configurado antes de repetir.
        """
        # Al iniciar el hilo, buffearse inmediatamente
        while not self._stop_event.is_set():
            # Guarda el estado anterior y cambia a BUFFING
            self.previous_action = self.character.action

            # Pulsa solo las teclas F1 a Fn para cada buff
            for i in range(1, int(self.character.NUM_BUFFS) + 1):
                key_fn = f"f{i}"
                self.character.action = self.character.STATE_BUFFING
                self.character.do.press_key(key_fn)
                time.sleep(float(self.character.USE_BUFF))

            # Vuelve al estado anterior
            self.character.action = self.previous_action

            # Espera hasta el próximo ciclo de buff (el temporizador inicia después de buffear)
            time.sleep(self.character.BUFF_INTERVAL * 60 - 1)  # 5 minutos para pruebas