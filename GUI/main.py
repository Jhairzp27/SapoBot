import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import shutil
import sys

def resource_path(relative_path):
    """
    Devuelve la ruta completa al recurso, ya sea desde el directorio temporal de PyInstaller o desde el directorio actual.
    """
    try:
        base_path = sys._MEIPASS  # Ruta temporal creada por PyInstaller
    except Exception:
        base_path = os.path.abspath(".")  # Ruta del directorio actual si no se está ejecutando desde PyInstaller
    return os.path.join(base_path, relative_path)

class Window:
    def __init__(self, master):
        """
        Inicializa la ventana principal, configura los paneles y llama a la función para mostrar el Dashboard.
        """
        self.master = master
        self.master.title("De estudiantes para estudiantes")
        self.master.geometry("1200x700")  # Tamaño inicial de la ventana
        self.master.resizable(True, True)  # Permitir redimensionar la ventana

        # Definir colores
        self.COLOR_BARRA_SUPERIOR = "#1f2329"
        self.COLOR_MENU_LATERAL = "#2a3138"
        self.COLOR_CUERPO_PRINCIPAL = "#f1faff"

        # Crear paneles
        self.paneles()

        # Cargar imagen de perfil
        self.profile_img = Image.open(resource_path("Perfil.png"))
        self.profile_img = self.profile_img.resize((220, 170))  # Redimensionar imagen
        self.profile_photo = ImageTk.PhotoImage(self.profile_img)
        
        # Configurar perfil y botones del menú lateral
        self.profile_label = tk.Label(self.menu_lateral, image=self.profile_photo, bg=self.COLOR_MENU_LATERAL, bd=0)
        self.profile_label.pack(pady=20, padx=10)  # Añadir imagen al menú lateral

        # Definir información de los botones del menú lateral
        buttons_info = [
            ("Dashboard", "📊", self.showDashboard),
            ("Profile", "👤", self.showProfile),
            ("Repositorio", "📁", self.showRepositorio),
            ("Info", "ℹ️", self.showInfo),
            ("Settings", "⚙️", self.showSettings)
        ]

        # Crear botones en el menú lateral
        for text, icon, command in buttons_info:
            button = tk.Button(
                self.menu_lateral, 
                text=text, 
                command=command, 
                font=("Arial", 16),  # Ajusta el tamaño de la fuente si es necesario
                bg="#34495E", 
                fg="white", 
                bd=0, 
                relief=tk.FLAT, 
                anchor="w", 
                padx=25,  # Ajusta el relleno horizontal interno
                pady=15,  # Ajusta el relleno vertical interno
                width=24,  # Ajusta el ancho del botón
                height=2    # Ajusta la altura del botón
            )
            button.pack(fill=tk.X, pady=10, padx=10)  # Ajusta el padding externo si es necesario

        # Mostrar vista inicial
        self.showDashboard()

    def paneles(self):
        """
        Crear paneles: barra superior, menú lateral y cuerpo principal.
        """
        # Crear barra superior
        self.barra_superior = tk.Frame(self.master, bg=self.COLOR_BARRA_SUPERIOR, height=50)
        self.barra_superior.pack(side=tk.TOP, fill='x')

        # Crear menú lateral
        self.menu_lateral = tk.Frame(self.master, bg=self.COLOR_MENU_LATERAL, width=250, padx=10, pady=10)  # Ajustar el ancho del menú lateral
        self.menu_lateral.pack(side=tk.LEFT, fill='y')

        # Crear cuerpo principal
        self.cuerpo_principal = tk.Frame(self.master, bg=self.COLOR_CUERPO_PRINCIPAL)
        self.cuerpo_principal.pack(side=tk.RIGHT, fill='both', expand=True)

    def clearContent(self):
        """
        Limpia todos los widgets en el frame del cuerpo principal para actualizar la vista.
        """
        for widget in self.cuerpo_principal.winfo_children():
            widget.destroy()

    def showDashboard(self):
        """
        Muestra el Dashboard con una imagen de fondo que se ajusta al tamaño del cuerpo principal.
        """
        self.clearContent()
        
        # Configura el fondo para la vista Dashboard
        self.bg_img = Image.open(resource_path("fondo_dashboard.png"))
        self.bg_img = self.bg_img.resize((self.cuerpo_principal.winfo_width(), self.cuerpo_principal.winfo_height()), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(self.bg_img)
        self.bg_label = tk.Label(self.cuerpo_principal, image=self.bg_img, bg=self.COLOR_CUERPO_PRINCIPAL)
        self.bg_label.place(relwidth=1, relheight=1)  # La imagen de fondo se coloca para ocupar toda el área del cuerpo principal
        
        self.master.bind("<Configure>", self.updateBackground)
        
    def updateBackground(self, event=None):
        """
        Actualiza la imagen de fondo cuando cambia el tamaño de la ventana.
        """
        if hasattr(self, 'bg_label') and self.bg_label.winfo_exists():
            self.bg_img = Image.open(resource_path("fondo_dashboard.png"))
            self.bg_img = self.bg_img.resize((self.cuerpo_principal.winfo_width(), self.cuerpo_principal.winfo_height()), Image.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(self.bg_img)
            self.bg_label.config(image=self.bg_img)

    def showProfile(self):
        """
        Muestra la vista del perfil.
        """
        self.clearContent()
        tk.Label(self.cuerpo_principal, text="Profile View", font=("Arial", 24), bg=self.COLOR_CUERPO_PRINCIPAL).pack(expand=True)

    def showRepositorio(self):
        """
        Muestra la vista de Repositorio con botones organizados en una cuadrícula 3x3.
        """
        self.clearContent()
        
        # Frame para los botones de Repositorio
        repo_frame = tk.Frame(self.cuerpo_principal, bg="white", padx=10, pady=10)
        repo_frame.pack(fill=tk.BOTH, expand=True)

        titles_colors = [
            ("Probabilidad y Estadística", "#FF9999", "2023B-Prob-Exa1_GR4SW[1].pdf"),
            ("Cálculo en una Variable", "#99FF99", "Cálculo Sistemas - 1 BIM.pdf"),
            ("Álgebra Lineal", "#9999FF", "EXERCISES ING.SANDOVAL_06-07-2022.pdf"),
            ("Mecánica Newtoniana", "#FFCC99", "Correccion_Prueba_1_MN_2022A.pdf"),
            ("Ecuaciones Diferenciales y Ordinarias", "#CC99FF", "ejercicios_edo.pdf"),
            ("Fundamentos de Electrónica", "#FFFF99", "FORMULARIO BOOLE.pdf")
        ]

        # Añade los botones en una cuadrícula 3x3
        for i, (title, color, pdf_name) in enumerate(titles_colors):
            button = tk.Button(repo_frame, text=title, bg=color, font=("Arial", 12), command=lambda t=title, p=pdf_name: self.showDetailView(t, p), relief=tk.RAISED, bd=2)
            button.grid(row=i//3, column=i%3, sticky="nsew", padx=5, pady=5)
        
        # Configura el peso de las filas y columnas
        for i in range(3):
            repo_frame.grid_rowconfigure(i, weight=1)
            repo_frame.grid_columnconfigure(i, weight=1)

    def showDetailView(self, title, pdf_name):
        """
        Muestra la vista detallada de un título seleccionado con opciones para descargar el PDF y regresar.
        """
        self.clearContent()
        
        # Añade la vista detallada
        tk.Label(self.cuerpo_principal, text=title, font=("Arial", 24), bg=self.COLOR_CUERPO_PRINCIPAL).pack(pady=20)

        # Imagen específica para "Probabilidad y Estadística"
        if title == "Probabilidad y Estadística":
            try:
                image = Image.open(resource_path("foto_probabilidad1.png"))
                image = image.resize((400, 300))  # Ajusta el tamaño de la imagen
                self.photo = ImageTk.PhotoImage(image)
                tk.Label(self.cuerpo_principal, image=self.photo, bg=self.COLOR_CUERPO_PRINCIPAL).pack()
            except FileNotFoundError:
                tk.Label(self.cuerpo_principal, text="Imagen no encontrada", font=("Arial", 16), bg=self.COLOR_CUERPO_PRINCIPAL).pack()
        
        # Botón Descargar
        tk.Button(self.cuerpo_principal, text="Descargar PDF", command=lambda: self.downloadPDF(pdf_name)).pack(pady=10)

        # Botón Regresar
        tk.Button(self.cuerpo_principal, text="Regresar", command=self.showRepositorio).pack(pady=10)

    def downloadPDF(self, pdf_name):
        """
        Descarga el archivo PDF desde la ruta del proyecto al directorio de descargas del usuario.
        """
        pdf_path = resource_path(pdf_name)
        if os.path.exists(pdf_path):
            shutil.copy(pdf_path, os.path.join(os.path.expanduser("~"), "Downloads", pdf_name))
            messagebox.showinfo("Descarga Completa", f"El archivo {pdf_name} ha sido descargado exitosamente.")
        else:
            messagebox.showerror("Error", f"No se encontró el archivo {pdf_name}.")

    def showInfo(self):
        """
        Muestra la vista de información.
        """
        self.clearContent()
        tk.Label(self.cuerpo_principal, text="Info View", font=("Arial", 24), bg=self.COLOR_CUERPO_PRINCIPAL).pack(expand=True)

    def showSettings(self):
        """
        Muestra la vista de configuración.
        """
        self.clearContent()
        tk.Label(self.cuerpo_principal, text="Settings View", font=("Arial", 24), bg=self.COLOR_CUERPO_PRINCIPAL).pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = Window(root)
    root.mainloop()
