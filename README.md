# 🐉 Dragon Ball Online Bot — Versión Avanzada

Bot de automatización para *Dragon Ball Online (DboClient.exe)* en servidores privados. Incluye combate automático, patrullaje inteligente, recolección de ítems, uso de habilidades, buffs y recuperación con sistema de gestión de estados multihilo y lectura directa de memoria.

---

## ✨ Características

- 🎯 **Detección de daño recibido** y cambio de estado a patrullaje tras 6 segundos sin recibir daño.
- ⚔️ **Sistema de combate** automático con habilidades rotativas configurables.
- 🧭 **Patrullaje en zona segura** con transición inteligente entre estados.
- 🍃 **Modo recuperación** con uso de pociones y descanso si la salud baja.
- 📦 **Recolección de ítems** post-combate.
- 🧠 **Control multihilo** para ejecutar combate y no-combate simultáneamente.
- 🛠 **Lectura de memoria** de vida, maná y enemigo para toma de decisiones precisa.

---

## 📂 Estructura
📁 bot_dbo/
├── bot_main.py # Script principal
├── combat_thread.py # Manejador del hilo de combate
├── patrol_thread.py # Manejador del hilo de patrullaje
├── memory_reader.py # Utilidades para leer memoria del proceso
├── config_bot_fighter.txt# Archivo de configuración personalizable
├── utils.py # Utilidades comunes (timers, logs, etc.)
└── README.md # Este archivo

---

## ⚙️ Requisitos

- ✅ Python 3.8+
- 📦 Librerías necesarias:
  ```bash
  pip install pywin32 keyboard
