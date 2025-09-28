class Node:
    def __init__(self, value, tipo):
        """
        represent a node of the tree.

        Atributos:
        ----------
        value : tuple
            
        type : str
            
        left : Node | None
            
        right : Node | None
            
        height : int
            Altura del nodo en el árbol (inicialmente 1 porque es hoja).
        """
        self.value = value      #Coordenadas del obstáculo, generalmente (x1, y1, x2, y2).
        self.type = tipo        #Type of obstacle (e.g., "rock", "cone", "hole"...).
        self.left = None        #Reference to the left child
        self.right = None       #Reference to the right child
        self.height = 1         #Height of the node in the tree (starts at 1 since it is a leaf).
