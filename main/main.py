import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

from app.app import App
from models.tree import AVLTree
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#muchacho si va a ejecutar main, desde una terminal pegue y ejecute esto: py -m main.main
class graphicInterface:
    def auto_refresh_tree(self, interval=1000):
        self.show_tree()
        self.root.after(interval, self.auto_refresh_tree, interval)


    def __init__(self, root):
        self.root = root
        self.root.title("Juego Carrito con AVL")
        self.json_file = "json\config.json"

        self.tree = AVLTree()
        self.app = None

        # ===== BUTTONS =====
        frame = tk.Frame(root)
        frame.pack(pady=10)

        btn_load = tk.Button(frame, text="Cargar JSON", command=self.load_json)
        btn_load.grid(row=0, column=0, padx=5)
        
        btn_load = tk.Button(frame, text="Insertar Obstacles", command=self.insert_node)
        btn_load.grid(row=0, column=1, padx=5)
        
        btn_load = tk.Button(frame, text="Delete Obstacles", command=self.delete_node)
        btn_load.grid(row=0, column=2, padx=5)

        btn_start = tk.Button(frame, text="Iniciar Juego", command=self.start_game)
        btn_start.grid(row=0, column=3, padx=5)

        btn_tree = tk.Button(frame, text="Ver AVL", command=self.show_tree)
        btn_tree.grid(row=0, column=4, padx=5)

        # ===== Canvas for game =====
        self.canvas = tk.Canvas(root, width=800, height=300, bg="white")
        self.canvas.pack()

    # JSON
    def load_json(self):
        filename = filedialog.askopenfilename(
            title="Selecciona el archivo de configuración",
            filetypes=[("Archivos JSON", "*.json")]
        )
        if filename:
            with open(filename, "r") as f:
                data = json.load(f)
                self.app = App(data["config"], self.tree)
                self.app.load_obstacles(data["obstacles"])
            self.json_file = filename  # Actualiza la ruta para guardar cambios
            messagebox.showinfo("Éxito", "Configuración y obstáculos cargados.")


    # New Obstacle
    def insert_node(self):
        if not self.app:
            messagebox.showwarning("Atención", "Primero cargue la configuración del juego.")
            return

        # create popup window
        top = tk.Toplevel()
        top.title("Nuevo obstáculo")

        labels = ["x1", "y1", "x2", "y2"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(top, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(top)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry

        # Menú for type
        tk.Label(top, text="Tipo").grid(row=len(labels), column=0, padx=5, pady=5)
        tipo_var = tk.StringVar(top)
        tipo_var.set("roca")  # default
        opciones_tipo = ["roca", "cono", "hueco", "aceite", "peaton"]
        menu_tipo = tk.OptionMenu(top, tipo_var, *opciones_tipo)
        menu_tipo.grid(row=len(labels), column=1, padx=5, pady=5)

        def save():
            try:
                x1 = int(entries["x1"].get())
                y1 = int(entries["y1"].get())
                x2 = int(entries["x2"].get())
                y2 = int(entries["y2"].get())
                tipo = tipo_var.get()
            except ValueError:
                messagebox.showerror("Error", "Las coordenadas deben ser números enteros.")
                return

            # Insert on tree
            self.app.insert_obstacle(x1, y1, x2, y2, tipo)

            # Seave on JSON
            nuevo = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "tipo": tipo}
            self._save_on_json(nuevo)

            messagebox.showinfo("Éxito", f"Obstáculo insertado: {nuevo}")
            top.destroy()

        tk.Button(top, text="Guardar", command=save).grid(row=len(labels) + 1, columnspan=2, pady=10)


    # Delete Obstacle
    def delete_node(self):
        if not self.app:
            messagebox.showwarning("Atención", "Primero cargue la configuración del juego.")
            return

        # create popup window
        top = tk.Toplevel()
        top.title("Eliminar obstáculo")

        # Load all obstacles from JSON
        try:
            with open(self.json_file, "r") as f:
                contenido = json.load(f)
                if not isinstance(contenido, dict):
                    contenido = {"config": {}, "obstacles": []}
                obstacles = contenido.get("obstacles", [])
        except (FileNotFoundError, json.JSONDecodeError):
            obstacles = []

        if not obstacles:
            messagebox.showinfo("Atención", "No hay obstáculos guardados.")
            top.destroy()
            return

        # Drop-down list with obstacles
        tk.Label(top, text="Seleccione el obstáculo a eliminar").pack(pady=5)
        opciones = [
            f"{i}: ({o['x1']}, {o['y1']}, {o['x2']}, {o['y2']}) - {o['tipo']}"
            for i, o in enumerate(obstacles)
        ]
        seleccion = tk.StringVar(top)
        seleccion.set(opciones[0])

        menu = tk.OptionMenu(top, seleccion, *opciones)
        menu.pack(pady=5)

        def eliminar():
            index = int(seleccion.get().split(":")[0])
            obstaculo = obstacles[index]

            # deleate from tree
            nodo = self.app.search_obstacle(
                obstaculo["x1"], obstaculo["y1"],
                obstaculo["x2"], obstaculo["y2"],
                obstaculo["tipo"]
            )
            if nodo:
                self.app._delete(nodo)

            # delete from JSON
            obstacles.pop(index)
            contenido["obstacles"] = obstacles

            with open(self.json_file, "w") as f:
                json.dump(contenido, f, indent=4)

            self.tree.root = None  # empty the tree
            self.app.load_obstacles(obstacles)  # Recharge from the updated list

            self.show_tree()

            messagebox.showinfo("Éxito", f"Obstáculo eliminado: {obstaculo}")
            top.destroy()

        tk.Button(top, text="Eliminar", command=eliminar).pack(pady=10)


    # Save new obstacle on JSON
    def _save_on_json(self, data):
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as f:
                try:
                    contenido = json.load(f)
                    # Ensure has the correct structure
                    if not isinstance(contenido, dict):
                        contenido = {"config": {}, "obstacles": []}
                    if "obstacles" not in contenido:
                        contenido["obstacles"] = []
                except json.JSONDecodeError:
                    contenido = {"config": {}, "obstacles": []}
        else:
            contenido = {"config": {}, "obstacles": []}

        # Add new obstacle
        contenido["obstacles"].append(data)

        # Save again
        with open(self.json_file, "w") as f:
            json.dump(contenido, f, indent=4)


    # Game
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

    #NOT YET
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


    # Show AVL
    def show_tree(self):
        if not self.tree.root:
            messagebox.showwarning("Atención", "El árbol está vacío.")
            return

        # Create window if it does not exist or was closed
        if not hasattr(self, "tree_window") or not self.tree_window.winfo_exists():
            self.tree_window = tk.Toplevel(self.root)
            self.tree_window.title("Árbol AVL de Obstáculos")
        else:
            # If it already exists, delete the old canvas
            for widget in self.tree_window.winfo_children():
                widget.destroy()

        # Create a new figure and a new canvas always
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.tree_canvas = FigureCanvasTkAgg(self.fig, master=self.tree_window)
        self.tree_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        #   Redraw entire tree
  
        # calculate positions using in-order traversal
        positions = {}
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

        # climb positions
        spacing_x = 2.0
        spacing_y = 2.5
        scaled = {}
        for node, (xi, depth) in positions.items():
            x = xi * spacing_x
            y = -depth * spacing_y
            scaled[node] = (x, y)

        # draw edges
        for node, (x, y) in scaled.items():
            if node.left and node.left in scaled:
                xl, yl = scaled[node.left]
                self.ax.plot([x, xl], [y, yl], color="gray", linewidth=1, zorder=1)
            if node.right and node.right in scaled:
                xr, yr = scaled[node.right]
                self.ax.plot([x, xr], [y, yr], color="gray", linewidth=1, zorder=1)

        # draw nodes
        for node, (x, y) in scaled.items():
            val = node.value
            tipo = getattr(node, "type", "")
            balance = self.tree.get_balance(node)

            # label
            if isinstance(val, (list, tuple)) and len(val) == 4:
                label = f"{val[0]},{val[1]}-{val[2]},{val[3]}\n{tipo}"
            else:
                label = str(val) + ("\n" + tipo if tipo else "")
            label += f"\nBF={balance}"

            # circle
            circle = plt.Circle((x, y), radius=0.6, edgecolor="black",
                                facecolor="lightblue", zorder=2)
            self.ax.add_patch(circle)
            self.ax.text(x, y, label, ha="center", va="center", fontsize=8, zorder=3)

        # adjust limits
        xs = [p[0] for p in scaled.values()]
        ys = [p[1] for p in scaled.values()]
        if xs and ys:
            self.ax.set_xlim(min(xs) - spacing_x, max(xs) + spacing_x)
            self.ax.set_ylim(min(ys) - spacing_y, max(ys) + spacing_y)

        self.ax.set_title("Árbol AVL de Obstáculos")
        self.ax.axis("off")

        # refreshr canvas
        self.tree_canvas.draw()
        self.tree_canvas.flush_events()
        self.tree_window.update_idletasks()



# Launch interface
if __name__ == "__main__":
    root = tk.Tk()
    gui = graphicInterface(root)
    root.mainloop()
    
#muchacho si va a ejecutar main, desde una terminal pegue y ejecute esto: py -m main.main
