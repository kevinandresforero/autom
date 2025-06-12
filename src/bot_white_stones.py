from src.character import Character
from src.potions import PotionThread
from src.search_and_attack import SearchAndAttackThread
from src.buff_thread import BuffThread
import threading
import time

class BotWhiteStones(Character):
    def __init__(self):
        super().__init__()
        self.name = "White stone collector"
        self.description = "A robot that collects white stones."
        self.version = "1.0.0"
        self.author = "Kebuun"
        self.threads = []
        self.should_buff = False  # Control externo para buffear

    def start(self):
        # Estado inicial del bot
        self.action = self.STATE_PATROLLING

        # Hilo para actualizar HP con pociones
        hilo_pociones = PotionThread(self, interval=0.5)
        hilo_pociones.start()
        self.threads.append(hilo_pociones)

        # Hilo para buscar y atacar enemigos
        hilo_search_attack = SearchAndAttackThread(self)
        hilo_search_attack.start()
        self.threads.append(hilo_search_attack)

        # Hilo para buffear
        hilo_buff = BuffThread(self)
        hilo_buff.start()
        self.threads.append(hilo_buff)

        # Hilo principal del bot (puedes agregar más lógica aquí)
        hilo_bot = threading.Thread(target=self.run, daemon=True)
        hilo_bot.start()
        self.threads.append(hilo_bot)

    def run(self):
        last_damage_time = time.time()
        while self.state != self.STATE_DEAD:
            self.set_hp()
            self.set_mp()
            print(f"[Bot] HP: {self.hp}, MP: {self.mp}")

            # Detecta daño recibido
            if hasattr(self, "last_hp"):
                if self.hp < self.last_hp:
                    last_damage_time = time.time()
                    if self.action != self.STATE_IN_COMBAT:
                        print("[Bot] Switching to IN_COMBAT state (damage received)")
                    self.action = self.STATE_IN_COMBAT
            self.last_hp = self.hp

            # Si lleva más de 15 segundos sin daño, pasa a estado PATROLLING
            if time.time() - last_damage_time > 15:
                if self.action != self.STATE_PATROLLING:
                    print("[Bot] Switching to PATROLLING state (no damage in 15s)")
                self.action = self.STATE_PATROLLING
                # Solo gira a la izquierda si NO está buffeando
                if self.action != self.STATE_BUFFING:
                    print("[Bot] Patrolling: holding 'a' to turn left")
                    self.do.hold_key("a")

            # El sleep debe ir en las rutinas/hilos secundarios


