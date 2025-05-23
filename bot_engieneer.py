from pymem import Pymem
from pymem.process import module_from_name
import pyautogui
import time
import threading
import random

# --- CONFIGURACIÓN ---
PROCESS_NAME = "DboClient.exe"
OFFSET_HP = 0x0023B132A0
OFFSET_MP = 0x001FF53580

# --- TIEMPOS DE ENFRIAMIENTO EN SEGUNDOS ---
COOLDOWN_HAB1 = 4
COOLDOWN_HAB2 = 8
COOLDOWN_DEBUFF = 40
BUFF_INTERVAL = 60 * 18  # Buff dura 18 minutos

# --- HABILIDADES: TIEMPOS DE USO (animaciones, bloqueo de nuevas acciones) ---
USO_HAB1 = 3.0
USO_HAB2 = 4.5
USO_DEBUFF = 0.5

# --- TEMPORIZADORES ---
ultimo_uso_hab1 = 0
ultimo_uso_hab2 = 0
ultimo_uso_debuff = 0
ultimo_buff = 0
ultimo_hp_bajo = 0
ultimo_uso_habilidad = 0  # Controla tiempo de uso de animaciones

# --- Variable global para controlar estado de uso de habilidad ---
usando_habilidad = False

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

# --- FUNCIONES ---

def presionar_tecla(tecla):
    if tecla != 'v':
        time.sleep(0.2)
    pyautogui.press(tecla)

def mantener_tecla(tecla):
    pyautogui.keyDown(tecla)
    time.sleep(0.2)
    pyautogui.keyUp(tecla)
    time.sleep(0.2)

def leer_hp_mp():
    hp = pm.read_int(OFFSET_HP)
    mp = pm.read_int(OFFSET_MP)
    return hp, mp

# Variables globales para máximo HP y MP (inicializadas en cero)
max_hp = 0
max_mp = 0

def actualizar_maximos(hp_actual, mp_actual):
    global max_hp, max_mp
    if hp_actual > max_hp:
        max_hp = hp_actual
        print(f"[+] Nuevo HP máximo registrado: {max_hp}")
    if mp_actual > max_mp:
        max_mp = mp_actual
        print(f"[+] Nuevo MP máximo registrado: {max_mp}")

def usar_pociones(hp_actual, mp_actual):
    global max_hp, max_mp, ultimo_hp_bajo

    if max_hp == 0 or max_mp == 0:
        print("[!] Valores máximos no inicializados aún.")
        return False

    hp_ratio = hp_actual / max_hp
    mp_ratio = mp_actual / max_mp

    print(f"[INFO] HP: {hp_actual} / {max_hp} ({hp_ratio*100:.1f}%) | MP: {mp_actual} / {max_mp} ({mp_ratio*100:.1f}%)")

    pocion_usada = False

    if hp_ratio < 0.45:
        print(f"[!] HP bajo ({hp_ratio*100:.1f}%), usando poción de vida")
        presionar_tecla('9')
        ultimo_hp_bajo = time.time()
        pocion_usada = True

    if mp_ratio < 0.45:
        print(f"[!] MP bajo ({mp_ratio*100:.1f}%), usando poción de maná")
        presionar_tecla('0')
        pocion_usada = True

    return pocion_usada

def lanzar_buff():
    global ultimo_buff
    if time.time() - ultimo_buff >= BUFF_INTERVAL:
        print("[*] Lanzando buff ALT+1")
        pyautogui.keyDown('alt')
        presionar_tecla('1')
        pyautogui.keyUp('alt')
        ultimo_buff = time.time()
        time.sleep(3)  # Sleep 3 segundos antes de permitir nuevo buff

def usar_habilidad(tecla, cooldown, ultimo_uso_ref, duracion):
    global ultimo_uso_habilidad, usando_habilidad
    if time.time() - ultimo_uso_ref >= cooldown and time.time() - ultimo_uso_habilidad >= duracion:
        print(f"[+] Usando habilidad {tecla}")
        usando_habilidad = True
        presionar_tecla(tecla)
        ultimo_uso_habilidad = time.time()
        time.sleep(duracion)  # Esperar a que termine la animación
        usando_habilidad = False
        return time.time()
    return ultimo_uso_ref

def usar_debuff():
    global ultimo_uso_debuff, ultimo_uso_habilidad, usando_habilidad
    if time.time() - ultimo_uso_debuff >= COOLDOWN_DEBUFF and time.time() - ultimo_uso_habilidad >= USO_DEBUFF:
        print("[+] Usando Debuff (F1)")
        usando_habilidad = True
        presionar_tecla('f1')
        ultimo_uso_debuff = time.time()
        ultimo_uso_habilidad = time.time()
        time.sleep(USO_DEBUFF)
        usando_habilidad = False

def combate(hp_actual):
    global ultimo_uso_hab1, ultimo_uso_hab2, ultimo_hp_bajo

    tiempo_desde_hp_bajo = time.time() - ultimo_hp_bajo

    if tiempo_desde_hp_bajo < 5 and hp_actual > 0.45 * max_hp:
        print("[!] Pausando combate por recuperación de HP...")
        return

    print("[*] Buscando enemigo cercano...")
    presionar_tecla('tab')       # Selecciona enemigo más cercano
    time.sleep(0.5)

    print("[*] Autoatacando por al menos 5 segundos...")
    autoataque_inicio = time.time()
    while time.time() - autoataque_inicio < 5:
        presionar_tecla('f')
        ultimo_uso_hab1 = usar_habilidad('1', COOLDOWN_HAB1, ultimo_uso_hab1, USO_HAB1)
        ultimo_uso_hab2 = usar_habilidad('2', COOLDOWN_HAB2, ultimo_uso_hab2, USO_HAB2)
        time.sleep(0.2)

    usar_debuff()

def recoger():
    print("[*] Caminando en círculo hacia adelante y recogiendo objetos (4 segundos)...")

    pyautogui.keyDown('w')     # Avanzar
    pyautogui.keyDown('v')     # Recoger objetos
    pyautogui.keyDown('d')     # Girar hacia la derecha (giro)

    time.sleep(4)              # Mantener 4 segundos

    # Soltar todas las teclas
    pyautogui.keyUp('d')
    pyautogui.keyUp('v')
    pyautogui.keyUp('w')

    print("[+] Recolección en movimiento terminada.")


def patrullar():
    print("[*] Moviéndose a otra zona...")
    pyautogui.keyDown('w')
    time.sleep(1.5)
    pyautogui.keyUp('w')
    
    # Giro aleatorio a la derecha o izquierda
    direccion = random.choice(['a', 'd'])
    print(f"[*] Girando hacia {'izquierda' if direccion == 'a' else 'derecha'}...")
    pyautogui.keyDown(direccion)
    time.sleep(0.8)
    pyautogui.keyUp(direccion)

def mantener_recoleccion():
    global usando_habilidad
    while True:
        if not usando_habilidad:
            # Mantener tecla 'v' presionada
            pyautogui.keyDown('v')
        else:
            # Soltar 'v' mientras se usa habilidad
            pyautogui.keyUp('v')
        time.sleep(0.1)

# Iniciar hilo secundario para mantener recolección
t = threading.Thread(target=mantener_recoleccion, daemon=True)
t.start()

# --- BUCLE PRINCIPAL DEL BOT ---
while True:
    try:
        hp, mp = leer_hp_mp()
        actualizar_maximos(hp, mp)
        usar_pociones(hp, mp)
        lanzar_buff()
        combate(hp)
        recoger()
        patrullar()
        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[!] Bot detenido por el usuario.")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        break
