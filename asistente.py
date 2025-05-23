from pymem import Pymem
from pymem.process import module_from_name
import pyautogui
import time
import threading

# --- CARGAR CONFIGURACIÓN DESDE TXT ---
def cargar_configuracion(archivo):
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
                if all(c in '0123456789ABCDEFabcdef' for c in valor):
                    config[clave] = int("0x" + valor, 16)
                else:
                    try:
                        config[clave] = int(valor)
                    except ValueError:
                        try:
                            config[clave] = float(valor)
                        except ValueError:
                            config[clave] = valor
    return config

config = cargar_configuracion("config_bot_fighter.txt")

# --- CONFIGURACIÓN DESDE ARCHIVO ---
PROCESS_NAME = config["PROCESS_NAME"]
OFFSET_HP = config["OFFSET_HP"]
OFFSET_MP = config["OFFSET_MP"]

TECLA_POCION_HP = config.get("TECLA_POCION_HP", "9")
TECLA_POCION_MP = config.get("TECLA_POCION_MP", "0")
TECLA_OBJETO = config.get("TECLA_OBJETO", "v")
TECLA_BUFF = config.get("TECLA_BUFF", "alt+1")
USO_BUFF = config.get("USO_BUFF", 2)
NUM_BUFS = config.get("NUM_BUFS", 1)
BUFF_INTERVAL = config.get("BUFF_INTERVAL", 5)  # minutos

# --- CONEXIÓN A MEMORIA ---
def esperar_proceso(nombre_proceso):
    while True:
        try:
            pm = Pymem(nombre_proceso)
            return pm
        except:
            print("[!] Esperando a que se abra el juego...")
            time.sleep(1)

pm = esperar_proceso(PROCESS_NAME)
base_module = module_from_name(pm.process_handle, PROCESS_NAME)
if base_module is None:
    raise Exception("[X] No se encontró el módulo del juego.")
base_addr = base_module.lpBaseOfDll

# --- VARIABLES DE ESTADO ---
max_hp = 0
max_mp = 0
ultimo_buff = 0

# --- FUNCIONES ---
def leer_hp_mp():
    hp = pm.read_int(OFFSET_HP)
    mp = pm.read_int(OFFSET_MP)
    return hp, mp

def actualizar_maximos(hp_actual, mp_actual):
    global max_hp, max_mp
    if hp_actual > max_hp:
        max_hp = hp_actual
        print(f"[+] Nuevo HP máximo: {max_hp}")
    if mp_actual > max_mp:
        max_mp = mp_actual
        print(f"[+] Nuevo MP máximo: {max_mp}")

def usar_pociones(hp_actual, mp_actual):
    global max_hp, max_mp
    if max_hp == 0 or max_mp == 0:
        return

    hp_ratio = hp_actual / max_hp
    mp_ratio = mp_actual / max_mp

    if hp_ratio < 0.45:
        print(f"[!] HP bajo ({hp_ratio*100:.1f}%), usando poción de vida")
        pyautogui.press(TECLA_POCION_HP)

    if mp_ratio < 0.45:
        print(f"[!] MP bajo ({mp_ratio*100:.1f}%), usando poción de maná")
        pyautogui.press(TECLA_POCION_MP)

def presionar_tecla(tecla):
    pyautogui.press(tecla)

def lanzar_buff():
    global ultimo_buff
    if time.time() - ultimo_buff >= BUFF_INTERVAL * 60:
        print("[*] Lanzando buffs...")
        try:
            pyautogui.keyDown('alt')
            for i in range(1, NUM_BUFS + 1):
                pyautogui.press(str(i))
                time.sleep(USO_BUFF)
            pyautogui.keyUp('alt')
            ultimo_buff = time.time()
            print("[+] Buff aplicado.")
        except Exception as e:
            print(f"[ERROR][Buff] {e}")
            pyautogui.keyUp('alt')  # Seguridad

# --- HILOS SECUNDARIOS ---
def hilo_pociones():
    while True:
        try:
            hp, mp = leer_hp_mp()
            actualizar_maximos(hp, mp)
            usar_pociones(hp, mp)
            time.sleep(1)  # Verificar cada segundo
        except Exception as e:
            print(f"[ERROR][Pociones] {e}")
            time.sleep(2)

def hilo_recoleccion():
    while True:
        try:
            pyautogui.press(TECLA_OBJETO)
            time.sleep(0.1)
        except Exception as e:
            print(f"[ERROR][Recolección] {e}")
            time.sleep(0.2)

# --- RUTINA PRINCIPAL ---
def rutina_principal():
    while True:
        try:
            hp, mp = leer_hp_mp()
            actualizar_maximos(hp, mp)
            usar_pociones(hp, mp)
            lanzar_buff()
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[!] Bot detenido por el usuario.")
            break
        except Exception as e:
            print(f"[ERROR][Principal] {e}")
            time.sleep(1)

# --- EJECUCIÓN ---
if __name__ == "__main__":
    print("[*] Iniciando asistente de bot...")
    threading.Thread(target=hilo_pociones, daemon=True).start()
    threading.Thread(target=hilo_recoleccion, daemon=True).start()
    rutina_principal()
