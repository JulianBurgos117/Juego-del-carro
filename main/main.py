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
        
        btn_load = tk.Button(frame, text="Insertar Obstacles", command=self.insert_node)
        btn_load.grid(row=0, column=1, padx=5)

        btn_start = tk.Button(frame, text="Iniciar Juego", command=self.start_game)
        btn_start.grid(row=0, column=2, padx=5)

        btn_tree = tk.Button(frame, text="Ver AVL", command=self.show_tree)
        btn_tree.grid(row=0, column=3, padx=5)

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

    def insert_node(self):
        if not self.app:
            messagebox.showwarning("Atención", "Primero cargue la configuración del juego.")
            return

        # Ejemplo simple: insertar un obstáculo en la posición 150, carril 1
        x = 150
        y = 1
        tipo = "rojo"

        self.app.insert_obstacle(x, y, tipo)
        messagebox.showinfo("Éxito", f"Obstáculo insertado en x={x}, y={y}, tipo={tipo}")

    # ---------- Game ----------
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

    # ---------- Show AVL ----------
    def show_tree(self):
        if not self.tree.root:
            messagebox.showwarning("Atención", "El árbol está vacío.")
            return

        # 1) calcular posiciones usando recorrido in-order (x = orden in-order, y = profundidad)
        positions = {}   # nodo -> (x_index, depth)
        counter = {"x": 0, "max_depth": 0}

        def inorder(node, depth=0):
            if not node:
                return
            inorder(node.left, depth + 1)
            positions[node] = (counter["x"], depth)
            counter["x"] += 1
            counter["max_depth"] = max(counter["max_depth"], depth)
            inorder(node.right, depth + 1)

        inorder(self.tree.root)

        # 2) crear figura con tamaño dinámico
        n_nodes = max(1, counter["x"])
        max_depth = max(1, counter["max_depth"] + 1)
        width = max(6, n_nodes * 0.7)
        height = max(4, max_depth * 1.2)

        fig, ax = plt.subplots(figsize=(width, height))
        ax.set_title("Árbol AVL de Obstáculos")
        ax.axis("off")

        # 3) escalar posiciones
        spacing_x = 2.0
        spacing_y = 2.5
        scaled = {}
        for node, (xi, depth) in positions.items():
            x = xi * spacing_x
            y = -depth * spacing_y
            scaled[node] = (x, y)

        # 4) dibujar aristas (todas mismo color)
        for node, (x, y) in scaled.items():
            if getattr(node, "left", None) and node.left in scaled:
                xl, yl = scaled[node.left]
                ax.plot([x, xl], [y, yl], color="gray", linewidth=1, zorder=1)
            if getattr(node, "right", None) and node.right in scaled:
                xr, yr = scaled[node.right]
                ax.plot([x, xr], [y, yr], color="gray", linewidth=1, zorder=1)

        # 5) dibujar nodos como círculos + info + balance
        for node, (x, y) in scaled.items():
            val = getattr(node, "value", None)
            tipo = getattr(node, "tipo", None) or getattr(node, "tipe", None) or ""
            balance = getattr(node, "balance", None)

            # Texto principal (coordenadas + tipo)
            if isinstance(val, (list, tuple)):
                if len(val) == 4:
                    label = f"{val[0]},{val[1]} - {val[2]},{val[3]}\n{tipo}"
                elif len(val) == 2:
                    label = f"{val[0]},{val[1]}\n{tipo}"
                else:
                    label = str(val) + ("\n" + str(tipo) if tipo else "")
            else:
                label = str(val) + ("\n" + str(tipo) if tipo else "")

            # Agregar balance factor (BF)
            if balance is not None:
                label += f"\nBF={balance}"

            # Dibujar círculo
            circle = plt.Circle((x, y), radius=0.6, edgecolor="black",
                                facecolor="lightblue", zorder=2)
            ax.add_patch(circle)

            # Texto dentro del círculo
            ax.text(x, y, label, ha="center", va="center", fontsize=8, zorder=3)

        # 6) ajustar límites y mostrar en Toplevel
        xs = [p[0] for p in scaled.values()]
        ys = [p[1] for p in scaled.values()]
        if xs and ys:
            margin_x = spacing_x
            margin_y = spacing_y
            ax.set_xlim(min(xs) - margin_x, max(xs) + margin_x)
            ax.set_ylim(min(ys) - margin_y, max(ys) + margin_y)

        win = tk.Toplevel(self.root)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --------- Launch interface ---------
if __name__ == "__main__":
    root = tk.Tk()
    gui = graphicInterface(root)
    root.mainloop()
    
#muchacho si va a ejecutar main, desde una terminal pegue y ejecute esto: py -m main.main
