import tkinter as tk
from tkinter import ttk
import requests
import cv2
import numpy as np
import base64
from PIL import Image, ImageTk


class CinemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cinema Totem App")

        # Variable para almacenar datos de la API
        self.api_url = "http://vps-3701198-x.dattaweb.com:4000"
        self.api_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.DGI_v9bwNm_kSrC-CQSb3dBFzxOlrtBDHcEGXvCFqgU"

        # Variables de seguimiento
        self.cinema_id, self.locations, self.available_seats = self.get_cinema_data()
        self.selected_location = tk.StringVar()
        self.movie_labels = []

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
            movies = response.json()
            movie_id = [movie["id"] for movie in movies]
            poster_id = [movie["poster_id"] for movie in movies]
            release_date = [movie["release_date"] for movie in movies]
            movie_name = [movie["name"] for movie in movies]
            synopsis = [movie["synopsis"] for movie in movies]
            gender = [movie["gender"] for movie in movies]
            duration = [movie["duration"] for movie in movies]
            actors = [movie["actors"] for movie in movies]
            directors = [movie["directors"] for movie in movies]
            rating = [movie["rating"] for movie in movies]
            return movie_id, poster_id, release_date, movie_name, synopsis, gender, duration, actors, directors, rating
        else:
            print("Error al obtener datos de la película desde la API")
            return [], [], [], [], [], [], [], [], [], []

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
            row = i // 13
            column = i % 13
            poster_id = movie
            if poster_id:
                poster_data = self.get_poster_data(poster_id)
                label = self.display_image_cv2(poster_data, row, container, column)
                self.movie_labels.append(label)

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

            return label  # Ensure to return the label

        return None  # Return None if there is no poster_data

    def search_movie(self):
        """
        Realiza la búsqueda de películas y actualiza la visualización.
        """
        search_entry_content = self.search_entry.get()  # Obtén el contenido del Entry de búsqueda
        if search_entry_content:
            filtered_movie_ids = self.filter_movies(search_entry_content)
            self.display_movies(self.movies_frame, filtered_movie_ids)
            self.filtered_movies = True  # Actualiza la variable de control
        else:
            # Si el Entry de búsqueda está vacío, muestra todas las películas
            movies = self.get_cinema_movies_data(1)[0]["has_movies"]
            self.display_movies(self.movies_frame, movies)
            self.filtered_movies = False  # Actualiza la variable de control

    def filter_movies(self, movie_name):
        """
        Filtra las películas por nombre.
        """
        movie_id, movie_names, _ = self.get_movies_data()
        filtered_movies = [movie_id[i] for i, name in enumerate(movie_names) if movie_name.lower() in name.lower()]
        return filtered_movies

    def show_movie_details(self, movie):
        # Implementa la transición a la pantalla secundaria
        pass

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()