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

COOLDOWN_HAB1 = config["COOLDOWN_HAB1"]
COOLDOWN_HAB2 = config["COOLDOWN_HAB2"]
COOLDOWN_HAB3 = config["COOLDOWN_HAB3"]
COOLDOWN_DEBUFF = config["COOLDOWN_DEBUFF"]
BUFF_INTERVAL = config["BUFF_INTERVAL"]
NUM_BUFS = int(config.get("NUM_BUFS", 1))

USO_HAB1 = config["USO_HAB1"]
USO_HAB2 = config["USO_HAB2"]
USO_HAB3 = config["USO_HAB3"]
USO_DEBUFF = config["USO_DEBUFF"]
AUTOATAQUE_DURACION = config["AUTOATAQUE_DURACION"]
USO_BUFF = config.get("USO_BUFF", 2)

TECLA_HAB1 = config.get("TECLA_HAB1", "1")
TECLA_HAB2 = config.get("TECLA_HAB2", "2")
TECLA_HAB3 = config.get("TECLA_HAB3", "3")
TECLA_DEBUFF = config.get("TECLA_DEBUFF", "f1")
TECLA_BUFF = config.get("TECLA_BUFF", "alt")
TECLA_POCION_HP = config.get("TECLA_POCION_HP", "9")
TECLA_POCION_MP = config.get("TECLA_POCION_MP", "0")
TECLA_AUTOATAQUE = config.get("TECLA_AUTOATAQUE", "f")
TECLA_OBJETO = config.get("TECLA_OBJETO", "v")
TECLA_PAUSA_COMBATE = config.get("TECLA_PAUSA_COMBATE", "x")
TECLA_BUSCAR = "tab"

# --- TEMPORIZADORES ---
ultimo_uso_hab1 = 0
ultimo_uso_hab2 = 0
ultimo_uso_hab3 = 0
ultimo_uso_debuff = 0
ultimo_buff = 0
ultimo_hp_bajo = 0
ultimo_uso_habilidad = 0
ultimo_hp = 0
ultimo_dano_recibido = time.time()

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

# --- FUNCIONES GENERALES ---
def presionar_tecla(tecla):
    if tecla != 'v':
        time.sleep(0.2)
    pyautogui.press(tecla)

def mantener_tecla(tecla):
    pyautogui.keyDown(tecla)
    time.sleep(0.9)
    pyautogui.keyUp(tecla)

def leer_hp_mp():
    hp = pm.read_int(OFFSET_HP)
    mp = pm.read_int(OFFSET_MP)
    return hp, mp

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


buffeando = False
ultimo_buff_aplicado = 0.0
def aplicar_buffs():
    """
    Aplica los buffs definidos en la configuración. 
    Usa la tecla especificada en TECLA_BUFF, repitiendo NUM_BUFS veces.
    """
    global buffeando, ultimo_buff_aplicado
    if time.time() - ultimo_buff_aplicado >= 1200 :
        print(f"[~] Aplicando {NUM_BUFS} buff(s)...")
        buffeando = True
        for i in range(NUM_BUFS):
            print(f"   -> Buff {i+1}")
            pyautogui.keyDown(TECLA_BUFF)
            pyautogui.keyDown(f"{i+1}")
            pyautogui.keyUp(f"{i+1}")
            pyautogui.keyUp(TECLA_BUFF)
            time.sleep(USO_BUFF)  # Puedes ajustar este tiempo si las animaciones son más largas
        ultimo_buff_aplicado = time.time()
        buffeando = False
    print("[✓] Buffs aplicados.")


# --- HILO 1: Uso de Pociones ---
def hilo_uso_pociones():
    global max_hp
    while True:
        hp, mp = leer_hp_mp()
        actualizar_maximos(hp, mp)
        if max_hp > 0 and hp / max_hp < 0.45:
            print("[!] Vida baja: Usando pociones.")
            presionar_tecla(TECLA_POCION_HP)
            presionar_tecla(TECLA_POCION_MP)
        time.sleep(0.5)

# --- HILO 2: Estados del personaje ---
estado_actual = "patrullando"

def hilo_estado_personaje():
    global estado_actual, ultimo_dano_recibido, ultimo_hp
    while True:
        hp, mp = leer_hp_mp()
        actualizar_maximos(hp, mp)

        # Detectar daño: solo si bajó respecto al anterior Y está debajo del máximo
        if hp < ultimo_hp and hp < max_hp:
            ultimo_dano_recibido = time.time()
            estado_actual = "combate"
        ultimo_hp = hp


        tiempo_sin_dano = time.time() - ultimo_dano_recibido
        print(f"Tiempo sin daño: {tiempo_sin_dano} s")

        if max_hp > 0 and hp / max_hp < 0.25 and tiempo_sin_dano > AUTOATAQUE_DURACION:
            estado_actual = "sentado"
            presionar_tecla(TECLA_PAUSA_COMBATE)
            print("[~] Estado: Sentado")
            time.sleep(1)
        else:
            estado_actual = "combate"
            print("[~] Estado: Combate")
            presionar_tecla(TECLA_BUSCAR)
            presionar_tecla(TECLA_AUTOATAQUE)
            presionar_tecla(TECLA_HAB1)
            presionar_tecla(TECLA_AUTOATAQUE)
            time.sleep(AUTOATAQUE_DURACION)
            buff_periodico()

        if max_hp == hp:
            estado_actual = "patrullando"
            mantener_tecla('a')
            presionar_tecla(TECLA_BUSCAR)
            presionar_tecla(TECLA_AUTOATAQUE)
            presionar_tecla(TECLA_HAB1)
            presionar_tecla(TECLA_AUTOATAQUE)

# --- HILO 3: Recolectar objetos ---
def hilo_recolecta_objetos():
    while True:
        pyautogui.keyDown(TECLA_OBJETO)
        time.sleep(0.5)
        pyautogui.keyUp(TECLA_OBJETO)
    time.sleep(0.1)


# --- Funcion de buffos: buff periodico ---
def buff_periodico():
    global ultimo_buff
    tiempo_actual = time.time()
    if tiempo_actual - ultimo_buff > BUFF_INTERVAL*60:
        aplicar_buffs()
        ultimo_buff = tiempo_actual

# --- HILO 4: Buffme up ---
#def hilo_buffos():
    


# --- INICIAR BOT ---
if __name__ == "__main__":
    threading.Thread(target=hilo_uso_pociones, daemon=True).start()
    threading.Thread(target=hilo_estado_personaje, daemon=True).start()
    threading.Thread(target=hilo_recolecta_objetos, daemon=True).start()

    print("[✓] Bot iniciado. Presiona Ctrl+C para detener.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[X] Bot detenido por el usuario.")

