class Car:
    def __init__(self, color="blue", energy=100, speed=5, jump_height=3):
        self.x = 0
        self.y = 1  # carril medio por defecto (0 abajo, 1 medio, 2 arriba)
        self.energy = energy
        self.color = color
        self.speed = speed
        self.jump_height = jump_height
        self.is_jumping = False
        self.jump_ticks = 0  # controla duración del salto

    def move_forward(self):
        """Move the car forward automatically along the X-axis"""
        self.x += self.speed

    def move_up(self):
        """Move the car one lane up (maximum is the top lane)."""
        if self.y < 2:  # máximo carril arriba
            self.y += 1

    def move_down(self):
        """Move the car one lane up (maximum is the top lane)."""
        if self.y > 0:  # mínimo carril abajo
            self.y -= 1

    def jump(self):
        """Move the car one lane up (maximum is the top lane)."""
        if not self.is_jumping:  # solo salta si no está ya en el aire
            self.is_jumping = True
            self.jump_ticks = self.jump_height

    def update_jump(self):
        """AUpdate the jump status by decreasing the jump counter.
        Once it reaches 0, the car lands back on the ground."""
        if self.is_jumping:
            self.jump_ticks -= 1
            if self.jump_ticks <= 0:
                self.is_jumping = False

    def collide(self, obstacle):
        """reduce the energy depend of the obstacle type"""
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