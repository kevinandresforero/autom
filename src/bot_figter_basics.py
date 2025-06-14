from pymem import Pymem
from pymem.process import module_from_name
import pyautogui
import time
import threading
import search_file

# --- LOAD CONFIGURATION FROM TXT ---
def cargar_configuracion(archivo):
    """
    Carga la configuración desde un archivo de texto.

    Args:
        archivo (str): Ruta al archivo de configuración.

    Returns:
        dict: Diccionario con las claves y valores de configuración.
    """
    config = {}
    with open(archivo, 'r') as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if '=' in linea:
                clave, valor = linea.split('=', 1)
                clave = clave.strip()
                valor = valor.strip()
                # Solo convierte a int si es un número decimal o hexadecimal válido
                if valor.startswith(('0x', '0X')):
                    try:
                        config[clave] = int(valor, 16)
                    except ValueError:
                        config[clave] = valor
                else:
                    try:
                        config[clave] = int(valor)
                    except ValueError:
                        try:
                            config[clave] = float(valor)
                        except ValueError:
                            config[clave] = valor
    return config

config_path = search_file.file()
config = cargar_configuracion(config_path)

# --- CONFIGURACIÓN DESDE ARCHIVO ---
PROCESS_NAME = config.get("PROCESS_NAME")
OFFSET_HP = config.get("OFFSET_HP")
OFFSET_MP = config.get("OFFSET_MP")

COOLDOWN_SKILL1 = config.get("COOLDOWN_SKILL1")
COOLDOWN_SKILL2 = config.get("COOLDOWN_SKILL2")
COOLDOWN_SKILL3 = config.get("COOLDOWN_SKILL3")
COOLDOWN_DEBUFF = config.get("COOLDOWN_DEBUFF")
BUFF_INTERVAL = config.get("BUFF_INTERVAL")
NUM_BUFFS = int(config.get("NUM_BUFFS", 1))

USE_SKILL1 = config.get("USE_SKILL1")
USE_SKILL2 = config.get("USE_SKILL2")
USE_SKILL3 = config.get("USE_SKILL3")
USE_DEBUFF = config.get("USE_DEBUFF")
AUTOATTACK_DURATION = config.get("AUTOATTACK_DURATION")
USE_BUFF = config.get("USE_BUFF", 2)

KEY_SKILL1 = config.get("KEY_SKILL1", "1")
KEY_SKILL2 = config.get("KEY_SKILL2", "2")
KEY_SKILL3 = config.get("KEY_SKILL3", "3")
KEY_DEBUFF = config.get("KEY_DEBUFF", "f1")
KEY_BUFF = config.get("KEY_BUFF", "alt")
KEY_POTION_HP = config.get("KEY_POTION_HP", "9")
KEY_POTION_MP = config.get("KEY_POTION_MP", "0")
KEY_AUTOATTACK = config.get("KEY_AUTOATTACK", "f")
KEY_PICKUP = config.get("KEY_PICKUP", "v")
KEY_PAUSE_COMBAT = config.get("KEY_PAUSE_COMBAT", "x")
KEY_SEARCH = config.get("KEY_SEARCH", "tab")

# --- TIMERS ---
last_use_skill1 = 0
last_use_skill2 = 0
last_use_skill3 = 0
last_use_debuff = 0
last_buff = 0
last_low_hp = 0
last_use_skill = 0
last_hp = 0
last_damage_received = time.time()

# --- MEMORY CONNECTION ---
def esperar_proceso(nombre_proceso):
    """
    Espera hasta que el proceso del juego esté disponible y retorna una instancia de Pymem.

    Args:
        nombre_proceso (str): Nombre del proceso a esperar.

    Returns:
        Pymem: Instancia conectada al proceso.
    """
    while True:
        try:
            pm = Pymem(nombre_proceso)
            return pm
        except Exception:
            print("[!] Waiting for the game to start...")
            time.sleep(1)

pm = esperar_proceso(PROCESS_NAME)
base_module = module_from_name(pm.process_handle, PROCESS_NAME)
if base_module is None:
    raise Exception("[X] Game module not found.")
base_addr = base_module.lpBaseOfDll

# --- GENERAL FUNCTIONS ---
def press_key(key):
    """
    Presiona una tecla usando pyautogui.

    Args:
        key (str): Tecla a presionar.
    """
    if key != 'v':
        time.sleep(0.2)
    pyautogui.press(key)

def hold_key(key):
    """
    Mantiene presionada una tecla durante 0.9 segundos.

    Args:
        key (str): Tecla a mantener presionada.
    """
    pyautogui.keyDown(key)
    time.sleep(0.9)
    pyautogui.keyUp(key)

