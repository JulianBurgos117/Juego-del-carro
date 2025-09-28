
from app.car import Car

class App:
    def __init__(self, config, tree, gui=None):
        self.config = config
        self.tree = tree
        self.gui = gui  # 👈 guardamos referencia a la interfaz gráfica
        self.car = Car(
            color=config.get("car_color", "blue"),
            speed=config.get("car_speed", 5),
            jump_height=config.get("jump_height", 3),
        )
        self.road_length = config.get("road_length", 1000)
        self.refresh_time = config.get("refresh_time", 200)

    def load_obstacles(self, obstacles_list):
        for obs in obstacles_list:
            value = (obs["x1"], obs["y1"], obs["x2"], obs["y2"])
            tipo = obs.get("tipo", obs.get("tipo", "obstaculo"))
            self.tree.root = self.tree.insert(self.tree.root, value, tipo)

    def update_game(self):
        """Mover carro y revisar colisiones"""
        self.car.move_forward()
        self.car.update_jump()
        self.check_collision()

        if self.car.energy <= 0:
            self.end_game("⚠️ Energía agotada")
            return

    def check_collision(self):
        """Verificar si el carro choca con algún obstáculo visible"""
        visibles = self.tree.range_query(
            self.tree.root,
            self.car.x, self.car.x + 40,  # rango horizontal del carro
            self.car.y, self.car.y        # carril actual
        )

        # Si está saltando, no se revisan colisiones
        if not self.car.is_jumping:
            for obs in visibles:
                ox1, oy1, ox2, oy2 = obs["x1"], obs["y1"], obs["x2"], obs["y2"]

                # 🔹 Colisión
                if ox1 <= self.car.x <= ox2 and self.car.y == oy1:
                    print(f"💥 Colisión detectada en ({ox1},{oy1}) - eliminando nodo")
                    self.car.collide(obs)
                    self.tree.root = self.tree.delete(self.tree.root, (ox1, oy1, ox2, oy2))

                    # 🔹 Refrescar AVL
                    if self.gui:
                        self.gui.show_tree()

        # 🔹 Limpiar obstáculos que quedaron atrás
        all_nodes = list(self.tree.inorder(self.tree.root))
        for node in all_nodes:
            x1, y1, x2, y2 = node.value
            if x2 < self.car.x:  # obstáculo ya pasó por completo
                print(f"⬅️ Obstáculo en ({x1},{y1}) quedó atrás - eliminando nodo")
                self.tree.root = self.tree.delete(self.tree.root, node.value)

                # 🔹 Refrescar AVL
                if self.gui:
                    self.gui.show_tree()

    #dele an existen obstacle
    def _delete(self, node_to_delete):
        # Case 1: node is a leaf (no children)
        if node_to_delete.left is None and node_to_delete.right is None:
            self.changeNodePosition(node_to_delete, None)
            return

        # Case 2: node has two children
        if node_to_delete.left is not None and node_to_delete.right is not None:
            predecessor = self._getPredecessor(node_to_delete)
            if predecessor.parent != node_to_delete:  # predecessor is not a direct child
                self.changeNodePosition(predecessor, predecessor.left)
                predecessor.left = node_to_delete.left
                predecessor.left.parent = predecessor
            self.changeNodePosition(node_to_delete, predecessor)
            predecessor.right = node_to_delete.right
            predecessor.right.parent = predecessor
            return

        # Case 3: node has only one child
        if node_to_delete.left is not None:
            self.changeNodePosition(node_to_delete, node_to_delete.left)
        else:
            self.changeNodePosition(node_to_delete, node_to_delete.right)
    
    #search for an specific obstacle
    def search_obstacle(self, x1, y1, x2, y2, tipo):
        key = (x1, y1, x2, y2, tipo)
        return self.tree.search(self.tree.root, key)

    # perform a simple rotation to left
    def rotate_left(self, current_root):
        new_subroot = current_root.right
        current_root.right = new_subroot.left
        if new_subroot.left is not None:
            new_subroot.left.parent = current_root
        new_subroot.parent = current_root.parent
        if current_root.parent is None:
            self.tree.root = new_subroot
        elif current_root == current_root.parent.left:
            current_root.parent.left = new_subroot
        else:
            current_root.parent.right = new_subroot
        new_subroot.left = current_root
        current_root.parent = new_subroot
        self.update_heights()

    # perform a simple rotation to right
    def rotate_right(self, current_root):
        new_subroot = current_root.left
        current_root.left = new_subroot.right
        if new_subroot.right is not None:
            new_subroot.right.parent = current_root
        new_subroot.parent = current_root.parent
        if current_root.parent is None:
            self.tree.root = new_subroot
        elif current_root == current_root.parent.right:
            current_root.parent.right = new_subroot
        else:
            current_root.parent.left = new_subroot
        new_subroot.right = current_root
        current_root.parent = new_subroot
        self.update_heights()
        
    # Rotación doble izquierda-derecha
    def rotate_left_right(self, x):
        self.rotate_left(x.left)
        self.rotate_right(x)

    # Rotación doble derecha-izquierda
    def rotate_right_left(self, x):
        self.rotate_right(x.right)
        self.rotate_left(x)

    # Insert a new obstacle
    def insert_obstacle(self, x1, y1, x2, y2, tipo="normal"):
        try:
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        except ValueError:
            raise ValueError(f"Coordenadas inválidas: {x1}, {y1}, {x2}, {y2}")

        value = (x1, y1, x2, y2)
        self.tree.root = self.tree.insert(self.tree.root, value, tipo)












