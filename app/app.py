# app/app.py
from app.car import Car

class App:
    """
    Game logic coordinator — moves the car, checks collisions and manages obstacles via AVLTree.
    """

    def __init__(self, config, tree, gui=None):
        self.config = config or {}
        self.tree = tree
        self.gui = gui
        self.car = Car(
            color=self.config.get("car_color", "blue"),
            speed=self.config.get("car_speed", 5),
            jump_height=self.config.get("jump_height", 3)
        )
        self.road_length = self.config.get("road_length", 1000)
        self.refresh_time = self.config.get("refresh_time", 200)

    def load_obstacles(self, obstacles_list):
        for obs in obstacles_list:
            value = (obs["x1"], obs["y1"], obs["x2"], obs["y2"])
            tipo = obs.get("tipo", "obstaculo")
            self.tree.root = self.tree.insert(self.tree.root, value, tipo)

    def update_game(self):
        self.car.move_forward()
        self.car.update_jump()
        self.check_collision()

        if self.car.energy <= 0:
            self.end_game("Energy depleted")

    def rect_collision(self, car_rect, obs_rect):
        cx1, cy1, cx2, cy2 = car_rect
        ox1, oy1, ox2, oy2 = obs_rect
        return (cx1 < ox2 and cx2 > ox1 and cy1 < oy2 and cy2 > oy1)

    def check_collision(self):
        """
        Check collisions using rectangle intersection.
        Car rectangle is built from car.x and car.y (lane).
        """
        # define car rectangle: x range [car.x, car.x + width], y as lane coordinate
        # Use width and height heuristics — adjust if needed
        car_width = 40
        car_height = 1  # lane height conceptual (we compare lanes by integer)
        car_x1 = self.car.x
        car_x2 = self.car.x + car_width
        # For y we map lane number to simple range: y * 1 ... y * 1 + 1
        car_y1 = self.car.y
        car_y2 = self.car.y + 1

        visibles = self.tree.range_query(self.tree.root, self.car.x, self.car.x + 200, self.car.y, self.car.y)

        # Collision detection
        if not self.car.is_jumping:
            for obs in visibles:
                ox1, oy1, ox2, oy2 = obs["x1"], obs["y1"], obs["x2"], obs["y2"]

                # Check X overlap (car has width ~40)
                if ox1 <= self.car.x + 40 and self.car.x <= ox2:
                    # Check same lane (y)
                    if self.car.y in (oy1, oy2):
                        print(f" Collision at ({ox1},{oy1}) - removing node")
                        self.car.collide(obs)
                        self.tree.root = self.tree.delete(self.tree.root, (ox1, oy1, ox2, oy2))

                        if self.gui:
                            self.gui.show_tree()

        # remove obstacles behind car
        for node in list(self.tree.inorder(self.tree.root)):
            x1, y1, x2, y2 = node.value
            if x2 < self.car.x - 200:
                self.tree.root = self.tree.delete(self.tree.root, node.value)
                if self.gui:
                    self.gui.show_tree()

    def insert_obstacle(self, x1, y1, x2, y2, tipo="normal"):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        value = (x1, y1, x2, y2)
        self.tree.root = self.tree.insert(self.tree.root, value, tipo)

    def end_game(self, msg):
        if self.gui:
            # Use messagebox in GUI thread
            from tkinter import messagebox
            messagebox.showinfo("Game Over", msg)
        else:
            print("Game Over:", msg)