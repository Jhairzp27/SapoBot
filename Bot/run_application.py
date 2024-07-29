# run_application.py

import os

# Ruta del ejecutable que deseas iniciar
APPLICATION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DesktopGoose-v0.31','GooseDesktop.exe')

def run_application():
    if os.path.exists(APPLICATION_PATH):
        os.startfile(APPLICATION_PATH)  # En Windows, para abrir un archivo o ejecutar un programa
            
if __name__ == "__main__":
    run_application()
