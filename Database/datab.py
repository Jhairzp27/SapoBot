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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        conex.commit()
        cursor.close()
        conex.close()
    except sqlite3.OperationalError as e:
        print(f"Error al crear la tabla en la base de datos: {str(e)}")

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

# Llamar a la función para asegurarse de que la tabla exista
create_table_if_not_exists()
