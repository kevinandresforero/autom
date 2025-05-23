# Bot DBO Fighter

Un bot automatizado para Dragon Ball Online (DBO) que gestiona combate, habilidades, pociones y recolección de objetos de forma inteligente usando un sistema de estados basado en detección de daño.

## 🎯 Características Principales

### Sistema de Estados Inteligente
- **Modo Combate (⚔️)**: Activo cuando recibes daño, busca enemigos cada 7 segundos
- **Modo Patrullaje (🚶)**: Activo tras 10 segundos sin recibir daño, explora y busca enemigos
- **Transición automática**: Cambio instantáneo a combate si recibes daño durante patrullaje

### Funcionalidades Automáticas
- **Gestión de HP/MP**: Uso automático de pociones cuando bajan del 45%
- **Rotación de habilidades**: Uso inteligente con cooldowns y animaciones
- **Sistema de buffs**: Aplicación automática cada X minutos (configurable)
- **Recolección continua**: Recoge objetos automáticamente durante todo el gameplay
- **Detección de memoria**: Lee HP/MP directamente de la memoria del juego

## 📋 Requisitos

### Dependencias Python
```bash
pip install pymem pyautogui
```

### Archivos Necesarios
- `bot_dbo_fighter.py` - Script principal del bot
- `config_bot_fighter.txt` - Archivo de configuración

## ⚙️ Configuración

### Archivo config_bot_fighter.txt

Crea un archivo llamado `config_bot_fighter.txt` en la misma carpeta del script con el siguiente contenido:

```ini
# --- CONFIGURACIÓN DEL BOT DBO ---
# Direcciones de memoria (hexadecimal sin 0x)
OFFSET_HP = 20224CB8
OFFSET_MP = 20224CC0

# Enfriamientos de habilidades (en segundos)
COOLDOWN_HAB1 = 12
COOLDOWN_HAB2 = 20
COOLDOWN_HAB3 = 5
COOLDOWN_DEBUFF = 24

# Numero de Buffs
NUM_BUFS = 4

# Intervalo para lanzar el buff (en minutos)
BUFF_INTERVAL = 19

# Tiempo de animación/duración de habilidades (en segundos)
USO_HAB1 = 3
USO_HAB2 = 1
USO_HAB3 = 3.5
USO_DEBUFF = 1.5
USO_BUFF = 2

# Tiempo de autoataque (en segundos)
AUTOATAQUE_DURACION = 7

# Nombre del proceso del juego
PROCESS_NAME = DboClient.exe
```

### Parámetros de Configuración

#### Direcciones de Memoria
- `OFFSET_HP`: Dirección hexadecimal donde se almacena la vida actual
- `OFFSET_MP`: Dirección hexadecimal donde se almacena el maná actual

#### Sistema de Habilidades
- `COOLDOWN_HAB1/2/3`: Tiempo de enfriamiento de cada habilidad (segundos)
- `COOLDOWN_DEBUFF`: Tiempo de enfriamiento del debuff (segundos)
- `USO_HAB1/2/3`: Duración de la animación de cada habilidad (segundos)
- `USO_DEBUFF`: Duración de la animación del debuff (segundos)

#### Sistema de Buffs
- `NUM_BUFS`: Cantidad de buffs a lanzar (teclas Alt+1, Alt+2, etc.)
- `BUFF_INTERVAL`: Intervalo entre aplicaciones de buff (minutos)
- `USO_BUFF`: Tiempo de espera entre cada buff individual (segundos)

#### Configuraciones de Combate
- `AUTOATAQUE_DURACION`: Tiempo mínimo de autoataque antes de usar habilidades (segundos)
- `PROCESS_NAME`: Nombre exacto del ejecutable del juego

#### Teclas Configurables (Opcionales)
Si no se especifican, se usan los valores por defecto:

```ini
# Teclas de habilidades
TECLA_HAB1 = 1
TECLA_HAB2 = 2
TECLA_HAB3 = 3
TECLA_DEBUFF = f1

# Teclas de consumibles
TECLA_POCION_HP = 9
TECLA_POCION_MP = 0

# Teclas de acción
TECLA_AUTOATAQUE = f
TECLA_OBJETO = v
TECLA_PAUSA_COMBATE = x
TECLA_BUFF = alt+1
```

