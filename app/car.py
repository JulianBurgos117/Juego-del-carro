class Car:
    def __init__(self, color="blue", energy=100, speed=5, jump_height=10):
        self.x = 0
        self.y = 1  # lanes: 0 bottom, 1 middle, 2 top
        self.energy = energy
        self.color = color
        self.speed = speed

        # Jump settings
        self.jump_height = jump_height   # how many "frames" it stays up
        self.is_jumping = False
        self.jump_ticks = 0
        self.jump_offset = 0  # vertical displacement in pixels

    def move_forward(self):
        """Automatically move in X axis"""
        self.x += self.speed

    def move_up(self):
        """Move to upper lane"""
        if self.y < 2:
            self.y += 1

    def move_down(self):
        """Move to lower lane"""
        if self.y > 0:
            self.y -= 1

    def jump(self):
        """Start jump (only if not already jumping)"""
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_ticks = self.jump_height
            self.jump_offset = 0  # start from ground

    def update_jump(self):
        """Update jump effect (rise and fall)"""
        if self.is_jumping:
            if self.jump_ticks > 0:
                # Going up
                self.jump_offset += 6   # speed going up
                self.jump_ticks -= 1
            else:
                # Falling down
                self.jump_offset -= 6   # speed falling down
                if self.jump_offset <= 0:
                    self.jump_offset = 0
                    self.is_jumping = False

    def get_icon_key(self):
        """Return correct car image depending on jump state"""
        return "car_jump" if self.is_jumping else "car"

    def collide(self, obstacle):
        """Reduce energy depending on obstacle type"""
        tipo = obstacle.get("tipo", "obstaculo")
        if tipo == "roca":
            self.energy -= 20
        elif tipo == "hueco":
            self.energy -= 30
        elif tipo == "cono":
            self.energy -= 10
        elif tipo == "aceite":
            self.energy -= 15
        elif tipo == "peaton":
            self.energy -= 50
        else:
            self.energy -= 5