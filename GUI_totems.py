from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import io
import base64
from PIL import Image, ImageTk
import qrcode
import os


class AplicacionCine:
    def __init__(self, root):
        self.checkbox_snack = None
        self.root = root
        self.root.title("Cinema Totem App")

        self.idqr = 1
        self.pelicula = ''
        self.ubicaciontotem = ''
        self.cantidad_entradas = 0

        self.asientos = {}

        self.carrito = {}

        # Variable para almacenar datos de la API
        self.api_url = "http://vps-3701198-x.dattaweb.com:4000"
        self.api_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.DGI_v9bwNm_kSrC-CQSb3dBFzxOlrtBDHcEGXvCFqgU"

        self.cine_id, self.ubicaciones, self.sillas_disponibles = self.obtener_datos_cine()
        self.ubicacion_seleccionada = tk.StringVar()
        self.etiquetas_peliculas = []
        self.ubicacion_actual = 1

        self.peliculas_filtradas = False
        self.entrada_busqueda = None

        # Pantalla principal
        self.crear_pantalla_principal()

        self.frame_peliculas = ttk.Frame(self.root)
        self.frame_peliculas.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    def seleccion_cambiada(self, event):
        ubicacion_seleccionada = self.ubicacion_seleccionada.get()
        indice_ubicacion = self.ubicaciones.index(ubicacion_seleccionada)
        cinema_id = self.cine_id[indice_ubicacion]
        self.ubicacion_actual = cinema_id
        peliculas = self.obtener_datos_peliculas_cine(cinema_id)[0]["has_movies"]
        self.mostrar_peliculas(self.frame_peliculas, peliculas)

    def obtener_datos_cine(self):
        headers = {"Authorization": self.api_token}
        respuesta = requests.get(f"{self.api_url}/cinemas", headers=headers)

        if respuesta.status_code == 200:
            cines = respuesta.json()
            cinema_id = [cine["cinema_id"] for cine in cines]
            ubicaciones = [cine["location"] for cine in cines]
            available_seats = [cine["available_seats"] for cine in cines]

            # Set asientos si está vacío
            if not self.asientos:
                self.asientos = dict(zip(ubicaciones, available_seats))
            return cinema_id, ubicaciones, available_seats
        else:
            print("Error al obtener datos desde la API")
            return [], []

    def obtener_datos_peliculas(self):
        headers = {"Authorization": self.api_token}
        respuesta = requests.get(f"{self.api_url}/movies", headers=headers)

        if respuesta.status_code == 200:
            peliculas = respuesta.json()
            id_pelicula = [pelicula["movie_id"] for pelicula in peliculas]
            nombre_pelicula = [pelicula["name"] for pelicula in peliculas]
            id_poster = [pelicula["poster_id"] for pelicula in peliculas]
            return id_pelicula, nombre_pelicula, id_poster
        else:
            print("Error al obtener datos de películas desde la API")
            return [], [], []

    def obtener_datos_pelicula(self, id_pelicula):
        headers = {"Authorization": self.api_token}
        respuesta = requests.get(f"{self.api_url}/movies/{id_pelicula}", headers=headers)

        if respuesta.status_code == 200:
            pelicula = respuesta.json()
            id_pelicula = pelicula.get("id", None)
            id_poster = pelicula.get("poster_id", None)
            fecha_estreno = pelicula.get("release_date", "")
            nombre_pelicula = pelicula.get("name", None)
            sinopsis = pelicula.get("synopsis", None)
            genero = pelicula.get("gender", None)

            # Convertir la duración a entero (suponiendo que siempre está en minutos)
            duracion_bruta = pelicula.get("duration", "0min")
            duracion = int(''.join(filter(str.isdigit, duracion_bruta)))

            actores = pelicula.get("actors", "").split(", ")
            directores = pelicula.get("directors", "").split(", ")
            rating = pelicula.get("rating", None)

            return id_pelicula, id_poster, fecha_estreno, nombre_pelicula, sinopsis, genero, duracion, actores, directores, rating
        else:
            print("Error al obtener datos de la película desde la API")
            return None, None, None, None, None, None, None, None, None, None

    def obtener_datos_poster(self, id_poster):
        headers = {"Authorization": self.api_token}
        respuesta = requests.get(f"{self.api_url}/posters/{id_poster}", headers=headers)

        if respuesta.status_code == 200:
            return respuesta.json()["poster_image"]
        else:
            print(f"Error al obtener datos del póster {id_poster} desde la API")
            return {}

    def obtener_datos_snacks(self):
        headers = {"Authorization": self.api_token}
        respuesta = requests.get(f"{self.api_url}/snacks", headers=headers)

        if respuesta.status_code == 200:
            return respuesta.json()
        else:
            print(f"Error al obtener datos de los snacks desde la API")
            return {}

    def obtener_datos_peliculas_cine(self, cinema_id):
        headers = {"Authorization": self.api_token}
        respuesta = requests.get(f"{self.api_url}/cinemas/{cinema_id}/movies", headers=headers)

        if respuesta.status_code == 200:
            return respuesta.json()
        else:
            print(f"Error al obtener datos del las películas del cine {cinema_id} desde la API")
            return {}

    def crear_pantalla_principal(self):
        label_ubicacion = ttk.Label(self.root, text="Ubicación del totem:")
        combobox_ubicacion = ttk.Combobox(self.root,
                                          state="readonly",
                                          values=self.ubicaciones,
                                          textvariable=self.ubicacion_seleccionada)

        combobox_ubicacion.bind("<<ComboboxSelected>>", self.seleccion_cambiada)

        if self.ubicaciones:
            combobox_ubicacion.set(self.ubicaciones[0])

        label_peliculas = ttk.Label(self.root, text="Cartelera:")
        frame_peliculas = ttk.Frame(self.root)
        peliculas = self.obtener_datos_peliculas_cine(1)[0]["has_movies"]
        self.mostrar_peliculas(frame_peliculas, peliculas)

        label_busqueda = ttk.Label(self.root, text="Buscar película:")
        entrada_busqueda = ttk.Entry(self.root)
        self.entrada_busqueda = entrada_busqueda
        boton_busqueda = ttk.Button(self.root, text="Buscar", command=self.buscar_pelicula)

        label_ubicacion.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        combobox_ubicacion.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        label_peliculas.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        frame_peliculas.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        label_busqueda.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        entrada_busqueda.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        boton_busqueda.grid(row=2, column=2, padx=10, pady=10)

        boton_checkout = ttk.Button(self.root, text="Checkout", command=self.mostrar_pantalla_checkout)
        boton_checkout.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def mostrar_detalles_pelicula(self, id_pelicula):
        datos_pelicula = self.obtener_datos_pelicula(int(id_pelicula))

        pantalla_secundaria = tk.Toplevel(self.root)
        pantalla_secundaria.geometry("650x400")
        pantalla_secundaria.title("Detalles de la Película")

        label_cinema = ttk.Label(pantalla_secundaria, text=f"Sala de proyección: {self.ubicacion_seleccionada.get()}")
        label_cinema.pack(pady=10)

        id_pelicula, id_poster, fecha_estreno, nombre_pelicula, sinopsis, genero, duracion, actores, directores, rating = datos_pelicula
        label_detalles = ttk.Label(pantalla_secundaria, text=f"Detalles de {nombre_pelicula}:")
        label_detalles.pack(pady=10)

        text_widget = scrolledtext.ScrolledText(pantalla_secundaria, wrap=tk.WORD, width=40, height=1)
        text_widget.pack(expand=True, fill="both")

        detalles_texto = f"Sinopsis: {sinopsis}"
        text_widget.insert(tk.END, detalles_texto)
        text_widget.configure(state=tk.DISABLED)

        detalles_texto2 = f"Género: {genero}\nDuración: {duracion} minutos\nActores: {', '.join(actores)}"
        detalles_info = ttk.Label(pantalla_secundaria, text=detalles_texto2, anchor="w")
        detalles_info.pack(pady=10)

        boton_volver = ttk.Button(pantalla_secundaria, text="Volver a pantalla principal",
                                  command=pantalla_secundaria.destroy)
        boton_volver.pack(pady=20)

        boton_reservar = ttk.Button(pantalla_secundaria, text="Reservar", command=lambda: self.reservar(datos_pelicula))
        boton_reservar.pack(pady=10)

    def mostrar_peliculas(self, container, peliculas):
        if self.peliculas_filtradas:
            for etiqueta in self.etiquetas_peliculas:
                etiqueta.grid_forget()
            self.etiquetas_peliculas = []

        for etiqueta in self.etiquetas_peliculas:
            etiqueta.grid_forget()

        self.etiquetas_peliculas = []

        for i, pelicula in enumerate(peliculas):
            row = i // 5
            column = i % 5
            id_poster = pelicula
            if id_poster:
                datos_poster = self.obtener_datos_poster(id_poster)
                etiqueta = self.mostrar_imagen_cv2(datos_poster, row, container, column)
                self.etiquetas_peliculas.append(etiqueta)
                etiqueta.bind("<Button-1>", lambda event, pelicula=id_poster: self.mostrar_detalles_pelicula(pelicula))

    def mostrar_imagen_cv2(self, datos_poster, row, container, column):
        if datos_poster:
            _, image_data = datos_poster.split(",", 1)
            image_data = base64.b64decode(image_data)
            image_tk = ImageTk.PhotoImage(Image.open(io.BytesIO(bytearray(image_data))).resize((100, 150)))

            etiqueta = ttk.Label(container, image=image_tk)
            etiqueta.grid(row=row, column=column, padx=10, pady=5)
            etiqueta.image = image_tk

            return etiqueta

        return None

    def buscar_pelicula(self):
        contenido_busqueda = self.entrada_busqueda.get()
        if contenido_busqueda:
            peliculas_filtradas = self.filtrar_peliculas(contenido_busqueda)
            self.mostrar_peliculas(self.frame_peliculas, peliculas_filtradas)
            self.peliculas_filtradas = True
        else:
            peliculas = self.obtener_datos_peliculas_cine(self.ubicacion_actual)[0]["has_movies"]
            self.mostrar_peliculas(self.frame_peliculas, peliculas)
            self.peliculas_filtradas = False

    def filtrar_peliculas(self, nombre_pelicula):
        id_pelicula, nombres_peliculas, _ = self.obtener_datos_peliculas()
        peliculas_filtradas = [id_pelicula[i] for i, nombre in enumerate(nombres_peliculas) if
                               nombre_pelicula.lower() in nombre.lower()]
        return peliculas_filtradas

    def reservar(self, datos_pelicula):
        if not self.asientos:
            cinema_id, ubicaciones, available_seats = self.obtener_datos_cine()
            self.asientos = dict(zip(ubicaciones, available_seats))

        ubicacion = self.ubicaciones[int(self.ubicacion_actual) - 1]
        if self.asientos[ubicacion] > 0:
            self.pantalla_reservar(datos_pelicula)

    def pantalla_reservar(self, movie_data):
        reserva_screen = tk.Toplevel(self.root)
        reserva_screen.geometry("650x400")
        reserva_screen.title("Reserva de película")

        cantidad_label = ttk.Label(reserva_screen, text="Cantidad de entradas:")
        cantidad_entry = ttk.Entry(reserva_screen)
        cantidad_label.pack()
        cantidad_entry.pack()

        precio_unitario_label = ttk.Label(reserva_screen, text="Valor unitario de cada entrada: $1000")
        precio_unitario_label.pack()

        pelicula = movie_data[3]

        añadir_al_carrito_button = ttk.Button(reserva_screen, text="Agregar al carrito",
                                              command=lambda: self.añadir_al_carrito(cantidad_entry.get(), 1000, pelicula))
        añadir_al_carrito_button.pack()

        añadir_snack_button = ttk.Button(reserva_screen, text="Añadir Snack", command=self.mostrar_snacks)
        añadir_snack_button.pack()

    def añadir_al_carrito(self, cantidad, precio_unitario, pelicula):
        self.pelicula = pelicula
        try:
            cantidad = int(cantidad)
            precio_unitario = float(precio_unitario)
            precio_total = cantidad * precio_unitario

            if "Entradas" in self.carrito:
                self.carrito["Entradas"] += cantidad
            else:
                self.carrito["Entradas"] = cantidad
            print(f"Se añadieron {cantidad} tickets al carrito. Precio total: {precio_total}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos para la cantidad y el precio unitario.")

    def mostrar_snacks(self):
        snacks_data = self.obtener_datos_snacks()

        snacks_screen = tk.Toplevel(self.root)
        snacks_screen.title("Añadir Snack al Carrito")

        snack_entries = {}
        for snack, precio in snacks_data.items():
            label_text = f"{snack}: {precio} pesos"
            ttk.Label(snacks_screen, text=label_text).pack()

            cantidad_entry = ttk.Entry(snacks_screen)
            cantidad_entry.pack()

            snack_entries[snack] = cantidad_entry

        añadir_snacks_al_carrito_button = ttk.Button(snacks_screen, text="Agregar al carrito",
                                                     command=lambda: self.añadir_snacks_al_carrito(snack_entries, snacks_screen))
        añadir_snacks_al_carrito_button.pack()

    def añadir_snacks_al_carrito(self, snack_entries, snacks_screen):
        for snack, entry in snack_entries.items():
            cantidad = entry.get()
            if cantidad:
                cantidad = int(cantidad)
                self.carrito[snack] = cantidad

        print("Added snacks to the cart:", self.carrito)

        snacks_screen.destroy()

    def mostrar_pantalla_checkout(self):
        checkout_screen = tk.Toplevel(self.root)
        checkout_screen.title("Carrito")

        ttk.Label(checkout_screen, text="Detalle de la compra").pack(pady=10)

        total_price = 0

        for item_id, quantity in self.carrito.items():
            if item_id != 'Entradas':
                item_details = self.obtener_datos_snacks().get(item_id)
                if item_details:
                    item_price = float(item_details)
                else:
                    item_price = 0.0
            else:
                item_price = 1000.0

            item_total_price = quantity * item_price
            total_price += item_total_price

            ttk.Label(checkout_screen,
                      text=f"{item_id}: {quantity}x ${item_price:.2f} = ${item_total_price:.2f}").pack()

        ttk.Label(checkout_screen, text=f"Total: ${total_price:.2f}").pack()
        if "Entradas" in self.carrito and self.carrito["Entradas"]:
            self.cantidad_entradas = self.carrito["Entradas"]

        self.ubicaciontotem = self.ubicaciones[int(self.ubicacion_actual) - 1]

        pagar_button = ttk.Button(checkout_screen, text="Pagar", command=lambda: self.generar_QR(checkout_screen))
        pagar_button.pack()

    def obtener_detalle_de_items(self, item_id):
        if item_id == 'Entradas':
            return {"name": "Entradas de Cine", "price": 1000.0}

        snack_data = self.obtener_datos_snacks().get(item_id)
        if snack_data:
            item_price = float(snack_data)
        else:
            item_price = 0.0

        return {"name": item_id, "price": item_price}

    def generar_QR(self, checkout_screen):
        png_file = os.path.join('QR', f'{self.idqr}.png')

        pdf_file = os.path.join('QR', f'{self.idqr}.pdf')

        name = f"{self.idqr} + {self.pelicula} + {self.ubicaciontotem} + {self.cantidad_entradas} + {datetime.timestamp(datetime.now())}"

        image = qrcode.make(name)

        image.save(png_file)

        Image.open(png_file).convert("RGB").save(pdf_file)

        print(f"QR generado y guardado en: {pdf_file}")
        self.idqr += 1

        checkout_screen.destroy()

        self.carrito = {}


# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionCine(root)
    root.mainloop()
