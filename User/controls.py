import telebot
from telebot import types

# Conexión con nuestro BOT
TOKEN = '7350752233:AAFZTB3HMBbzbFMHh0-7q3XDbKnDb-ExWLg'
bot = telebot.TeleBot(TOKEN)

# Función para crear el menú de botones
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_help = types.KeyboardButton('/help')
    btn_demo = types.KeyboardButton('/demo')
    btn_screenshot = types.KeyboardButton('/screenshot')
    btn_send_files = types.KeyboardButton('/send_files')
    btn_list_files = types.KeyboardButton('/list_files')
    btn_list_directory = types.KeyboardButton('/list_directory')
    markup.add(btn_help, btn_demo, btn_screenshot, btn_send_files, btn_list_files, btn_list_directory)
    return markup

# Función para enviar instrucciones y mostrar botones
def send_instructions(chat_id):
    markup = get_main_menu()
    welcome_message = ("Hola! Soy tu bot. Puedes interactuar conmigo usando los siguientes comandos:\n"
                       "/help - Muestra este mensaje de ayuda\n"
                       "/demo - Muestra una demostración\n"
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
                    '/demo - Muestra una demostración\n'
                    '/screenshot - Toma y envía una captura de pantalla\n'
                    '/send_files - Envía un archivo\n'
                    '/list_files - Lista los directorios en la raíz del disco C\n'
                    '/list_directory - Lista el contenido de una carpeta específica')
    bot.send_message(message.chat.id, help_message, reply_markup=markup)
