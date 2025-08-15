from src.character import Character
from src.search_and_attack import SearchAndAttackThread
from src.buff_thread import BuffThread
import threading
import time

class BotWhiteStonesNoLp(Character):
    def __init__(self):
        super().__init__()
        self.name = "White stone collector (No LP/MP)"
        self.description = "Un bot que farmea white stones, se buffea y ataca enemigos, sin leer HP/MP ni acceder a la RAM."
        self.version = "1.0.0"
        self.author = "Kebuun"
        self.threads = []

    def start(self):
        print("[Bot] Iniciando rutina de farmeo (No LP/MP)...")
        self.action = self.STATE_PATROLLING

        hilo_search_attack = SearchAndAttackThread(self)
        hilo_search_attack.start()
        self.threads.append(hilo_search_attack)
        print("[Bot] Hilo de búsqueda y ataque iniciado.")

        hilo_buff = BuffThread(self)
        hilo_buff.start()
        self.threads.append(hilo_buff)
        print("[Bot] Hilo de buff iniciado.")

        hilo_bot = threading.Thread(target=self.run, daemon=True)
        hilo_bot.start()
        self.threads.append(hilo_bot)
        print("[Bot] Hilo principal iniciado.")

    def run(self):
        last_buff_time = 0
        last_skill1 = last_skill2 = last_skill3 = 0

        while self.state != self.STATE_DEAD:
            now = time.time()
            max_skill_sleep = 0

            # Buff: cada 5 minutos
            if now - last_buff_time > 5 * 60:
                prev_action = self.action
                self.action = self.STATE_BUFFING
                print("[Bot] Buffeando...")

                for i in range(1, int(self.NUM_BUFFS) + 1):
                    key_fn = f"f{i}"
                    print(f"[Bot] Lanzando buff {key_fn}")
                    self.do.press_key(key_fn)
                    time.sleep(float(self.USE_BUFF))
                self.action = prev_action
                last_buff_time = time.time()
                print("[Bot] Buff finalizado.")
                continue  # No atacar ni buscar mientras buffea

            # Siempre en estado patrulla si no está buffeando
            self.action = self.STATE_PATROLLING
            if self.action != self.STATE_BUFFING:
                print("[Bot] Patrullando...")
                self.do.hold_key("a")

            # Buscar y atacar enemigos (si no está buffeando ni recuperando)
            if self.action not in [self.STATE_BUFFING, self.STATE_RECOVERING]:
                print("[Bot] Buscando enemigos...")
                self.buscar_enemigos()
                print("[Bot] Atacando enemigo.")
                self.do.press_key(self.KEY_AUTOATTACK)

                # Skills solo si han pasado 10s desde el último buff
                if now - last_buff_time > 10:
                    # Skill 1
                    if getattr(self, "USE_SKILL1", False):
                        cooldown1 = float(getattr(self, "COOLDOWN_SKILL1", 0))
                        if now - last_skill1 >= cooldown1:
                            print("[Bot] Usando Skill 1")
                            self.do.press_key(self.KEY_SKILL1)
                            last_skill1 = now
                            skill1_sleep = float(getattr(self, "USE_SKILL1", 0))
                            max_skill_sleep = max(max_skill_sleep, skill1_sleep)
                    # Skill 2
                    if getattr(self, "USE_SKILL2", False):
                        cooldown2 = float(getattr(self, "COOLDOWN_SKILL2", 0))
                        if now - last_skill2 >= cooldown2:
                            print("[Bot] Usando Skill 2")
                            self.do.press_key(self.KEY_SKILL2)
                            last_skill2 = now
                            skill2_sleep = float(getattr(self, "USE_SKILL2", 0))
                            max_skill_sleep = max(max_skill_sleep, skill2_sleep)
                    # Skill 3
                    if getattr(self, "USE_SKILL3", False):
                        cooldown3 = float(getattr(self, "COOLDOWN_SKILL3", 0))
                        if now - last_skill3 >= cooldown3:
                            print("[Bot] Usando Skill 3")
                            self.do.press_key(self.KEY_SKILL3)
                            last_skill3 = now
                            skill3_sleep = float(getattr(self, "USE_SKILL3", 0))
                            max_skill_sleep = max(max_skill_sleep, skill3_sleep)

            # Espera el mayor tiempo de animación de skill, o el tiempo de autoataque si no usó skills
            if max_skill_sleep > 0:
                print(f"[Bot] Esperando {max_skill_sleep} segundos por animación de skill.")
                time.sleep(max_skill_sleep)
            else:
                print(f"[Bot] Esperando {self.AUTOATTACK_DURATION} segundos por autoataque.")
                time.sleep(self.AUTOATTACK_DURATION)