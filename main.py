import threading
from Bot.comandos import run_bot
import tkinter as tk

from GUI.interface import Window


if __name__ == "__main__":
    # Ejecutar el bot de Telegram en un hilo separado
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    root = tk.Tk()
    app = Window(root)
    root.mainloop()
