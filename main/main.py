import tkinter as tk
from tkinter import filedialog, messagebox
import json

from app.app import App
from models.tree import AVLTree
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class graphicInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego Carrito con AVL")

        self.tree = AVLTree()
        self.app = None

        # ===== Botones principales =====
        frame = tk.Frame(root)
        frame.pack(pady=10)

        btn_load = tk.Button(frame, text="Cargar JSON", command=self.load_json)
        btn_load.grid(row=0, column=0, padx=5)

        btn_start = tk.Button(frame, text="Iniciar Juego", command=self.start_game)
        btn_start.grid(row=0, column=1, padx=5)

        btn_tree = tk.Button(frame, text="Ver AVL", command=self.show_tree)
        btn_tree.grid(row=0, column=2, padx=5)

        # ===== Canvas para el juego =====
        self.canvas = tk.Canvas(root, width=800, height=300, bg="white")
        self.canvas.pack()

    # ---------- JSON ----------
    def load_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, "r") as f:
                data = json.load(f)
                self.app = App(data["config"], self.tree)
                self.app.load_obstacles(data["obstacles"])
            messagebox.showinfo("Éxito", "Configuración y obstáculos cargados.")

    # ---------- Juego ----------
    def start_game(self):
        if not self.app:
            messagebox.showwarning("Atención", "Primero cargue un archivo JSON.")
            return
        self.game_loop()

    def game_loop(self):
        if self.app.car.x < self.app.road_length and self.app.car.energy > 0:
            self.app.update_game()
            self.draw_game()
            self.root.after(self.app.refresh_time, self.game_loop)
        else:
            messagebox.showinfo("Juego terminado", "Fin del juego")

    def draw_game(self):
        self.canvas.delete("all")

        # Dibujar carretera
        self.canvas.create_line(0, 250, 800, 250, fill="black", width=3)

        # Dibujar carro
        car_x = 50
        car_y = 250 - self.app.car.y * 80
        self.canvas.create_rectangle(
            car_x, car_y - 20, car_x + 40, car_y + 20, fill=self.app.car.color
        )

        # Obstáculos visibles
        visibles = self.tree.range_query(
            self.tree.root,
            self.app.car.x,
            self.app.car.x + 200,  # rango de pantalla
            0,
            2,
        )

        for obs in visibles:
            ox, oy = obs.value
            screen_x = 50 + (ox - self.app.car.x)  # carro fijo en x=50
            screen_y = 250 - oy * 80
            self.canvas.create_rectangle(
                screen_x, screen_y - 20, screen_x + 30, screen_y + 20, fill="red"
            )

        # Energía
        self.canvas.create_text(700, 20, text=f"Energía: {self.app.car.energy}%", fill="blue")

    # ---------- Mostrar AVL ----------
    def show_tree(self):
        if not self.tree.root:
            messagebox.showwarning("Atención", "El árbol está vacío.")
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.set_title("Árbol AVL de Obstáculos")
        ax.axis("off")

        def draw(node, x, y, dx):
            if not node:
                return
            ax.text(x, y, f"{node.value}", ha="center", va="center",
                    bbox=dict(boxstyle="round", facecolor="lightblue"))
            if node.left:
                ax.plot([x, x - dx], [y - 1, y - 2], "k-")
                draw(node.left, x - dx, y - 2, dx / 2)
            if node.right:
                ax.plot([x, x + dx], [y - 1, y - 2], "k-")
                draw(node.right, x + dx, y - 2, dx / 2)

        draw(self.tree.root, 0, 0, 4)

        win = tk.Toplevel(self.root)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# --------- Lanzar interfaz ---------
if __name__ == "__main__":
    root = tk.Tk()
    gui = graphicInterface(root)
    root.mainloop()