#building class of tree
from models.node import Node

class AVLTree:
    def __init__(self):
        #empty root, its for start the tree
        self.root = None

    # Utility Functions
    
    # get the node height, if is None return 0
    def get_height(self, node):
        return node.height if node else 0

    # calculate the balance factor of one node.
    def get_balance(self, node):
        # diference between height of the left and right child
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    # simple rotation to the right
    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        # here is the rotation
        y.right = z
        z.left = T3
        # recalculate height 
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        # this is the new subtree root 
        return y

    # simple rotation to the left
    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        # here is the rotation 
        y.left = z
        z.right = T2
        # recalculate height
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        # this is the new subtree root 
        return y

    # Comparison (x,y)
    def compare(self, v1, v2):
        if not isinstance(v1, tuple) or not isinstance(v2, tuple):
            raise TypeError(f"compare esperaba tuplas, recibió {v1} ({type(v1)}), {v2} ({type(v2)})")

        if v1[0] < v2[0]:
            return -1
        elif v1[0] > v2[0]:
            return 1
        elif v1[1] < v2[1]:
            return -1
        elif v1[1] > v2[1]:
            return 1
        else:
            return 0

    # Insertion
    def insert(self, root, value, type):
        print("Insertando:", value, type)

        # tree is empty
        if not root:
            return Node(value, type)
            
        # comparison: We order by x1, y1
        cmp = self.compare(value, root.value)

        if cmp < 0:
            root.left = self.insert(root.left, value, type)
        elif cmp > 0:
            root.right = self.insert(root.right, value, type)
        else:
            # if already exists, no duplicates
            return root  

        # update height
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # Check balance
        balance = self.get_balance(root)

        # Rotations
        if balance > 1 and self.compare(value, root.left.value) < 0:
            return self.right_rotate(root)

        if balance < -1 and self.compare(value, root.right.value) > 0:
            return self.left_rotate(root)

        if balance > 1 and self.compare(value, root.left.value) > 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)

        if balance < -1 and self.compare(value, root.right.value) < 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    # Search by coordenates
    
    def search(self, root, key):
        if root is None:
            return None

        if key == root.value:
            return root
        elif key < root.value:
            return self.search(root.left, key)
        else:
            return self.search(root.right, key)


    def _getPredecessor(self, node):

        current = node.left
        while current and current.right:
            current = current.right
        return current

    # ===== routes =====
    def inorder(self, root):
        #route by left → root → right 
        if root:
            yield from self.inorder(root.left)
            yield root
            yield from self.inorder(root.right)

    def preorder(self, root):
        #route by root → left → right 
        if root:
            yield root
            yield from self.preorder(root.left)
            yield from self.preorder(root.right)

    def postorder(self, root):
        #route by left → right → root
        if root:
            yield from self.postorder(root.left)
            yield from self.postorder(root.right)
            yield root

    def bfs(self, root):
        #route by levels (width (anchura)) using a queue
        if not root:
            return
        queue = [root]
        while queue:
            node = queue.pop(0)
            yield node
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    
    #not checked yet
    def range_query(self, root, x_min, x_max, y_min, y_max, result=None):
        """
        Devuelve todos los obstáculos cuyo rectángulo (x1, y1, x2, y2)
        esté dentro del rango definido por [x_min, x_max] x [y_min, y_max].
        """

        if result is None:
            result = []
        if not root:
            return result

        x1, y1, x2, y2 = root.value  # coordenadas del obstáculo

        # Chequeo de intersección: si el obstáculo toca el área visible
        if not (x2 < x_min or x1 > x_max or y2 < y_min or y1 > y_max):
            result.append({
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2,
                "tipo": root.tipo
            })

        # Recorremos ramas del árbol según la comparación
        if root.left and x1 >= x_min:
            self.range_query(root.left, x_min, x_max, y_min, y_max, result)
        if root.right and x2 <= x_max:
            self.range_query(root.right, x_min, x_max, y_min, y_max, result)

        return result
