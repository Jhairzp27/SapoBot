import sqlite3

# Verifica si exista una base de datos con el nombre indicado para conectarse
# si esta base no existe, la creará
conex = sqlite3.connect('telegram_bot.db')

# Ayuda a ejecutar comandos sql
cursor = conex.cursor()

# Creacion de tabla para almacenar los datos
cursor.execute('''  
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT
)

''')

conex.commit()
cursor.close()
conex.close()

