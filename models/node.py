 #building class of nodes
class Node:
    def __init__(self, value, tipe):
        """
        value: tuple (x, y) -> obstacle coordinates
        tipo: string -> obstacle tipe (stone, hole, etc.)
        """
        self.value = value
        self.tipo = tipe
        self.height = 1
        self.left = None
        self.right = None
        
