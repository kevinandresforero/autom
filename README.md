# Bot DBO Fighter (Versión OOP)

## 🚀 Comandos Rápidos de Instalación y Uso

```bash
# 1. Clona el repositorio
git clone https://github.com/kevinandresforero/autom

# 2. Entra a la carpeta del proyecto
cd tu-repo-bot-dbozero/autom

# 3. Instala las dependencias necesarias
pip install pymem pyautogui

# 4. Ejecuta el bot (elige el archivo principal que desees usar)
python main.py
# o para el asistente clásico
python src/asistente.py
```

---

## 📦 Estructura del Proyecto (POO)

El bot está desarrollado en **Python** usando **Programación Orientada a Objetos (POO)** y una arquitectura modular.  
Cada funcionalidad principal está separada en clases y archivos independientes para facilitar la extensión y el mantenimiento.

```
autom/
│
├── main.py                      # Interfaz gráfica principal (Tkinter)
├── README.md                    # Este archivo
└── src/
    ├── asistente.py
    ├── bot_figter_basics.py
    ├── bot_white_stones.py
    ├── buff_thread.py
    ├── build.py
    ├── character.py
    ├── config_bot.txt
    ├── general_actions.py
    ├── load_configuration.py
    ├── memory_connector.py
    ├── potions.py
    ├── search_and_attack.py
    ├── search_file.py
```

---

## 🧩 Principales Clases y Funciones

### main.py
- **Interfaz gráfica**: Permite iniciar/detener el bot, editar configuración y mostrar información.

### src/asistente.py
- **Modo asistente clásico**: Ejecuta el bot desde consola, con hilos para pociones, buffs y recolección.

### src/build.py
- **Build**: Clase base para bots. Define estados (`ALIVE`, `DEAD`, `IN_COMBAT`, etc.), timers y acciones generales.

### src/character.py
- **Character**: Hereda de Build. Añade lógica de HP/MP, métodos para actualizar valores y buscar enemigos.

### src/bot_white_stones.py
- **BotWhiteStones**: Bot especializado en farmear Whitestones. Ejecuta la lógica principal de combate, buffs y patrullaje.

### src/buff_thread.py
- **BuffThread**: Hilo que aplica automáticamente los buffs usando las teclas F1 a Fn según configuración.

### src/potions.py
- **PotionThread**: Hilo que monitoriza el HP y usa pociones automáticamente si baja del umbral configurado.

### src/search_and_attack.py
- **SearchAndAttackThread**: Hilo que busca enemigos, ataca y usa habilidades según cooldowns y estado del personaje.

### src/general_actions.py
- **GeneralActions**: Métodos utilitarios para presionar teclas, combos, mantener teclas, etc.

### src/load_configuration.py
- **LoadConfiguration**: Carga y parsea el archivo de configuración, además de leer valores de memoria del juego.

### src/memory_connector.py
- **MemoryConnection**: Conecta con el proceso del juego y obtiene la base de memoria para leer HP/MP.

### src/search_file.py
- **file()**: Devuelve la ruta absoluta al archivo de configuración.

---

## 🖥️ Uso de la Interfaz Gráfica

Al ejecutar `python main.py` se abre una ventana con las siguientes opciones:

- **1 - Farm Whitestones**: Inicia el bot de farmeo automático.
- **2 - Loot Assistant (buff/loot)**: (En desarrollo) Asistente para recoger objetos y aplicar buffs.
- **0 - Configure**: Abre un editor para modificar el archivo `config_bot.txt` directamente desde la interfaz.
- **Stop Bot**: Detiene el bot sin cerrar la aplicación.
- **Exit**: Cierra la interfaz gráfica.

### Edición de Configuración

Desde el botón **Configure** puedes editar y guardar el archivo `config_bot.txt` sin salir del programa.  
Todos los cambios se aplican al guardar y reiniciar el bot.

---

## ⚙️ Funcionalidades Automáticas

- **Gestión de HP/MP**: Uso automático de pociones si el HP baja del 45%.
- **Rotación de habilidades**: Uso inteligente de habilidades con cooldowns y animaciones.
- **Sistema de buffs**: Aplica automáticamente los buffs configurados (F1 a Fn).
- **Recolección continua**: Recoge objetos automáticamente.
- **Detección de memoria**: Lee HP/MP directamente de la memoria del juego.
- **Sistema de estados**: Cambia entre combate, patrullaje y buffeo según la situación.

---

## 📝 Personalización y Configuración

Edita el archivo `src/config_bot.txt` para ajustar:
- Direcciones de memoria (OFFSET_HP, OFFSET_MP)
- Cooldowns y duración de habilidades
- Número de buffs y teclas asociadas (F1, F2, ...)
- Teclas de acción y consumibles
- Nombre del proceso del juego

---

## 🛠️ Notas y Consejos

- Ejecuta el bot como administrador para permitir la lectura de memoria.
- Si cambian las direcciones de memoria del juego, actualízalas en el archivo de configuración.
- El bot está optimizado para minimizar el uso de recursos y simular pulsaciones humanas.

---

## ❓ Preguntas Frecuentes

- **¿Puedo usarlo en cualquier versión de DBO?**  
  Sí, solo debes actualizar las direcciones de memoria en el archivo de configuración.

- **¿Cómo detengo el bot sin cerrar la ventana?**  
  Usa el botón **Stop Bot** en la interfaz.

- **¿Puedo agregar más funciones?**  
  Sí, la estructura modular y orientada a objetos facilita la extensión del bot.

---

**Nota:** Este bot es solo para fines educativos y personales. Úsalo bajo tu propio riesgo y respeta los términos de servicio del juego.
