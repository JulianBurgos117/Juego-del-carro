 #building class of nodes
class Node:
    
    def __init__(self, value, parent=None):
        self.value = value
        self.left = None
        self.right = None
        self.parent = parent
        self.height = 1
        