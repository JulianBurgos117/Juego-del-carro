
from app.car import Car

class App:
    def __init__(self, config, tree):
        self.config = config
        self.tree = tree
        self.car = Car(
            color=config.get("car_color", "blue"),
            speed=config.get("car_speed", 5),
            jump_height=config.get("jump_height", 3),
        )
        self.road_length = config.get("road_length", 1000)
        self.refresh_time = config.get("refresh_time", 200)

    def load_obstacles(self, obstacles_list):
        for obs in obstacles_list:
            # Asegurarse que el JSON use x1,y1,x2,y2
            value = (obs["x1"], obs["y1"], obs["x2"], obs["y2"])
            tipo = obs.get("tipo", obs.get("type", "obstaculo"))
            self.tree.root = self.tree.insert(self.tree.root, value, tipo)


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

    def insert_obstacle(self, x, y, tipo="normal"):
        """
        Inserta un obstáculo en el árbol AVL.
        x: posición en la carretera
        y: carril (0, 1 o 2)
        tipo: tipo de obstáculo (string)
        """
        value = (x, y)  # coordenadas del obstáculo
        self.tree.root = self.tree.insert(self.tree.root, value, tipo)








