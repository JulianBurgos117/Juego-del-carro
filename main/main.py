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
        # Road
        self.canvas.create_line(0,250,800,250,fill="black",width=3)
        # Car
        car_x = 50
        car_y = 250 - self.app.car.y * 80 - self.app.car.jump_offset
        icon_key = self.app.car.get_icon_key()
        self.canvas.create_image(car_x, car_y, image=self.icons[icon_key], anchor="nw")
        # Obstacles
        visibles = self.tree.range_query(self.tree.root, self.app.car.x, self.app.car.x+200, 0, 2)
        for obs in visibles:
            ox, oy = obs["x1"], obs["y1"]
            screen_x = 50 + (ox - self.app.car.x)
            screen_y = 250 - oy * 80
            tipo = obs["tipo"]
            if tipo in self.icons:
                self.canvas.create_image(screen_x, screen_y - 20, image=self.icons[tipo], anchor="nw")
            else:
                self.canvas.create_rectangle(screen_x, screen_y-20, screen_x+30, screen_y+20, fill="red")

        # Energy bar
        bar_x, bar_y = 10, 10; bar_w, bar_h = 200, 20
        self.canvas.create_rectangle(bar_x, bar_y, bar_x+bar_w, bar_y+bar_h, fill="gray")
        energy_ratio = max(0, self.app.car.energy)/100
        color = "green" if energy_ratio>0.5 else "orange" if energy_ratio>0.2 else "red"
        self.canvas.create_rectangle(bar_x, bar_y, bar_x+bar_w*energy_ratio, bar_y+bar_h, fill=color)
        self.canvas.create_text(bar_x+bar_w/2, bar_y+bar_h/2, text=f"Energy: {self.app.car.energy}%", fill="white")

    # AVL visualization
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

        for node,(x,y) in scaled.items():
            if node.left and node.left in scaled:
                xl, yl = scaled[node.left]; self.ax.plot([x,xl],[y,yl],color="gray",linewidth=1)
            if node.right and node.right in scaled:
                xr, yr = scaled[node.right]; self.ax.plot([x,xr],[y,yr],color="gray",linewidth=1)

        for node,(x,y) in scaled.items():
            x1,y1,x2,y2 = node.value
            label = f"({x1},{y1})-({x2},{y2})\n{node.tipo}"
            bf = self.tree.get_balance(node)
            label += f"\nBF={bf}"
            circle = plt.Circle((x,y), radius=0.6, edgecolor="black", facecolor="lightblue")
            self.ax.add_patch(circle)
            self.ax.text(x,y,label,ha="center",va="center",fontsize=7)

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


if __name__ == "__main__":
    root = tk.Tk()
    gui = GraphicInterface(root)
    root.mainloop()

    #    py -m main.main