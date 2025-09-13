class Car:
    def __init__(self, color="blue", energy=100, speed=5, jump_height=3):
        self.x = 0
        self.y = 1  # carril medio por defecto
        self.energy = energy
        self.color = color
        self.speed = speed
        self.jump_height = jump_height
        self.is_jumping = False

    def move_forward(self):
        pass

    def move_up(self):
        pass

    def move_down(self):
        pass

    def jump(self):
        pass

    def collide(self, obstacle):
        # reduce energía según tipo
        pass


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
        # insertar obstáculos en el AVL
        pass

    def update_game(self):
        # mover carro, detectar colisiones
        pass

    def check_collision(self):
        # validar colisiones con obstáculos visibles
        pass
