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
        """
        Inicia todos los hilos necesarios para el funcionamiento del bot:
        - Hilo de pociones (cura automática)
        - Hilo de búsqueda y ataque de enemigos
        - Hilo de buffeo
        - Hilo principal del bot (gestión de estados y lógica principal)
        """
        self.action = self.STATE_PATROLLING

        hilo_pociones = PotionThread(self, interval=0.5)
        hilo_pociones.start()
        self.threads.append(hilo_pociones)

        hilo_search_attack = SearchAndAttackThread(self)
        hilo_search_attack.start()
        self.threads.append(hilo_search_attack)

        hilo_buff = BuffThread(self)
        hilo_buff.start()
        self.threads.append(hilo_buff)

        hilo_bot = threading.Thread(target=self.run, daemon=True)
        hilo_bot.start()
        self.threads.append(hilo_bot)

    def run(self):
        """
        Lógica principal del bot:
        - Actualiza HP y MP.
        - Detecta daño recibido y cambia a estado de combate.
        - Realiza buffeo cada 5 minutos.
        - Cambia a estado de patrulla si no recibe daño por 15 segundos.
        - Busca enemigos y ataca si no está buffeando ni recuperando.
        - Usa habilidades si han pasado al menos 10 segundos desde el último buff y respeta cooldowns.
        - Espera el mayor tiempo de animación de skill o el tiempo de autoataque si no usó skills.
        """
        last_damage_time = time.time()
        last_buff_time = 0
        last_skill1 = last_skill2 = last_skill3 = 0

        while self.state != self.STATE_DEAD:
            self.set_hp()
            self.set_mp()

            # Detecta daño recibido
            if hasattr(self, "last_hp"):
                if self.hp < self.last_hp:
                    last_damage_time = time.time()
                    self.action = self.STATE_IN_COMBAT
            self.last_hp = self.hp

            now = time.time()
            max_skill_sleep = 0

            # Buff: cada 5 minutos (pruebas)
            if now - last_buff_time > 5 * 60:
                prev_action = self.action
                self.action = self.STATE_BUFFING

                for i in range(1, int(self.NUM_BUFFS) + 1):
                    key_fn = f"f{i}"
                    self.do.press_key(key_fn)
                    time.sleep(float(self.USE_BUFF))
                self.action = prev_action
                last_buff_time = time.time()
                continue  # No atacar ni buscar mientras buffea

            # Si lleva más de 15 segundos sin daño, pasa a estado PATROLLING
            if now - last_damage_time > 15:
                self.action = self.STATE_PATROLLING
                if self.action != self.STATE_BUFFING:
                    self.do.hold_key("a")

            # Search and attack (solo si no está buffeando ni recuperando)
            if self.action not in [self.STATE_BUFFING, self.STATE_RECOVERING]:
                self.buscar_enemigos()
                self.do.press_key(self.KEY_AUTOATTACK)

                # Skills solo si han pasado 10s desde el último buff
                if now - last_buff_time > 10:
                    # Skill 1
                    if getattr(self, "USE_SKILL1", False):
                        cooldown1 = float(getattr(self, "COOLDOWN_SKILL1", 0))
                        if now - last_skill1 >= cooldown1:
                            self.do.press_key(self.KEY_SKILL1)
                            last_skill1 = now
                            skill1_sleep = float(getattr(self, "USE_SKILL1", 0))
                            max_skill_sleep = max(max_skill_sleep, skill1_sleep)
                    # Skill 2
                    if getattr(self, "USE_SKILL2", False):
                        cooldown2 = float(getattr(self, "COOLDOWN_SKILL2", 0))
                        if now - last_skill2 >= cooldown2:
                            self.do.press_key(self.KEY_SKILL2)
                            last_skill2 = now
                            skill2_sleep = float(getattr(self, "USE_SKILL2", 0))
                            max_skill_sleep = max(max_skill_sleep, skill2_sleep)
                    # Skill 3
                    if getattr(self, "USE_SKILL3", False):
                        cooldown3 = float(getattr(self, "COOLDOWN_SKILL3", 0))
                        if now - last_skill3 >= cooldown3:
                            self.do.press_key(self.KEY_SKILL3)
                            last_skill3 = now
                            skill3_sleep = float(getattr(self, "USE_SKILL3", 0))
                            max_skill_sleep = max(max_skill_sleep, skill3_sleep)

            # Espera el mayor tiempo de animación de skill, o el tiempo de autoataque si no usó skills
            if max_skill_sleep > 0:
                time.sleep(max_skill_sleep)
            else:
                time.sleep(self.AUTOATTACK_DURATION)


