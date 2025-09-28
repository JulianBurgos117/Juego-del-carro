# models/node.py
class Node:
    """
    Represents a node in the AVL tree.

    Attributes
    ----------
    value : tuple
        Obstacle coordinates (x1, y1, x2, y2).
    tipo : str
        Obstacle type (e.g., "roca", "cono", ...).
    left, right : Node | None
        Child references.
    height : int
        Node height in AVL tree (1 for a leaf).
    """
    def __init__(self, value, tipo):
        self.value = value
        self.tipo = tipo
        self.left = None
        self.right = None
        self.height = 1