# main/main.py
import tkinter as tk
from tkinter import filedialog, messagebox
import json
from PIL import Image, ImageTk

from app.app import App
from models.avl import AVLTree
from app.config_manager import ConfigManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphicInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Game with AVL")
        self.config_mgr = ConfigManager("json/config.json")

        self.tree = AVLTree()
        self.app = None

        # Buttons frame
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Button(frame, text="Load JSON", command=self.load_json).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Insert Obstacle", command=self.insert_node).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Delete Obstacle", command=self.delete_node).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Start Game", command=self.start_game).grid(row=0, column=3, padx=5)
        tk.Button(frame, text="Show AVL", command=self.show_tree).grid(row=0, column=4, padx=5)
        tk.Button(frame, text="Inorder", command=self.show_inorder).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame, text="Preorder", command=self.show_preorder).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame, text="Postorder", command=self.show_postorder).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(frame, text="BFS", command=self.show_bfs).grid(row=1, column=3, padx=5, pady=5)
        tk.Button(frame, text="Restart", command=self.restart_game).grid(row=0, column=5, padx=5)

        # Bind keys (guard against app None)
        self.root.bind("<Up>", lambda e: self._safe_move_up())
        self.root.bind("<Down>", lambda e: self._safe_move_down())
        self.root.bind("<space>", lambda e: self._safe_jump())

        # icons
        # === Load and resize icons with PIL ===
        def load_icon(path, size=(40, 40)):
            img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)

        self.icons = {
            "car": load_icon("assets/car_blue.png"),
            "car_jump": load_icon("assets/car_green.png"),
            "roca": load_icon("assets/stone.png"),
            "cono": load_icon("assets/traffic_cone.png"),
            "hueco": load_icon("assets/hole.png"),
            "aceite": load_icon("assets/oil.png"),
            "peaton": load_icon("assets/human.png"),
        }

        self.canvas = tk.Canvas(root, width=800, height=300, bg="white")
        self.canvas.pack()


    # safe wrappers
    def _safe_move_up(self):
        if self.app:
            self.app.car.move_up()

    def _safe_move_down(self):
        if self.app:
            self.app.car.move_down()

    def _safe_jump(self):
        if self.app:
            self.app.car.jump()

    # JSON load/save using ConfigManager
    def load_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if not filename:
            return
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON: {e}")
            return

        # copy loaded data into config manager and use its config
        self.config_mgr.data = data
        config = self.config_mgr.get_config()
        self.tree = AVLTree()
        self.app = App(config, self.tree, gui=self)
        self.app.load_obstacles(self.config_mgr.get_obstacles())
        messagebox.showinfo("Success", "Configuration and obstacles loaded.")

    def insert_node(self):
        if not self.app:
            messagebox.showwarning("Warning", "Please load configuration first.")
            return

        top = tk.Toplevel()
        top.title("New Obstacle")
        labels = ["x1","y1","x2","y2"]; entries = {}
        for i,label in enumerate(labels):
            tk.Label(top, text=label).grid(row=i,column=0,padx=5,pady=5)
            e = tk.Entry(top); e.grid(row=i,column=1,padx=5,pady=5); entries[label]=e

        tk.Label(top, text="Type").grid(row=4,column=0,padx=5,pady=5)
        tipo_var = tk.StringVar(top); tipo_var.set("roca")
        tk.OptionMenu(top, tipo_var, "roca","cono","hueco","aceite","peaton").grid(row=4,column=1,padx=5,pady=5)

        def save():
            try:
                x1=int(entries["x1"].get()); y1=int(entries["y1"].get())
                x2=int(entries["x2"].get()); y2=int(entries["y2"].get())
                tipo=tipo_var.get()
            except ValueError:
                messagebox.showerror("Error","Coordinates must be integers.")
                return
            self.app.insert_obstacle(x1,y1,x2,y2,tipo)
            self.config_mgr.add_obstacle({"x1":x1,"y1":y1,"x2":x2,"y2":y2,"tipo":tipo})
            messagebox.showinfo("Success","Obstacle inserted.")
            top.destroy()

        tk.Button(top, text="Save", command=save).grid(row=5,columnspan=2,pady=10)

    def delete_node(self):
        if not self.app:
            messagebox.showwarning("Warning", "Please load configuration first.")
            return

        obs = self.config_mgr.get_obstacles()
        if not obs:
            messagebox.showinfo("Info","No obstacles to remove.")
            return

        top = tk.Toplevel()
        tk.Label(top, text="Select obstacle to delete").pack(pady=5)
        options=[f"{i}: ({o['x1']},{o['y1']},{o['x2']},{o['y2']}) - {o['tipo']}" for i,o in enumerate(obs)]
        var=tk.StringVar(top); var.set(options[0])
        tk.OptionMenu(top,var,*options).pack(pady=5)

        def eliminar():
            idx=int(var.get().split(":")[0])
            removed = self.config_mgr.remove_obstacle_by_index(idx)
            if removed:
                # rebuild tree from remaining obstacles
                self.tree = AVLTree()
                self.app.tree = self.tree
                self.app.load_obstacles(self.config_mgr.get_obstacles())
                self.show_tree()
                messagebox.showinfo("Success", f"Removed {removed}")
            top.destroy()

        tk.Button(top, text="Delete", command=eliminar).pack(pady=10)

    # Game loop
    def start_game(self):
        if not self.app:
            messagebox.showwarning("Warning","Please load configuration first.")
            return
        if getattr(self, "game_running", False):
            return
        self.game_running = True
        self.game_loop()

    def game_loop(self):
        if self.app.car.x < self.app.road_length and self.app.car.energy > 0:
            self.app.update_game()
            self.draw_game()
            self.root.after(self.app.refresh_time, self.game_loop)
        else:
            self.game_running = False
            messagebox.showinfo("Game Over","End of the game")

    def draw_game(self): 
        self.canvas.delete("all")

        # === Parámetros visuales ===
        canvas_width = 800
        canvas_height = 300
        road_height = 180
        road_top = (canvas_height - road_height) // 2
        road_bottom = road_top + road_height

        # Césped arriba y abajo
        self.canvas.create_rectangle(0, 0, canvas_width, road_top, fill="#228B22", outline="")
        self.canvas.create_rectangle(0, road_bottom, canvas_width, canvas_height, fill="#228B22", outline="")

        # Gradiente de la carretera
        for i in range(road_top, road_bottom, 8):
            gray = int(90 + (i - road_top) * 1.0)
            shade = f"#{gray:02x}{gray:02x}{gray:02x}"
            y2 = min(i+8, road_bottom)
            self.canvas.create_rectangle(0, i, canvas_width, y2, fill=shade, outline="")

        # Carretera centrada
        self.canvas.create_rectangle(0, road_top, canvas_width, road_bottom, fill="#5a5a5a", outline="")

        # === Césped superior (oscuro → claro hacia la carretera) ===
        for i in range(road_top):
            rel = i / road_top
            green_val = int(50 + rel * 80)  # verde oscuro arriba, más claro abajo
            shade = f"#{green_val:02x}{150:02x}{green_val:02x}"
            self.canvas.create_line(0, i, canvas_width, i, fill=shade)

        # === Carretera (encima del césped) ===
        for i in range(road_top, road_bottom):
            rel = (i - road_top) / road_height
            gray = int(90 + rel * 90)  # gris medio → claro
            shade = f"#{gray:02x}{gray:02x}{gray:02x}"
            self.canvas.create_line(0, i, canvas_width, i, fill=shade)

        # === Césped inferior (claro → oscuro hacia abajo) ===
        for i in range(road_bottom, canvas_height):
            rel = (i - road_bottom) / (canvas_height - road_bottom)
            green_val = int(130 - rel * 60)  # más claro junto a la carretera, más oscuro abajo
            shade = f"#{green_val:02x}{150:02x}{green_val:02x}"
            self.canvas.create_line(0, i, canvas_width, i, fill=shade)

        # === Carriles ===
        lane_count = 3
        lane_height = road_height // lane_count

        # Bordes de carriles (para líneas viales)
        lane_borders = [road_top + i * lane_height for i in range(lane_count + 1)]
        # Centros de carriles (para auto y obstáculos)
        lane_centers = [(lane_borders[i] + lane_borders[i+1]) / 2 for i in range(lane_count)]

        # Líneas viales
        offset = (self.app.car.x // 15) % 30
        for lane_y in lane_borders[1:-1]:  # solo las divisorias internas
            for x in range(-offset, canvas_width, 30):
                self.canvas.create_line(x, lane_y, x+12, lane_y, fill="white", width=3)

        # === Carro ===
        car_x = 120
        car_y = lane_centers[self.app.car.y] + self.app.car.get_jump_offset()
        icon_key = self.app.car.get_icon_key()
        self.canvas.create_image(car_x, car_y, image=self.icons[icon_key], anchor="center")

        # === Obstáculos ===
        render_distance_front = canvas_width
        render_distance_back = 100
        obstacle_width = 40

        visibles = self.tree.range_query(
            self.tree.root,
            self.app.car.x - render_distance_back,
            self.app.car.x + render_distance_front,
            0, lane_count - 1
        )

        for obs in visibles:
            ox, oy = obs["x1"], obs["y1"]
            screen_x = car_x + (ox - self.app.car.x)
            screen_y = lane_centers[oy]

            tipo = obs["tipo"]
            if tipo in self.icons:
                self.canvas.create_image(screen_x, screen_y, image=self.icons[tipo], anchor="center")
            else:
                colors = {"roca": "gray", "hueco": "black", "peaton": "blue"}
                fill_color = colors.get(tipo, "orange")
                self.canvas.create_rectangle(
                    screen_x - obstacle_width // 2, screen_y - obstacle_width // 2,
                    screen_x + obstacle_width // 2, screen_y + obstacle_width // 2,
                    fill=fill_color, outline=""
                )

        # === Barra de energía ===
        bar_x, bar_y, bar_w, bar_h = 10, 10, 200, 20
        self.canvas.create_rectangle(bar_x, bar_y, bar_x+bar_w, bar_y+bar_h,
                                    outline="white", width=2)
        energy_ratio = max(0, self.app.car.energy) / 100
        color = "green" if energy_ratio > 0.5 else "orange" if energy_ratio > 0.2 else "red"
        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_w * energy_ratio,
                                    bar_y + bar_h, fill=color, outline="")
        self.canvas.create_text(bar_x + bar_w/2, bar_y + bar_h/2,
                                text=f"⚡ {self.app.car.energy}%",
                                fill="white", font=("Arial", 10, "bold"))



    # === AVL visualization ===
    def show_tree(self):
        if not self.tree.root:
            messagebox.showwarning("Warning","Tree is empty.")
            return

        if not hasattr(self,"tree_window") or not self.tree_window.winfo_exists():
            self.tree_window = tk.Toplevel(self.root)
            self.tree_window.title("AVL Tree")
            self.fig, self.ax = plt.subplots(figsize=(6,4))
            self.tree_canvas = FigureCanvasTkAgg(self.fig, master=self.tree_window)
            self.tree_canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            self.ax.clear()

        positions = {}; counter = {"x":0,"max_depth":0}
        def inorder(node, depth=0):
            if not node: return
            inorder(node.left, depth+1)
            positions[node] = (counter["x"], depth)
            counter["x"] += 1
            counter["max_depth"] = max(counter["max_depth"], depth)
            inorder(node.right, depth+1)
        inorder(self.tree.root)

        spacing_x, spacing_y = 2.0, 2.5
        scaled = {node:(xi*spacing_x, -depth*spacing_y) for node,(xi,depth) in positions.items()}

        # Edges
        for node,(x,y) in scaled.items():
            if node.left and node.left in scaled:
                xl, yl = scaled[node.left]; self.ax.plot([x,xl],[y,yl],color="gray",linewidth=1)
            if node.right and node.right in scaled:
                xr, yr = scaled[node.right]; self.ax.plot([x,xr],[y,yr],color="gray",linewidth=1)

        # Nodes
        for node,(x,y) in scaled.items():
            x1,y1,x2,y2 = node.value
            label = f"({x1},{y1})-({x2},{y2})\n{node.tipo}"
            bf = self.tree.get_balance(node)
            label += f"\nBF={bf}"

            # Color by balance factor
            color = "lightgreen" if bf == 0 else "lightblue" if bf > 0 else "lightcoral"

            circle = plt.Circle((x,y), radius=0.6, edgecolor="black", facecolor=color, lw=1.5)
            self.ax.add_patch(circle)
            self.ax.text(x,y,label,ha="center",va="center",fontsize=7, fontweight="bold")

        if scaled:
            xs, ys = zip(*scaled.values())
            self.ax.set_xlim(min(xs)-spacing_x, max(xs)+spacing_x)
            self.ax.set_ylim(min(ys)-spacing_y, max(ys)+spacing_y)

        self.ax.axis("off")
        self.ax.set_title("AVL Tree of Obstacles")
        self.tree_canvas.draw()
        self.tree_window.update_idletasks()

    # Traversal helpers
    def _show_traversal(self, nodes, title):
        if not nodes:
            messagebox.showinfo("Traversal", "Tree is empty.")
            return

        # Create or reuse window
        window = tk.Toplevel(self.root)
        window.title(title)
        fig, ax = plt.subplots(figsize=(6, 4))
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # === Calculate positions (reuse inorder layout like show_tree) ===
        positions = {}
        counter = {"x": 0, "max_depth": 0}

        def inorder_pos(node, depth=0):
            if not node:
                return
            inorder_pos(node.left, depth + 1)
            positions[node] = (counter["x"], depth)
            counter["x"] += 1
            counter["max_depth"] = max(counter["max_depth"], depth)
            inorder_pos(node.right, depth + 1)

        inorder_pos(self.tree.root)

        spacing_x, spacing_y = 2.0, 2.5
        scaled = {node: (xi * spacing_x, -depth * spacing_y)
                for node, (xi, depth) in positions.items()}

        # === Draw edges ===
        for node, (x, y) in scaled.items():
            if node.left and node.left in scaled:
                xl, yl = scaled[node.left]
                ax.plot([x, xl], [y, yl], color="gray", linewidth=1)
            if node.right and node.right in scaled:
                xr, yr = scaled[node.right]
                ax.plot([x, xr], [y, yr], color="gray", linewidth=1)

        # === Highlight traversal order ===
        order_map = {node: idx + 1 for idx, node in enumerate(nodes)}
        for node, (x, y) in scaled.items():
            x1, y1, x2, y2 = node.value
            tipo = getattr(node, "type", "unknown")
            label = f"({x1},{y1})-({x2},{y2})\n{tipo}"

            if node in order_map:
                # Node is part of the traversal
                circle = plt.Circle((x, y), radius=0.6, edgecolor="black", facecolor="lightgreen")
                ax.add_patch(circle)
                # Number showing visit order
                ax.text(x, y, f"{order_map[node]}", ha="center", va="center", fontsize=9, color="red")
            else:
                # Non-visited node (shouldn't happen in complete traversals)
                circle = plt.Circle((x, y), radius=0.6, edgecolor="black", facecolor="lightblue")
                ax.add_patch(circle)

            ax.text(x, y - 0.9, label, ha="center", va="center", fontsize=6)

        # Adjust view
        if scaled:
            xs, ys = zip(*scaled.values())
            ax.set_xlim(min(xs) - spacing_x, max(xs) + spacing_x)
            ax.set_ylim(min(ys) - spacing_y, max(ys) + spacing_y)

        ax.axis("off")
        ax.set_title(title)
        canvas.draw()
        window.update_idletasks()
    
    def show_inorder(self):
        """Display the AVL tree highlighting nodes in Inorder traversal."""
        nodes = list(self.tree.inorder(self.tree.root))
        self._show_traversal(nodes, "Inorder Traversal")

    def show_preorder(self):
        """Display the AVL tree highlighting nodes in Preorder traversal."""
        nodes = list(self.tree.preorder(self.tree.root))
        self._show_traversal(nodes, "Preorder Traversal")

    def show_postorder(self):
        """Display the AVL tree highlighting nodes in Postorder traversal."""
        nodes = list(self.tree.postorder(self.tree.root))
        self._show_traversal(nodes, "Postorder Traversal")

    def show_bfs(self):
        """Display the AVL tree highlighting nodes in Breadth-First traversal (BFS)."""
        nodes = list(self.tree.bfs(self.tree.root))
        self._show_traversal(nodes, "BFS Traversal")

    def restart_game(self):
        if not self.app:
            messagebox.showwarning("Warning", "Please load configuration first.")
            return
        
        # Detener loop del juego si estaba corriendo
        self.game_running = False  
        
        # Crear nuevo árbol y reiniciar app con la misma config
        self.tree = AVLTree()
        config = self.config_mgr.get_config()
        self.app = App(config, self.tree, gui=self)
        self.app.load_obstacles(self.config_mgr.get_obstacles())
        
        # Reiniciar carro
        self.app.car.x = 0
        self.app.car.y = 0
        self.app.car.energy = 100
        self.app.car.is_jumping = False
        self.app.car.jump_offset = 0
        self.app.car.jump_velocity = 0
        
        # Limpiar canvas
        self.canvas.delete("all")
        
        # Redibujar estado inicial (carro y obstáculos)
        self.draw_game()
        
        # También refrescar AVL si estaba abierto
        if hasattr(self, "tree_window") and self.tree_window.winfo_exists():
            self.show_tree()
        
        messagebox.showinfo("Restart", "Game restarted successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = GraphicInterface(root)
    root.mainloop()

    #    py -m main.main