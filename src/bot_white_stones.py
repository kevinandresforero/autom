from src.character import Character
from src.potions import PotionThread
import threading

class BotWhiteStones(Character):
    def __init__(self):
        super().__init__()
        self.name = "White stone collector"
        self.description = "A robot that collects white stones."
        self.version = "1.0.0"
        self.author = "Kebuun"
        self.threads = []

    def start(self):
        # Hilo para actualizar HP con pociones
        hilo_pociones = PotionThread(self, interval=0.5)
        hilo_pociones.start()
        self.threads.append(hilo_pociones)

        # Hilo principal del bot (puedes agregar más lógica aquí)
        hilo_bot = threading.Thread(target=self.run, daemon=True)
        hilo_bot.start()
        self.threads.append(hilo_bot)

    def run(self):
        while self.state != self.STATE_DEAD:
            self.set_hp()
            self.set_mp()
            print(f"[Bot] HP: {self.hp}, MP: {self.mp}")
            # El sleep debe ir aquí, dentro de la rutina/hilo
            # time.sleep(1)


