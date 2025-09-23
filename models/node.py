class Node:
    def __init__(self, value, tipo):
        # value será una tupla con (x1, y1, x2, y2)
        self.value = value
        self.tipo = tipo
        self.left = None
        self.right = None
        self.height = 1
