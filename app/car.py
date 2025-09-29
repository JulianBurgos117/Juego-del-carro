class Car:
    def __init__(self, color="blue", energy=100, speed=5, jump_height=6, jump_duration=30):
        self.x = 0
        self.y = 1  # lane: 0=bottom, 1=middle, 2=top
        self.energy = energy
        self.color = color
        self.speed = speed
        self.jump_height = jump_height
        self.jump_duration = jump_duration
        self.is_jumping = False
        self.jump_progress = 0  # counter for jump frames

    def move_forward(self):
        """Move automatically in X axis"""
        self.x += self.speed

    def move_up(self):
        if self.y < 2:
            self.y += 1

    def move_down(self):
        if self.y > 0:
            self.y -= 1

    def jump(self):
        """Start a jump if not already jumping"""
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_progress = 0

    def update_jump(self):
        """Update jump progress"""
        if self.is_jumping:
            self.jump_progress += 1
            if self.jump_progress >= self.jump_duration:
                self.is_jumping = False

    def get_jump_offset(self):
        """Smooth jump offset in pixels"""
        if not self.is_jumping:
            return 0
        mid = self.jump_duration / 2
        return -int(
            self.jump_height * 10 * (1 - abs(self.jump_progress - mid) / mid)
        )

    def get_icon_key(self):
        """Choose correct car icon"""
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