## 🚀 Uso

1. **Configurar el archivo**: Edita `config_bot_fighter.txt` con tus valores específicos
2. **Ejecutar el juego**: Inicia Dragon Ball Online
3. **Ejecutar el bot**: 
   ```bash
   python bot_dbo_fighter.py
   ```
4. **Posicionar el personaje**: Coloca tu personaje en la zona donde quieres farmear
5. **El bot tomará control automáticamente**

## 🔧 Funcionamiento del Sistema

### Detección de Estados
- **Timer de daño**: El bot registra cada vez que recibes daño
- **Umbral de 10 segundos**: Si no recibes daño por 10 segundos, cambia a patrullaje
- **Detección instantánea**: Cualquier pérdida de HP en patrullaje activa combate inmediatamente

### Modo Combate (⚔️)
1. Busca enemigos cada 7 segundos (Tab + F)
2. Usa dash para acercarse
3. Ejecuta rotación de autoataque + habilidades
4. Aplica debuff cuando está disponible
5. Pausa combate si HP está bajo después de usar poción

### Modo Patrullaje (🚶)
1. Se mueve aleatoriamente por el área
2. Busca enemigos y ataca por 5 segundos
3. Aplica buffs según el intervalo configurado
4. Activa modo camping si HP < 60%
5. Monitorea constantemente la pérdida de HP

### Hilos de Ejecución
- **Estado del personaje**: Gestiona transiciones entre combate/patrullaje
- **Rutina de combate**: Maneja la lógica de combate activo
- **Rutina de patrullaje**: Maneja la exploración y búsqueda
- **Monitoreo de patrullaje**: Detecta daño recibido durante patrullaje
- **Verificación de pociones**: Monitorea HP/MP y usa pociones automáticamente
- **Recolección continua**: Mantiene activa la recolección de objetos 24/7

## ⚠️ Consideraciones Importantes

### Configuración de Memoria
- Las direcciones de memoria (`OFFSET_HP` y `OFFSET_MP`) pueden cambiar entre versiones del juego
- Si el bot no detecta correctamente HP/MP, será necesario actualizar estas direcciones
- Usa herramientas como Cheat Engine para encontrar las direcciones correctas

### Rendimiento
- El bot usa múltiples hilos para operaciones simultáneas
- Consume recursos mínimos del sistema
- Optimizado para largas sesiones de farming

### Seguridad
- El bot lee memoria pero no la modifica
- Simula pulsaciones de teclado reales
- Incluye delays aleatorios para parecer más humano

## 🐛 Solución de Problemas

### El bot no detecta HP/MP
- Verifica que `PROCESS_NAME` coincida exactamente con el ejecutable
- Actualiza `OFFSET_HP` y `OFFSET_MP` usando Cheat Engine
- Asegúrate de ejecutar el script como administrador

### Problemas con las teclas
- Revisa que las teclas configuradas coincidan con tu setup del juego
- Verifica que el juego esté en ventana activa
- Ajusta los tiempos de `USO_HAB` si las animaciones son diferentes

### Problemas de memoria
- Cierra otros programas que usen mucha RAM
- Reinicia el juego si lleva mucho tiempo abierto
- El bot detectará automáticamente si el proceso se cierra

## 📝 Logs del Sistema

El bot proporciona información detallada en consola:
- Estado actual (Combate/Patrullaje)
- Tiempo sin recibir daño
- Uso de habilidades y pociones
- Detección de máximos de HP/MP
- Cambios de estado automáticos

## 🎮 Personalización Avanzada

### Ajustar Agresividad
- Reduce `AUTOATAQUE_DURACION` para más uso de habilidades
- Aumenta cooldowns si tus habilidades son más lentas
- Modifica `BUFF_INTERVAL` según la duración de tus buffs

### Optimizar Supervivencia
- Ajusta los umbrales de pociones modificando las condiciones en `usar_pociones()`
- Cambia el tiempo de pausa tras HP bajo en la función `combate()`
- Personaliza la lógica de camping modificando el umbral del 60%

---

**Nota**: Este bot está diseñado para uso educativo y personal. Asegúrate de cumplir con los términos de servicio del juego.
