from pymem import Pymem
from pymem.process import module_from_name
import pyautogui
import time
import threading
import random

# --- CARGAR CONFIGURACIÓN DESDE TXT ---
def cargar_configuracion(archivo):
    """
    Carga la configuración del bot desde un archivo de texto.
    
    Lee un archivo de configuración línea por línea, parseando pares clave=valor.
    Detecta automáticamente valores hexadecimales, enteros, flotantes y strings.
    Ignora líneas vacías y comentarios que empiecen con #.
    
    Args:
        archivo (str): Ruta al archivo de configuración
        
    Returns:
        dict: Diccionario con las configuraciones parseadas
        
    Example:
        config = cargar_configuracion("config.txt")
        hp_offset = config["OFFSET_HP"]  # 0x20224CB8
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
NUM_BUFS = config.get("NUM_BUFS", 1)

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
TECLA_BUFF = config.get("TECLA_BUFF", "alt+1")
TECLA_POCION_HP = config.get("TECLA_POCION_HP", "9")
TECLA_POCION_MP = config.get("TECLA_POCION_MP", "0")
TECLA_AUTOATAQUE = config.get("TECLA_AUTOATAQUE", "f")
TECLA_OBJETO = config.get("TECLA_OBJETO", "v")
TECLA_PAUSA_COMBATE = config.get("TECLA_PAUSA_COMBATE", "x")

# --- TEMPORIZADORES ---
ultimo_uso_hab1 = 0
ultimo_uso_hab2 = 0
ultimo_uso_hab3 = 0
ultimo_uso_debuff = 0
ultimo_buff = 0
ultimo_hp_bajo = 0
ultimo_uso_habilidad = 0  # Controla tiempo de uso de animaciones
ultimo_hp = 0
ultimo_dano_recibido = time.time()  # Nueva variable para el timer de 6 segundos

# --- CONEXIÓN A MEMORIA ---
def esperar_proceso(nombre_proceso):
    """
    Espera a que el proceso del juego esté disponible y se conecta a él.
    
    Intenta conectarse continuamente al proceso hasta que tenga éxito.
    Útil para iniciar el bot antes que el juego o para reconexión automática.
    
    Args:
        nombre_proceso (str): Nombre del ejecutable del proceso (ej: "DboClient.exe")
        
    Returns:
        Pymem: Objeto Pymem conectado al proceso
        
    Example:
        pm = esperar_proceso("DboClient.exe")
    """
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
    """
    Simula la pulsación de una tecla con delay opcional.
    
    Presiona y suelta una tecla. Incluye un delay de 0.2s para todas las teclas
    excepto 'v' (recolección) que debe ser más rápida.
    
    Args:
        tecla (str): Tecla a presionar (ej: "1", "f1", "space")
        
    Returns:
        None
        
    Example:
        presionar_tecla("1")  # Presiona la tecla 1
        presionar_tecla("f1")  # Presiona F1
    """
    if tecla != 'v':
        time.sleep(0.2)
    pyautogui.press(tecla)

def mantener_tecla(tecla):
    """
    Mantiene una tecla presionada por medio segundo.
    
    Presiona una tecla, la mantiene por 0.5 segundos y luego la suelta.
    Útil para movimiento continuo o acciones que requieren presión sostenida.
    
    Args:
        tecla (str): Tecla a mantener presionada
        
    Returns:
        None
        
    Example:
        mantener_tecla("w")  # Mantiene W presionado por 0.5s
    """
    pyautogui.keyDown(tecla)
    time.sleep(0.5)
    pyautogui.keyUp(tecla)

def leer_hp_mp():
    """
    Lee los valores actuales de HP y MP desde la memoria del juego.
    
    Accede directamente a las direcciones de memoria donde el juego almacena
    los valores de vida y maná del personaje.
    
    Args:
        None
        
    Returns:
        tuple: (hp_actual, mp_actual) como enteros
        
    Example:
        hp, mp = leer_hp_mp()
        print(f"HP: {hp}, MP: {mp}")
    """
    hp = pm.read_int(OFFSET_HP)
    mp = pm.read_int(OFFSET_MP)
    return hp, mp

max_hp = 0
max_mp = 0

def actualizar_maximos(hp_actual, mp_actual):
    """
    Actualiza los valores máximos registrados de HP y MP.
    
    Mantiene registro de los valores más altos de HP y MP observados.
    Esto permite calcular porcentajes precisos para el uso de pociones.
    
    Args:
        hp_actual (int): Valor actual de HP
        mp_actual (int): Valor actual de MP
        
    Returns:
        None
        
    Example:
        actualizar_maximos(1500, 800)  # Actualiza máximos si son mayores
    """
    global max_hp, max_mp
    if hp_actual > max_hp:
        max_hp = hp_actual
        print(f"[+] Nuevo HP máximo registrado: {max_hp}")
    if mp_actual > max_mp:
        max_mp = mp_actual
        print(f"[+] Nuevo MP máximo registrado: {max_mp}")

def usar_pociones(hp_actual, mp_actual):
    """
    Usa pociones automáticamente basado en umbrales de HP/MP.
    
    Calcula los porcentajes de HP y MP y usa pociones si caen por debajo del 45%.
    Actualiza el timer de HP bajo para pausar combate temporalmente.
    
    Args:
        hp_actual (int): Valor actual de HP
        mp_actual (int): Valor actual de MP
        
    Returns:
        bool: True si se usó alguna poción, False en caso contrario
        
    Example:
        pocion_usada = usar_pociones(500, 200)
        if pocion_usada:
            print("Se usó una poción")
    """
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
        presionar_tecla(TECLA_POCION_HP)
        ultimo_hp_bajo = time.time()
        pocion_usada = True

    if mp_ratio < 0.45:
        print(f"[!] MP bajo ({mp_ratio*100:.1f}%), usando poción de maná")
        presionar_tecla(TECLA_POCION_MP)
        pocion_usada = True

    return pocion_usada

def lanzar_buff():
    """
    Lanza todos los buffs configurados en secuencia.
    
    Aplica buffs usando Alt+1, Alt+2, etc. según NUM_BUFS configurado.
    Solo ejecuta si ha pasado el intervalo configurado desde el último uso.
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        lanzar_buff()  # Lanza buffs si es momento
    """
    global ultimo_buff
    if time.time() - ultimo_buff >= BUFF_INTERVAL * 60:
        print("[*] Lanzando buffs...")
        time.sleep(3)
        for i in range(1, NUM_BUFS+1):
            pyautogui.keyDown('alt')
            presionar_tecla(str(i))
            pyautogui.keyUp('alt')
            time.sleep(USO_BUFF)

        ultimo_buff = time.time()
        time.sleep(1)

def usar_habilidad(tecla, cooldown, ultimo_uso_ref, duracion):
    """
    Usa una habilidad si está disponible (cooldown cumplido).
    
    Verifica que haya pasado suficiente tiempo desde el último uso y desde
    la última habilidad usada. Incluye animación y regreso al autoataque.
    
    Args:
        tecla (str): Tecla de la habilidad a usar
        cooldown (float): Tiempo de enfriamiento en segundos
        ultimo_uso_ref (float): Timestamp del último uso de esta habilidad
        duracion (float): Duración de la animación en segundos
        
    Returns:
        float: Nuevo timestamp si se usó la habilidad, o el original si no
        
    Example:
        ultimo_hab1 = usar_habilidad("1", 12.0, ultimo_hab1, 3.0)
    """
    global ultimo_uso_habilidad
    if time.time() - ultimo_uso_ref >= cooldown and time.time() - ultimo_uso_habilidad >= duracion:
        print(f"[+] Usando habilidad {tecla}")
        presionar_tecla(tecla)
        ultimo_uso_habilidad = time.time()
        time.sleep(duracion)
        presionar_tecla('f')
        return time.time()
    return ultimo_uso_ref

def usar_debuff():
    """
    Usa la habilidad de debuff si está disponible.
    
    Aplica debuff al enemigo respetando cooldown y tiempo desde última habilidad.
    Actualiza los timers globales de uso de habilidades.
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        usar_debuff()  # Usa debuff si está disponible
    """
    global ultimo_uso_debuff, ultimo_uso_habilidad
    if time.time() - ultimo_uso_debuff >= COOLDOWN_DEBUFF and time.time() - ultimo_uso_habilidad >= USO_DEBUFF:
        print("[+] Usando Debuff")
        presionar_tecla(TECLA_DEBUFF)
        ultimo_uso_debuff = time.time()
        ultimo_uso_habilidad = time.time()
        time.sleep(USO_DEBUFF)

def combate(hp_actual):
    """
    Ejecuta la rutina principal de combate.
    
    Busca enemigos, se acerca con dash, autoataca y usa habilidades en rotación.
    Incluye pausa temporal si el HP está en recuperación tras usar poción.
    
    Args:
        hp_actual (int): Valor actual de HP del personaje
        
    Returns:
        None
        
    Example:
        hp, _ = leer_hp_mp()
        combate(hp)
    """
    presionar_tecla('f')
    global ultimo_uso_hab1, ultimo_uso_hab2, ultimo_uso_hab3, ultimo_hp_bajo

    tiempo_desde_hp_bajo = time.time() - ultimo_hp_bajo

    if tiempo_desde_hp_bajo < 15 and hp_actual > 0.45 * max_hp:
        print("[!] Pausando combate por recuperación de HP...")
        presionar_tecla(TECLA_PAUSA_COMBATE)
        time.sleep(15)
        return

    print("[*] Buscando enemigo cercano...")
    presionar_tecla('tab')
    presionar_tecla('f')
    dash()
    time.sleep(0.5)

    print(f"[*] Autoatacando por al menos {AUTOATAQUE_DURACION} segundos...")
    autoataque_inicio = time.time()
    while time.time() - autoataque_inicio < AUTOATAQUE_DURACION:
        if time.time() - ultimo_uso_habilidad >= USO_HAB1:
            presionar_tecla(TECLA_AUTOATAQUE)
        ultimo_uso_hab1 = usar_habilidad(TECLA_HAB1, COOLDOWN_HAB1, ultimo_uso_hab1, USO_HAB1)
        ultimo_uso_hab2 = usar_habilidad(TECLA_HAB2, COOLDOWN_HAB2, ultimo_uso_hab2, USO_HAB2)
        ultimo_uso_hab3 = usar_habilidad(TECLA_HAB3, COOLDOWN_HAB3, ultimo_uso_hab3, USO_HAB3)
        time.sleep(0.2)

    usar_debuff()

def recoger():
    """
    Realiza recolección de objetos mientras se mueve en círculo.
    
    Se mueve hacia adelante en dirección aleatoria mientras mantiene
    presionada la tecla de recolección por 4 segundos.
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        recoger()  # Inicia recolección en movimiento
    """
    print("[*] Caminando en círculo hacia adelante y recogiendo objetos (4 segundos)...")
    pyautogui.keyDown('w')
    pyautogui.keyDown(TECLA_OBJETO)
    direccion = random.choice(['a', 'd'])
    pyautogui.keyDown(direccion)
    time.sleep(4)
    pyautogui.keyUp(direccion)
    pyautogui.keyUp(TECLA_OBJETO)
    pyautogui.keyUp('w')
    print("[+] Recolección en movimiento terminada.")

def dash():
    """
    Ejecuta una secuencia de dash para moverse rápidamente.
    
    Realiza una combinación de salto y movimiento para acercarse
    rápidamente al enemigo. Incluye orientación hacia el objetivo.
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        dash()  # Ejecuta dash hacia el enemigo
    """
    pyautogui.keyDown('space')
    pyautogui.keyUp('space')
    pyautogui.keyDown('w')
    pyautogui.keyUp('w')
    pyautogui.keyDown('w')
    pyautogui.keyUp('w')
    pyautogui.keyDown('f')
    pyautogui.keyUp('f')

def patrullar():
    """
    Ejecuta rutina de patrullaje para buscar enemigos.
    
    Se mueve a diferentes zonas, busca enemigos, aplica buffs si es necesario
    y realiza combate breve. Incluye movimiento aleatorio.
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        patrullar()  # Inicia rutina de patrullaje
    """
    global ultimo_buff
    print("[*] Moviéndose a otra zona...")
    pyautogui.keyDown('w')
    time.sleep(1.5)
    pyautogui.keyUp('w')
    direccion = random.choice(['a', 'd'])
    pyautogui.keyDown(direccion)
    time.sleep(1.2)
    pyautogui.keyUp(direccion)

    # Revisar si es momento de lanzar buffs
    if time.time() - ultimo_buff >= BUFF_INTERVAL * 60:
        lanzar_buff()

    print("[*] Buscando enemigos durante el patrullaje...")
    presionar_tecla('tab')  # Buscar enemigo
    time.sleep(0.3)
    presionar_tecla('f')    # Girar hacia el enemigo
    dash()
    presionar_tecla('tab')  # Buscar enemigo
    presionar_tecla('f')    # Girar hacia el enemigo
    time.sleep(0.3)

    temp_d = AUTOATAQUE_DURACION/2
    print("[*] Iniciando combate breve ({temp_d} segundos)...")
    inicio_combate = time.time()
    while time.time() - inicio_combate < temp_d:
        presionar_tecla(TECLA_AUTOATAQUE)
        time.sleep(0.4)

# ----- Hilos -----

def mantener_recoleccion():
    """
    Hilo que mantiene la recolección de objetos siempre activa.
    
    Ejecuta en hilo separado para mantener la tecla de recolección presionada
    continuamente, excepto durante el uso de habilidades con animación.
    
    Args:
        None
        
    Returns:
        None (función de hilo, ejecuta indefinidamente)
        
    Example:
        threading.Thread(target=mantener_recoleccion, daemon=True).start()
    """
    print("[+] 🔄 Hilo de recolección iniciado - SIEMPRE ACTIVO")
    
    while True:
        try:
            # La recolección está siempre activa, independiente del estado
            if time.time() - ultimo_uso_habilidad >= max(USO_HAB1, USO_HAB2, USO_HAB3, USO_DEBUFF):
                pyautogui.keyDown(TECLA_OBJETO)
            else:
                pyautogui.keyUp(TECLA_OBJETO)
            
            time.sleep(0.2)
        except Exception as e:
            print(f"[ERROR][Recolección] {e}")
            time.sleep(1)

def verificar_pociones():
    """
    Hilo que monitorea HP/MP y usa pociones automáticamente.
    
    Verifica constantemente los valores de HP y MP, actualiza máximos registrados,
    detecta daño recibido y usa pociones cuando es necesario.
    
    Args:
        None
        
    Returns:
        None (función de hilo, ejecuta indefinidamente)
        
    Example:
        threading.Thread(target=verificar_pociones, daemon=True).start()
    """
    global max_hp, max_mp, ultimo_hp, ultimo_dano_recibido
    
    while True:
        try:
            hp, mp = leer_hp_mp()
            actualizar_maximos(hp, mp)
            
            # Detectar daño recibido y actualizar timer
            if hp < ultimo_hp and ultimo_hp > 0:
                print(f"[!] Daño recibido: HP actual {hp} < HP anterior {ultimo_hp}")
                ultimo_dano_recibido = time.time()
            ultimo_hp = hp
            
            usar_pociones(hp, mp)
            time.sleep(5.0)  # Ajusta la frecuencia de verificación
        except Exception as e:
            print(f"[ERROR][Pociones] {e}")
            time.sleep(2)

estado_actual = "combate"  # Empezar en combate por seguridad
lock_estado = threading.Lock()

def rutina_combate():
    """
    Hilo principal que maneja el estado de combate activo.
    
    Ejecuta búsqueda de enemigos y combate cuando el estado es "combate".
    Busca enemigos cada AUTOATAQUE_DURACION segundos y ejecuta rutina completa.
    
    Args:
        None
        
    Returns:
        None (función de hilo, ejecuta indefinidamente)
        
    Example:
        threading.Thread(target=rutina_combate, daemon=True).start()
    """
    ultimo_busqueda_enemigo = 0
    
    while True:
        with lock_estado:
            if estado_actual != "combate":
                time.sleep(1)
                continue
        try:
            print("[*] ⚔️ MODO COMBATE ACTIVO")
            
            # Buscar enemigos cada AUTOATAQUE_DURACION segundos durante combate
            if time.time() - ultimo_busqueda_enemigo >= AUTOATAQUE_DURACION:
                print("[*] 🎯 Buscando enemigos (cada {AUTOATAQUE_DURACION} segundos)...")
                presionar_tecla('tab')  # Buscar enemigo
                presionar_tecla('f')    # Girar hacia enemigo
                dash()
                presionar_tecla('f')
                ultimo_busqueda_enemigo = time.time()
            
            hp, _ = leer_hp_mp()
            combate(hp)
            
        except Exception as e:
            print(f"[ERROR][Combate] {e}")
            time.sleep(2)

def buscar_pelea():
    """
    Intenta encontrar y atacar enemigos por 5 segundos durante patrullaje.
    
    Busca enemigos, se acerca y ataca por tiempo limitado. Puede interrumpirse
    si cambia el estado del bot. Usa habilidades disponibles durante el ataque.
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        buscar_pelea()  # Busca y ataca por 5 segundos
    """
    global ultimo_uso_hab1, ultimo_uso_hab2, ultimo_uso_hab3  # FIX: Declare as global
    
    print("[*] 🎯 INICIANDO BÚSQUEDA DE PELEA (5 segundos)...")
    
    # Buscar enemigo
    presionar_tecla('tab')
    time.sleep(0.3)
    presionar_tecla('f')  # Girar hacia enemigo
    dash()
    time.sleep(0.5)
    
    # Atacar por 5 segundos
    inicio_pelea = time.time()
    while time.time() - inicio_pelea < 5.0:
        # Verificar si seguimos en patrullaje (si no, salir)
        with lock_estado:
            if estado_actual != "patrullaje":
                print("[!] Saliendo de búsqueda de pelea - cambio de estado")
                return
        
        presionar_tecla(TECLA_AUTOATAQUE)
        ultimo_uso_hab1 = usar_habilidad(TECLA_HAB1, COOLDOWN_HAB1, ultimo_uso_hab1, USO_HAB1)
        ultimo_uso_hab2 = usar_habilidad(TECLA_HAB2, COOLDOWN_HAB2, ultimo_uso_hab2, USO_HAB2)
        ultimo_uso_hab3 = usar_habilidad(TECLA_HAB3, COOLDOWN_HAB3, ultimo_uso_hab3, USO_HAB3)
    
    print("[+] Búsqueda de pelea completada (5 segundos)")

def rutina_no_combate():
    """
    Hilo que maneja el estado de patrullaje/exploración.
    
    Ejecuta movimiento, búsqueda de enemigos, aplicación de buffs y camping
    cuando el estado es "patrullaje". Incluye recuperación de vida.
    
    Args:
        None
        
    Returns:
        None (función de hilo, ejecuta indefinidamente)
        
    Example:
        threading.Thread(target=rutina_no_combate, daemon=True).start()
    """
    global ultimo_dano_recibido
    
    while True:
        with lock_estado:
            if estado_actual != "patrullaje":
                time.sleep(1)
                continue
        try:
            print("[*] 🚶 MODO PATRULLAJE ACTIVO")
            
            # Ejecutar patrullaje básico (sin recolección, ya que hay hilo dedicado)
            print("[*] Moviéndose a otra zona...")
            pyautogui.keyDown('w')
            time.sleep(1.5)
            pyautogui.keyUp('w')
            direccion = random.choice(['a', 'd'])
            pyautogui.keyDown(direccion)
            time.sleep(0.8)
            pyautogui.keyUp(direccion)
            
            # Revisar buffs
            if time.time() - ultimo_buff >= BUFF_INTERVAL * 60:
                lanzar_buff()
            
            # Buscar pelea (atacar 5 segundos)
            buscar_pelea()
            
            # Verificar si necesita recuperar vida
            hp, _ = leer_hp_mp()
            if max_hp > 0 and hp / max_hp < 0.6:
                print("[*] Activando modo camping para recuperar vida.")
                presionar_tecla(TECLA_PAUSA_COMBATE)  # 'x'
                time.sleep(5)
                
            time.sleep(1)  # Pequeña pausa antes del siguiente ciclo
                
        except Exception as e:
            print(f"[ERROR][Patrullaje] {e}")
            time.sleep(2)

def monitoreo_patrullaje():
    """
    Hilo específico que detecta daño durante patrullaje.
    
    Monitorea constantemente el HP durante el patrullaje y cambia automáticamente
    a modo combate si detecta pérdida de vida, indicando presencia de enemigos.
    
    Args:
        None
        
    Returns:
        None (función de hilo, ejecuta indefinidamente)
        
    Example:
        threading.Thread(target=monitoreo_patrullaje, daemon=True).start()
    """
    global estado_actual, ultimo_dano_recibido
    hp_anterior = None
    
    while True:
        try:
            with lock_estado:
                en_patrullaje = (estado_actual == "patrullaje")
            
            if en_patrullaje:
                hp_actual, _ = leer_hp_mp()
                
                # Solo detectar daño si tenemos un HP anterior válido
                if hp_anterior is not None and hp_actual < hp_anterior:
                    print(f"[!] 🚨 DAÑO DETECTADO EN PATRULLAJE: {hp_anterior} → {hp_actual}")
                    ultimo_dano_recibido = time.time()
                    
                    with lock_estado:
                        estado_actual = "combate"
                    print("[!] ⚔️ CAMBIO AUTOMÁTICO: PATRULLAJE → COMBATE")
                
                hp_anterior = hp_actual
            else:
                # Si no estamos en patrullaje, resetear el HP anterior
                hp_anterior = None
                
            time.sleep(0.5)  # Monitoreo frecuente durante patrullaje
            
        except Exception as e:
            print(f"[ERROR][Monitoreo Patrullaje] {e}")
            time.sleep(1)

def estado_personaje_loop():
    """
    Hilo maestro que gestiona las transiciones entre estados.
    
    Controla el cambio automático entre modo "combate" y "patrullaje" basado
    en el tiempo transcurrido since el último daño recibido (10 segundos).
    
    Args:
        None
        
    Returns:
        None (función de hilo, ejecuta indefinidamente)
        
    Example:
        threading.Thread(target=estado_personaje_loop, daemon=True).start()
    """
    global estado_actual, ultimo_dano_recibido
    
    while True:
        try:
            hp, _ = leer_hp_mp()
            if max_hp == 0:
                actualizar_maximos(hp, _)
                time.sleep(1)
                continue

            # Determinar estado basado en el timer de 10 segundos
            tiempo_sin_dano = time.time() - ultimo_dano_recibido
            
            # Lógica de transición de estados