def read_hp_mp():
    """
    Lee los valores actuales de HP y MP desde la memoria del juego.

    Returns:
        tuple: (hp, mp) valores actuales de HP y MP.
    """
    hp = pm.read_int(OFFSET_HP)
    mp = pm.read_int(OFFSET_MP)
    return hp, mp

max_hp = 0
max_mp = 0

def update_max_values(current_hp, current_mp):
    """
    Actualiza los valores máximos de HP y MP si los actuales son mayores.

    Args:
        current_hp (int): HP actual.
        current_mp (int): MP actual.
    """
    global max_hp, max_mp
    if current_hp > max_hp:
        max_hp = current_hp
        print(f"[+] New max HP recorded: {max_hp}")
    if current_mp > max_mp:
        max_mp = current_mp
        print(f"[+] New max MP recorded: {max_mp}")

buffing = False
last_buff_applied = 0.0
def apply_buffs():
    """
    Aplica los buffs definidos en la configuración.
    Usa la tecla definida en KEY_BUFF, repitiendo NUM_BUFFS veces.
    """
    global buffing, last_buff_applied
    if time.time() - last_buff_applied >= 1200:
        print(f"[~] Applying {NUM_BUFFS} buff(s)...")
        buffing = True
        for i in range(NUM_BUFFS):
            print(f"   -> Buff {i+1}")
            pyautogui.keyDown(KEY_BUFF)
            pyautogui.keyDown(f"{i+1}")
            pyautogui.keyUp(f"{i+1}")
            pyautogui.keyUp(KEY_BUFF)
            time.sleep(USE_BUFF)
        last_buff_applied = time.time()
        buffing = False
        print("[✓] Buffs applied.")

# --- THREAD 1: Potion Usage ---
def thread_use_potions():
    """
    Hilo que usa pociones automáticamente cuando el HP es bajo.
    """
    global max_hp
    while True:
        hp, mp = read_hp_mp()
        update_max_values(hp, mp)
        if max_hp > 0 and hp / max_hp < 0.45:
            print("[!] Low HP: Using potions.")
            press_key(KEY_POTION_HP)
            press_key(KEY_POTION_MP)
        time.sleep(0.5)

# --- THREAD 2: Character State ---
current_state = "patrolling"

def thread_character_state():
    """
    Hilo que gestiona el estado del personaje (combate, patrulla, sentado) y realiza acciones según el estado.
    """
    global current_state, last_damage_received, last_hp
    while True:
        hp, mp = read_hp_mp()
        update_max_values(hp, mp)

        # Detect damage: only if it dropped compared to previous and is below max
        if hp < last_hp and hp < max_hp:
            last_damage_received = time.time()
            current_state = "combat"
        last_hp = hp

        time_without_damage = time.time() - last_damage_received
        print(f"Time without damage: {time_without_damage} s")

        if max_hp > 0 and hp / max_hp < 0.25 and time_without_damage > AUTOATTACK_DURATION:
            current_state = "sitting"
            press_key(KEY_PAUSE_COMBAT)
            print("[~] State: Sitting")
            time.sleep(1)
        else:
            current_state = "combat"
            print("[~] State: Combat")
            press_key(KEY_SEARCH)
            press_key(KEY_AUTOATTACK)
            press_key(KEY_SKILL1)
            press_key(KEY_AUTOATTACK)
            time.sleep(AUTOATTACK_DURATION)
            periodic_buff()

        if max_hp == hp:
            current_state = "patrolling"
            hold_key('a')
            press_key(KEY_SEARCH)
            press_key(KEY_AUTOATTACK)
            press_key(KEY_SKILL1)
            press_key(KEY_AUTOATTACK)

# --- THREAD 3: Collect Items ---
def thread_collect_items():
    """
    Hilo que recoge ítems automáticamente manteniendo presionada la tecla de recoger.
    """
    while True:
        pyautogui.keyDown(KEY_PICKUP)
        time.sleep(0.5)
        pyautogui.keyUp(KEY_PICKUP)
        time.sleep(0.1)

# --- Periodic Buff Function ---
def periodic_buff():
    """
    Aplica buffs periódicamente según el intervalo configurado.
    """
    global last_buff
    current_time = time.time()
    if current_time - last_buff > BUFF_INTERVAL * 60:
        apply_buffs()
        last_buff = current_time

# --- START BOT ---
if __name__ == "__main__":
    threading.Thread(target=thread_use_potions, daemon=True).start()
    threading.Thread(target=thread_character_state, daemon=True).start()
    threading.Thread(target=thread_collect_items, daemon=True).start()

    print("[✓] Bot started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[X] Bot stopped by user.")

