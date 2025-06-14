import os
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from src.bot_white_stones import BotWhiteStones
import threading
import time

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "src", "config_bot.txt")

class DBOBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DBO Bot")
        self.root.geometry("600x500")
        self.bot = None

        # Título
        title = tk.Label(root, text="🤖 Welcome to DBO Bot! 🤖", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Descripción
        desc = tk.Label(root, text="Hello! I am your assistant bot for DBOZero.\n\nWith this bot, you can:\n"
                                   "1. Farm Whitestones automatically\n"
                                   "2. Use the Loot Assistant to help you collect items and buff your character\n"
                                   "0. Configure the bot to your preferences",
                        font=("Arial", 11), justify="left")
        desc.pack(pady=10)

        # Botones de opciones
        btn_farm = tk.Button(root, text="1 - Farm Whitestones", width=30, command=self.start_farm)
        btn_farm.pack(pady=5)

        btn_loot = tk.Button(root, text="2 - Loot Assistant (buff/loot)", width=30, command=self.show_loot)
        btn_loot.pack(pady=5)

        btn_config = tk.Button(root, text="0 - Configure", width=30, command=self.show_config)
        btn_config.pack(pady=5)

        # Botón para salir
        btn_exit = tk.Button(root, text="Exit", width=30, command=self.root.quit)
        btn_exit.pack(pady=20)

    def start_farm(self):
        time.sleep(5)
        if self.bot is None:
            self.bot = BotWhiteStones()
            threading.Thread(target=self.bot.start, daemon=True).start()
            messagebox.showinfo("DBO Bot", "Bot started: Farm Whitestones")
        else:
            messagebox.showinfo("DBO Bot", "Bot is already running.")

    def show_loot(self):
        time.sleep(5)
        messagebox.showinfo("DBO Bot", "Loot Assistant (includes buffing your character)\nThis feature is under construction.")

    def show_config(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Edit config_bot.txt")
        config_window.geometry("700x600")

        # Área de texto para editar el archivo
        text_area = scrolledtext.ScrolledText(config_window, wrap=tk.WORD, font=("Consolas", 11))
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

        # Cargar el archivo
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading config_bot.txt: {e}"
        text_area.insert(tk.END, content)

        # Botón para guardar cambios
        def save_config():
            try:
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    f.write(text_area.get("1.0", tk.END))
                messagebox.showinfo("Config", "Configuration saved successfully.")
            except Exception as e:
                messagebox.showerror("Config", f"Error saving configuration:\n{e}")

        btn_save = tk.Button(config_window, text="Save", width=20, command=save_config)
        btn_save.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = DBOBotApp(root)
    root.mainloop()