import tkinter as tk
from tkinter import filedialog
import json

from app.app import App
from models.tree import AVLTree

class graphicInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego Carrito con AVL")
        self.tree = AVLTree()
        self.app = None

        # Botones principales
        btn_load = tk.Button(root, text="Cargar JSON", command=self.load_json)
        btn_load.pack()

        btn_start = tk.Button(root, text="Iniciar Juego", command=self.start_game)
        btn_start.pack()

    def load_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "r") as f:
                data = json.load(f)
                self.app = App(data["config"], self.tree)
                self.app.load_obstacles(data["obstacles"])
            print("Configuración y obstáculos cargados.")

    def start_game(self):
        if not self.app:
            print("Primero cargue un archivo JSON.")
            return
        self.game_loop()

    def game_loop(self):
        if self.app.car.x < self.app.road_length and self.app.car.energy > 0:
            self.app.update_game()
            print(f"Carro en x={self.app.car.x}, energía={self.app.car.energy}")
            self.root.after(self.app.refresh_time, self.game_loop)
        else:
            print("Juego terminado.")