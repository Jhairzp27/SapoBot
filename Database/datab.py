import os
import sqlite3

# Ruta de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
DB_PATH = os.path.join(DATA_DIR, 'telegram_bot.db')

# Crear el directorio si no existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def create_table_if_not_exists():
    try:
        conex = sqlite3.connect(DB_PATH)
        cursor = conex.cursor()
        
        # Crear tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        
        # Crear tabla de capturas de pantalla
        cursor.execute('''
           
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                screenshot_path TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        conex.commit()
        cursor.close()
        conex.close()
    except sqlite3.OperationalError as e:
        print(f"Error al crear las tablas en la base de datos: {str(e)}")


def insert_or_update_user(telegram_id: int, name: str):
    try:
        conex = sqlite3.connect(DB_PATH)
        cursor = conex.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users(telegram_id, name)
            VALUES (?, ?)
        ''', (telegram_id, name))
        conex.commit()
        cursor.close()
        conex.close()
    except sqlite3.OperationalError as e:
        print(f"Error al insertar o actualizar el usuario en la base de datos: {str(e)}")
        
def insert_screenshot(user_id: int, screenshot_path: str):
    try:
        conex = sqlite3.connect(DB_PATH)
        cursor = conex.cursor()
        cursor.execute('''
            INSERT INTO screenshots (user_id, screenshot_path)
            VALUES (?, ?)
        ''', (user_id, screenshot_path))
        conex.commit()
        cursor.close()
        conex.close()
    except sqlite3.OperationalError as e:
        print(f"Error al insertar la captura de pantalla en la base de datos: {str(e)}")


# Llamar a la función para asegurarse de que la tabla exista
create_table_if_not_exists()
