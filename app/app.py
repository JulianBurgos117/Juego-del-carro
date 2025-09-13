
from .car import Car

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
            value = (obs["x"], obs["y"])
            self.tree.root = self.tree.insert(self.tree.root, value, obs["tipo"])

    def update_game(self):
        self.car.move_forward()
        self.check_collision()

    def check_collision(self):
        visibles = self.tree.range_query(
            self.tree.root,
            self.car.x,
            self.car.x + 50,  # rango visible
            0,
            2
        )
        for obs in visibles:
            if obs.value[0] == self.car.x and obs.value[1] == self.car.y:
                self.car.collide(obs)