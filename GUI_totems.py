import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import cv2
import numpy as np
import base64
from PIL import Image, ImageTk
import qrcode


class CinemaApp:
    def __init__(self, root):
        self.snack_checkbox = None
        self.root = root
        self.root.title("Cinema Totem App")

        # Declare asientos as a class attribute
        self.asientos = {}

        self.carrito = {}

        # Variable para almacenar datos de la API
        self.api_url = "http://vps-3701198-x.dattaweb.com:4000"
        self.api_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.DGI_v9bwNm_kSrC-CQSb3dBFzxOlrtBDHcEGXvCFqgU"

        # Variables de seguimiento
        self.cinema_id, self.locations, self.available_seats = self.get_cinema_data()
        self.selected_location = tk.StringVar()
        self.movie_labels = []
        self.actual_location = 1

        self.filtered_movies = False
        self.search_entry = None

        # Pantalla principal
        self.create_main_screen()

        self.movies_frame = ttk.Frame(self.root)
        self.movies_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    def selection_changed(self, event):
        selected_location = self.selected_location.get()
        location_index = self.locations.index(selected_location)
        cinema_id = self.cinema_id[location_index]
        self.actual_location= cinema_id
        movies = self.get_cinema_movies_data(cinema_id)[0]["has_movies"]
        self.display_movies(self.movies_frame, movies)


    def get_cinema_data(self):
        headers = {"Authorization": self.api_token}
        response = requests.get(f"{self.api_url}/cinemas", headers=headers)

        if response.status_code == 200:
            cinemas = response.json()
            cinema_id = [cinema["cinema_id"] for cinema in cinemas]
            locations = [cinema["location"] for cinema in cinemas]
            available_seats = [cinema["available_seats"] for cinema in cinemas]

            # Set asientos if it's empty
            if not self.asientos:
                self.asientos = dict(zip(locations, available_seats))
            return cinema_id, locations, available_seats
        else:
            # Manejar el error según sea necesario
            print("Error al obtener datos desde la API")
            return [], []

    def get_movies_data(self):
        headers = {"Authorization": self.api_token}
        response = requests.get(f"{self.api_url}/movies", headers=headers)

        if response.status_code == 200:
            movies = response.json()
            movie_id = [movie["movie_id"] for movie in movies]
            movie_name = [movie["name"] for movie in movies]
            poster_id = [movie["poster_id"] for movie in movies]
            return movie_id, movie_name, poster_id
        else:
            print("Error al obtener datos de películas desde la API")
            return [], [], []

    def get_movie_data(self, movie_id):
        headers = {"Authorization": self.api_token}
        response = requests.get(f"{self.api_url}/movies/{movie_id}", headers=headers)

        if response.status_code == 200:
            movie = response.json()
            movie_id = movie.get("id", None)
            poster_id = movie.get("poster_id", None)
            release_date = movie.get("release_date", "")
            movie_name = movie.get("name", None)
            synopsis = movie.get("synopsis", None)
            gender = movie.get("gender", None)

            # Convert duration to integer (assuming it's always in minutes)
            duration_raw = movie.get("duration", "0min")
            duration = int(''.join(filter(str.isdigit, duration_raw)))

            actors = movie.get("actors", "").split(", ")
            directors = movie.get("directors", "").split(", ")
            rating = movie.get("rating", None)

            return movie_id, poster_id, release_date, movie_name, synopsis, gender, duration, actors, directors, rating
        else:
            print("Error al obtener datos de la película desde la API")
            return None, None, None, None, None, None, None, None, None, None

    def get_poster_data(self, poster_id):
        headers = {"Authorization": self.api_token}
        response = requests.get(f"{self.api_url}/posters/{poster_id}", headers=headers)

        if response.status_code == 200:
            return response.json()["poster_image"]
        else:
            # Manejar el error según sea necesario
            print(f"Error al obtener datos del póster {poster_id} desde la API")
            return {}

    def get_snack_data(self):
        headers = {"Authorization": self.api_token}
        response = requests.get(f"{self.api_url}/snacks", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            # Manejar el error según sea necesario
            print(f"Error al obtener datos de los snacks desde la API")
            return {}

    def get_movies_cinema_data(self, movie_id):
        headers = {"Authorization": self.api_token}
        response = requests.get(f"{self.api_url}/movies/{movie_id}/cinemas", headers=headers)

        if response.status_code == 200:
            cinemas = response.json()
            cinema_id = [cinema["cinema_id"] for cinema in cinemas]
            has_movies = [cinema["has_movies"] for cinema in cinemas]
            return cinema_id, has_movies
        else:
            # Manejar el error según sea necesario
            print(f"Error al obtener datos del los cines de la pelicula {movie_id} desde la API")
            return {}

    def get_cinema_movies_data(self, cinema_id):
        headers = {"Authorization": self.api_token}
        response = requests.get(f"{self.api_url}/cinemas/{cinema_id}/movies", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            # Manejar el error según sea necesario
            print(f"Error al obtener datos del las pelicuas del cine {cinema_id} desde la API")
            return {}

    def create_main_screen(self):
        location_label = ttk.Label(self.root, text="Ubicación del totem:")
        location_combobox = ttk.Combobox(self.root,
                                         state="readonly",
                                         values=self.locations,
                                         textvariable=self.selected_location)

        location_combobox.bind("<<ComboboxSelected>>", self.selection_changed)

        if self.locations:
            location_combobox.set(self.locations[0])

        movies_label = ttk.Label(self.root, text="Cartelera:")
        movies_frame = ttk.Frame(self.root)
        movies = self.get_cinema_movies_data(1)[0]["has_movies"]
        self.display_movies(movies_frame, movies)

        search_label = ttk.Label(self.root, text="Buscar película:")
        search_entry = ttk.Entry(self.root)
        self.search_entry = search_entry
        search_button = ttk.Button(self.root, text="Buscar", command=self.search_movie)

        # Diseño de la pantalla principal
        location_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        location_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        movies_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        movies_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        search_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        search_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        search_button.grid(row=2, column=2, padx=10, pady=10)

        checkout_button = ttk.Button(self.root, text="Checkout", command=self.show_checkout_screen)
        checkout_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def show_movie_details(self, movie_id):
        # Obtener datos de la película
        movie_data = self.get_movie_data(int(movie_id))

        # Crear la pantalla secundaria
        secondary_screen = tk.Toplevel(self.root)
        secondary_screen.geometry("650x400")
        secondary_screen.title("Detalles de la Película")

        # Mostrar sala de proyección
        cinema_label = ttk.Label(secondary_screen, text=f"Sala de proyección: {self.selected_location.get()}")
        cinema_label.pack(pady=10)

        # Mostrar sinopsis, duración, actores y género
        movie_id, poster_id, release_date, movie_name, synopsis, gender, duration, actors, directors, rating = movie_data
        details_label = ttk.Label(secondary_screen, text=f"Detalles de {movie_name}:")
        details_label.pack(pady=10)

        # Create a scrolled text widget
        text_widget = scrolledtext.ScrolledText(secondary_screen, wrap=tk.WORD, width=40, height=1)
        text_widget.pack(expand=True, fill="both")

        details_text = f"Sinopsis: {synopsis}"
        text_widget.insert(tk.END, details_text)
        text_widget.configure(state=tk.DISABLED)

        details_text2 = f"Género: {gender}\nDuración: {duration} minutos\nActores: {', '.join(actors)}"
        details_info = ttk.Label(secondary_screen, text=details_text2, anchor="w")
        details_info.pack(pady=10)

        # Botón para volver a la pantalla principal
        back_button = ttk.Button(secondary_screen, text="Volver a pantalla principal", command=secondary_screen.destroy)
        back_button.pack(pady=20)

        # Boton de reservar
        reservar_button = ttk.Button(secondary_screen, text="Reservar", command=self.reservar)
        reservar_button.pack(pady=10)

    def display_movies(self, container, movies):
        # Lógica existente para ocultar las películas en caso de búsqueda
        if self.filtered_movies:
            for label in self.movie_labels:
                label.grid_forget()
            self.movie_labels = []

        # Hide existing posters in the container
        for label in self.movie_labels:
            label.grid_forget()

        self.movie_labels = []  # Clear the list of movie labels

        for i, movie in enumerate(movies):
            # Calculate row and column based on index
            row = i // 5
            column = i % 5
            poster_id = movie
            if poster_id:
                poster_data = self.get_poster_data(poster_id)
                label = self.display_image_cv2(poster_data, row, container, column)
                self.movie_labels.append(label)

                # Bind the callback function to the label
                label.bind("<Button-1>", lambda event, movie=poster_id: self.show_movie_details(movie))

    def display_image_cv2(self, poster_data, row, container, column):
        if poster_data:
            _, image_data = poster_data.split(",", 1)
            image_data = base64.b64decode(image_data)
            image_np = np.frombuffer(image_data, np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            resized_image = cv2.resize(image_cv2, (100, 150))

            # Create a PhotoImage object from the image_cv2
            image_tk = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
            image_tk = ImageTk.PhotoImage(image_tk)

            # Display the image using Label
            label = ttk.Label(container, image=image_tk)
            label.grid(row=row, column=column, padx=10, pady=5)
            label.image = image_tk

            return label

        return None

    def search_movie(self):
        """
        Realiza la búsqueda de películas y actualiza la visualización.
        """
        search_entry_content = self.search_entry.get()  # Obtén el contenido del Entry de búsqueda
        if search_entry_content:
            filtered_movie_ids = self.filter_movies(search_entry_content)
            self.display_movies(self.movies_frame, filtered_movie_ids)
            self.filtered_movies = True
        else:
            # Si el Entry de búsqueda está vacío, muestra todas las películas
            movies = self.get_cinema_movies_data(self.actual_location)[0]["has_movies"]
            self.display_movies(self.movies_frame, movies)
            self.filtered_movies = False  # Actualiza la variable de control

    def filter_movies(self, movie_name):
        """
        Filtra las películas por nombre.
        """
        movie_id, movie_names, _ = self.get_movies_data()
        filtered_movies = [movie_id[i] for i, name in enumerate(movie_names) if movie_name.lower() in name.lower()]
        return filtered_movies

    def reservar(self):
        # Check if asientos is empty, and initialize it if necessary
        if not self.asientos:
            cinema_id, locations, available_seats = self.get_cinema_data()
            self.asientos = dict(zip(locations, available_seats))

        ubicacion = self.locations[int(self.actual_location) - 1]
        if self.asientos[ubicacion]>0:
            self.pantalla_reservar()
        pass

    def pantalla_reservar(self):
        # Create the reservation screen
        reserva_screen = tk.Toplevel(self.root)
        reserva_screen.geometry("650x400")
        reserva_screen.title("Reserva de película")

        # Entry widgets for ticket details
        quantity_label = ttk.Label(reserva_screen, text="Cantidad de entradas:")
        quantity_entry = ttk.Entry(reserva_screen)
        quantity_label.pack()
        quantity_entry.pack()

        unit_price_label = ttk.Label(reserva_screen, text="Valor unitario de cada entrada: $1000")
        unit_price_label.pack()


        # Button to add ticket details to the cart
        add_to_cart_button = ttk.Button(reserva_screen, text="Agregar al carrito",
                                        command=lambda: self.add_to_cart(quantity_entry.get(), 1000))
        add_to_cart_button.pack()

        # Button to add snacks to the cart
        add_snack_button = ttk.Button(reserva_screen, text="Añadir Snack", command=self.show_snacks)
        add_snack_button.pack()

    def add_to_cart(self, quantity, unit_price):
        try:
            quantity = int(quantity)
            unit_price = float(unit_price)
            total_price = quantity * unit_price

            if "Entradas" in self.carrito:
                self.carrito["Entradas"] += quantity
            else:
                self.carrito["Entradas"] = quantity
            print(f"Added {quantity} tickets to the cart. Total price: {total_price}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos para la cantidad y el precio unitario.")

    def show_snacks(self):
        # Retrieve snack data from the API (use your existing API request logic)
        snacks_data = self.get_snack_data()

        # Create a new window to display snack options
        snacks_screen = tk.Toplevel(self.root)
        snacks_screen.title("Añadir Snack al Carrito")

        # Create Entry widgets for each snack along with their prices
        snack_entries = {}
        for snack, price in snacks_data.items():
            label_text = f"{snack}: {price} pesos"
            ttk.Label(snacks_screen, text=label_text).pack()

            # Entry widget for quantity
            quantity_entry = ttk.Entry(snacks_screen)
            quantity_entry.pack()

            snack_entries[snack] = quantity_entry

        # Button to add entered quantities to the cart
        add_snacks_to_cart_button = ttk.Button(snacks_screen, text="Agregar al carrito",
                                               command=lambda: self.add_snacks_to_cart(snack_entries, snacks_screen))
        add_snacks_to_cart_button.pack()

    def add_snacks_to_cart(self, snack_entries, snacks_screen):
        for snack, entry in snack_entries.items():
            quantity = entry.get()
            if quantity:
                quantity = int(quantity)
                self.carrito[snack] = quantity

        print("Added snacks to the cart:", self.carrito)

        # Destroy the snacks screen
        snacks_screen.destroy()

    def show_checkout_screen(self):
        checkout_screen = tk.Toplevel(self.root)
        checkout_screen.title("Carrito")

        # Create labels to display cart contents
        ttk.Label(checkout_screen, text="Detalle de la compra").pack(pady=10)

        total_price = 0  # Variable to calculate the total price

        # Iterate through items in the cart
        for item_id, quantity in self.carrito.items():
            # For snacks, fetch the price dynamically
            if item_id != 'Entradas':
                item_details = self.get_snack_data().get(item_id)
                if item_details:
                    item_price = float(item_details)
                else:
                    # Handle the case where the price is not available
                    item_price = 0.0
            else:
                # For 'Entradas', use a fixed price since it's not in the snack data
                item_price = 1000.0

            # Calculate the price for the quantity
            item_total_price = quantity * item_price
            total_price += item_total_price

            # Display item details in the checkout screen
            ttk.Label(checkout_screen, text=f"{item_id}: {quantity}x ${item_price:.2f} = ${item_total_price:.2f}").pack()

        # Display the total price rounded to two decimal places
        ttk.Label(checkout_screen, text=f"Total: ${total_price:.2f}").pack()

        pagar_button = ttk.Button(checkout_screen, text="Pagar", command=lambda: self.generar_QR())
        pagar_button.pack()

    def get_item_details(self, item_id):
        # Placeholder for item details (replace this with your actual data structure)
        if item_id == 'Entradas':
            return {"name": "Entradas de Cine", "price": 1000.0}

        # For snacks, fetch the price dynamically
        snack_data = self.get_snack_data().get(item_id)
        if snack_data:
            item_price = float(snack_data)
        else:
            # Handle the case where the price is not available
            item_price = 0.0

        return {"name": item_id, "price": item_price}

    def generar_QR(self):
        image = qrcode.make("La data de la compra")
        image.save("QR-Compra " + "numero" + ".png")

        image_1 = Image.open(r'QR-Compra numero.png')
        im_1 = image_1.convert('RGB')
        im_1.save(r'QR-Compra numero.pdf')


# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()