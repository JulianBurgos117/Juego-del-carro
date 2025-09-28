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
    """
    Graphical interface for the Car Game with AVL Tree.
    Handles user interaction, obstacle management, game drawing, and AVL visualization.
    """
    def auto_refresh_tree(self, interval=1000):
        """
        Automatically refresh the AVL tree visualization every given interval (ms).
        """
        self.show_tree()
        self.root.after(interval, self.auto_refresh_tree, interval)


    def __init__(self, root):
        """
        Initialize the main window, buttons, event bindings, and canvas.
        """
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

        btn_inorder = tk.Button(frame, text="Inorder", command=self.show_inorder)
        btn_inorder.grid(row=1, column=0, padx=5, pady=5)

        btn_preorder = tk.Button(frame, text="Preorder", command=self.show_preorder)
        btn_preorder.grid(row=1, column=1, padx=5, pady=5)

        btn_postorder = tk.Button(frame, text="Postorder", command=self.show_postorder)
        btn_postorder.grid(row=1, column=2, padx=5, pady=5)

        btn_bfs = tk.Button(frame, text="BFS", command=self.show_bfs)
        btn_bfs.grid(row=1, column=3, padx=5, pady=5)

        # Key bindings for car movement
        self.root.bind("<Up>", lambda e: self.app.car.move_up())
        self.root.bind("<Down>", lambda e: self.app.car.move_down())
        self.root.bind("<space>", lambda e: self.app.car.jump())

        # ===== Load icons =====
        self.icons = {
            "car": tk.PhotoImage(file="assets/car_blue.png").subsample(10, 10),
            "car_jump": tk.PhotoImage(file="assets/car_green.png").subsample(10, 10),
            "roca": tk.PhotoImage(file="assets/stone.png").subsample(6, 6),
            "cono": tk.PhotoImage(file="assets/traffic_cone.png").subsample(9, 9),
            "hueco": tk.PhotoImage(file="assets/hole.png").subsample(9, 9),
            "aceite": tk.PhotoImage(file="assets/oil.png").subsample(6, 6),
            "peaton": tk.PhotoImage(file="assets/human.png").subsample(6, 6),
        }   

        # ===== Canvas for game =====
        self.canvas = tk.Canvas(root, width=800, height=300, bg="white")
        self.canvas.pack()

    
    # ============================
    # JSON Loading and Saving
    # ============================
    def load_json(self):
        #Load configuration and obstacles from a JSON file.
        filename = filedialog.askopenfilename(
            title="Selecciona el archivo de configuración",
            filetypes=[("Archivos JSON", "*.json")]
        )
        if filename:
            with open(filename, "r") as f:
                data = json.load(f)
                # 👇 aquí le paso la referencia de la GUI
                self.app = App(data["config"], self.tree, gui=self)  
                self.app.load_obstacles(data["obstacles"])
            self.json_file = filename  # Actualiza la ruta para guardar cambios
            messagebox.showinfo("Éxito", "Configuración y obstáculos cargados.")


    # New Obstacle
    def insert_node(self):
        #Open a popup window to insert a new obstacle into the tree and JSON.
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
        #Open a popup window to delete an obstacle from the tree and JSON.
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
            # eliminar del árbol AVL (usando coordenadas)
            self.tree.root = self.tree.delete(
                self.tree.root,
                (obstaculo["x1"], obstaculo["y1"], obstaculo["x2"], obstaculo["y2"])
            )

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
        #Start the game loop if configuration has been loaded.
        if not self.app:
            messagebox.showwarning("Atención", "Primero cargue un archivo JSON.")
            return

        if getattr(self, "game_running", False):  # ya está corriendo
            return

        self.game_running = True
        self.game_loop()


    def game_loop(self):
        #Main game loop: update state, redraw, and repeat until game ends
        if self.app.car.x < self.app.road_length and self.app.car.energy > 0:
            self.app.update_game()
            self.draw_game()
            self.root.after(self.app.refresh_time, self.game_loop)
        else:
            self.game_running = False
            messagebox.showinfo("Juego terminado", "Fin del juego")

    #NOT YET
    def draw_game(self):
        #Draw the road, car, obstacles, and energy bar on the canvas
        self.canvas.delete("all")

        # paint road 
        self.canvas.create_line(0, 250, 800, 250, fill="black", width=3)

        # oaint the car
        car_x = 50
        car_y = 250 - self.app.car.y * 80
        car_icon = self.icons["car_jump"] if self.app.car.is_jumping else self.icons["car"]
        self.canvas.create_image(car_x, car_y, image=car_icon, anchor="nw")

        # visible obstacles 
        visibles = self.tree.range_query(
            self.tree.root,
            self.app.car.x,
            self.app.car.x + 200,  # rango de pantalla
            0,
            2,
        )

        for obs in visibles:
            ox, oy = obs["x1"], obs["y1"]  # diccionario, no nodo
            screen_x = 50 + (ox - self.app.car.x)
            screen_y = 250 - oy * 80
            tipo = obs["tipo"]
            if tipo in self.icons:
                self.canvas.create_image(screen_x, screen_y - 20, image=self.icons[tipo], anchor="nw")
            else:
                # fallback si no hay icono definido
                self.canvas.create_rectangle(
                    screen_x, screen_y - 20, screen_x + 30, screen_y + 20, fill="red"
                )

        # Energy
        self.canvas.create_text(700, 20, text=f"Energía: {self.app.car.energy}%", fill="blue")

        # draw the energy bar
        bar_x, bar_y = 10, 10  # esquina superior izquierda
        bar_width, bar_height = 200, 20

        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height, fill="gray")

        # Energía restante (verde → rojo)
        energy_ratio = max(0, self.app.car.energy) / 100
        color = "green" if energy_ratio > 0.5 else "orange" if energy_ratio > 0.2 else "red"
        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width * energy_ratio, bar_y + bar_height, fill=color)

        # Texto con porcentaje
        self.canvas.create_text(bar_x + bar_width / 2, bar_y + bar_height / 2,
                                text=f"Energía: {self.app.car.energy}%", fill="white")

    # Show AVL
    def show_tree(self):
        if not self.tree.root:
            messagebox.showwarning("Atención", "El árbol está vacío.")
            return

        # create o reuse the window
        if not hasattr(self, "tree_window") or not self.tree_window.winfo_exists():
            self.tree_window = tk.Toplevel(self.root)
            self.tree_window.title("Árbol AVL de Obstáculos")
            self.fig, self.ax = plt.subplots(figsize=(6, 4))
            self.tree_canvas = FigureCanvasTkAgg(self.fig, master=self.tree_window)
            self.tree_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            #  clear figure
            self.ax.clear()

        # === Redibujar árbol completo ===
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

        spacing_x, spacing_y = 2.0, 2.5
        scaled = {node: (xi * spacing_x, -depth * spacing_y)
                for node, (xi, depth) in positions.items()}

        # draw conections
        for node, (x, y) in scaled.items():
            if node.left and node.left in scaled:
                xl, yl = scaled[node.left]
                self.ax.plot([x, xl], [y, yl], color="gray", linewidth=1)
            if node.right and node.right in scaled:
                xr, yr = scaled[node.right]
                self.ax.plot([x, xr], [y, yr], color="gray", linewidth=1)

        # draw nodes
        for node, (x, y) in scaled.items():
            x1, y1, x2, y2 = node.value
            label = f"({x1},{y1})-({x2},{y2})\n{node.type}"
            balance = self.tree.get_balance(node)
            label += f"\nBF={balance}"

            circle = plt.Circle((x, y), radius=0.6, edgecolor="black", facecolor="lightblue")
            self.ax.add_patch(circle)
            self.ax.text(x, y, label, ha="center", va="center", fontsize=7)

        # settings
        if scaled:
            xs, ys = zip(*scaled.values())
            self.ax.set_xlim(min(xs) - spacing_x, max(xs) + spacing_x)
            self.ax.set_ylim(min(ys) - spacing_y, max(ys) + spacing_y)

        self.ax.axis("off")
        self.ax.set_title("Árbol AVL de Obstáculos")

        # refresh the canvas
        self.tree_canvas.draw()
        self.tree_window.update_idletasks()

    def end_jump(self):
        self.app.car.end_jump()

    def _show_traversal(self, nodes, title):
        #Helper to show a traversal (Inorder, Preorder, Postorder, BFS).
        if not nodes:
            messagebox.showinfo("Recorrido", "El árbol está vacío.")
            return

        # New window
        window = tk.Toplevel(self.root)
        window.title(title)

        fig, ax = plt.subplots(figsize=(6, 2))
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Draw nodes in line
        x = 0
        for node in nodes:
            val = node.value
            tipo = getattr(node, "type", "")
            label = f"{val}\n{tipo}"
            circle = plt.Circle((x, 0), radius=0.4, edgecolor="black", facecolor="lightgreen")
            ax.add_patch(circle)
            ax.text(x, 0, label, ha="center", va="center", fontsize=7)
            x += 1

        ax.set_xlim(-1, x)
        ax.set_ylim(-1, 1)
        ax.axis("off")
        ax.set_title(title)

        canvas.draw()
        window.update_idletasks()

    def show_inorder(self):
        """Show Inorder traversal in a new window."""
        nodes = list(self.tree.inorder(self.tree.root))
        self._show_traversal(nodes, "Recorrido Inorder")

    def show_preorder(self):
        """Show Preorder traversal in a new window."""
        nodes = list(self.tree.preorder(self.tree.root))
        self._show_traversal(nodes, "Recorrido Preorder")

    def show_postorder(self):
        """Show Postorder traversal in a new window."""
        nodes = list(self.tree.postorder(self.tree.root))
        self._show_traversal(nodes, "Recorrido Postorder")

    def show_bfs(self):
        """Show BFS (level order) traversal in a new window."""
        nodes = list(self.tree.bfs(self.tree.root))
        self._show_traversal(nodes, "Recorrido BFS")


# Launch interface
if __name__ == "__main__":
    root = tk.Tk()
    gui = graphicInterface(root)
    root.mainloop()
    
#muchacho si va a ejecutar main, desde una terminal pegue y ejecute esto: py -m main.main
