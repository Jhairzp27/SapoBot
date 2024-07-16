import subprocess
from PIL import Image
import os

# Función para esconder un comando en una imagen
def encode_command_in_image(image_path, command, output_path):
    img = Image.open(image_path)
    encoded_img = img.copy()
    width, height = img.size
    command += '\0'  # Añadir un terminador de cadena

    bin_command = ''.join(format(ord(char), '08b') for char in command)
    data_index = 0

    for y in range(height):
        for x in range(width):
            pixel = list(img.getpixel((x, y)))
            for n in range(3):  # Iterar sobre R, G, B
                if data_index < len(bin_command):
                    pixel[n] = (pixel[n] & ~1) | int(bin_command[data_index])
                    data_index += 1
                if data_index >= len(bin_command):
                    break
            encoded_img.putpixel((x, y), tuple(pixel))
            if data_index >= len(bin_command):
                break
        if data_index >= len(bin_command):
            break

    encoded_img.save(output_path)
    print(f"Command encoded in image saved as {output_path}")

# Función para extraer un comando de una imagen
def decode_command_from_image(image_path):
    img = Image.open(image_path)
    width, height = img.size
    bin_command = ''

    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            for n in range(3):  # Iterar sobre R, G, B
                bin_command += str(pixel[n] & 1)
                if len(bin_command) % 8 == 0 and bin_command[-8:] == '00000000':
                    bin_command = bin_command[:-8]
                    return ''.join(chr(int(bin_command[i:i+8], 2)) for i in range(0, len(bin_command), 8))

# Función para ejecutar un comando
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Output:\n{result.stdout.decode()}")
        if result.stderr:
            print(f"Errors:\n{result.stderr.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

# Función principal para ejecutar el flujo completo
def main():
    # Pedir permiso explícito
    user_input = input("Este script ejecutará comandos en su dispositivo. ¿Desea continuar? (sí/no): ").strip().lower()
    if user_input != 'sí':
        print("Permiso denegado. Saliendo del script.")
        return

    # Esconder el comando en la imagen
    encode_command_in_image('input_image.png', 'echo Hello, world!', 'encoded_image.png')

    # Extraer el comando de la imagen
    command = decode_command_from_image('encoded_image.png')
    print(f"Decoded command: {command}")

    # Ejecutar el comando
    execute_command(command)

