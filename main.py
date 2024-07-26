import threading
from Bot.comandos import run_bot
import flet as ft
from GUI.interface import start_interface

if __name__ == "__main__":
    # Ejecutar el bot de Telegram en un hilo separado
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Ejecutar la aplicación Flet
    ft.app(target=start_interface)
