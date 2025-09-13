#building class of tree
from .node import Node

class AVLTree:
    def __init__(self):
        #empty root, its for start the tree
        self.root = None

    # ===== Utility Functions =====
    #get the node height, if is None return 0
    def get_height(self, node):
        return node.height if node else 0

    #calculate the balance factor of one node.
    #diference between height of the left and right child
    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def right_rotate(self, z):
        #simple rotation to the right for balance the tree
        y = z.left
        T3 = y.right
        #here is the rotation
        y.right = z
        z.left = T3
        #recalculate height 
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        #this is the new subtree root 
        return y

    def left_rotate(self, z):
        #simple rotation to the left for balance the tree
        y = z.right
        T2 = y.left
        #here is the rotation 
        y.left = z
        z.right = T2
        #recalculate height
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        #this is the new subtree root 
        return y

    # ===== Comparison (x,y) =====
    def compare(self, v1, v2):
        #first compare by x
        if v1[0] < v2[0]:
            return -1
        elif v1[0] > v2[0]:
            return 1
        else:
            #if x are the same so compare by y
            if v1[1] < v2[1]:
                return -1
            elif v1[1] > v2[1]:
                return 1
            else:
                return 0  # they're exactly the same coordinates

    # ===== Insertion =====
    def insert(self, root, value, tipe):
        #case 0 or base: if the subtree is empty create a new node
        if not root:
            return Node(value, tipe)

        #compare the new coordinate with the root
        cmp = self.compare(value, root.value)
        if cmp < 0:
            #insert in left child
            root.left = self.insert(root.left, value, tipe)
        elif cmp > 0:
            #insert in right child
            root.right = self.insert(root.right, value, tipe)
        else:
            #this is for a duplicated root, here not insert 
            return root  # no duplicates allowed

        #update the current height node
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        #calculate the balance of the current node 
        balance = self.get_balance(root)

        # Rotations
        if balance > 1 and self.compare(value, root.left.value) < 0:
            return self.right_rotate(root) #right rotation
        if balance < -1 and self.compare(value, root.right.value) > 0:
            return self.left_rotate(root) #left rotation
        if balance > 1 and self.compare(value, root.left.value) > 0:
            root.left = self.left_rotate(root.left) #left - right rotation 
            return self.right_rotate(root)
        if balance < -1 and self.compare(value, root.right.value) < 0:
            root.right = self.right_rotate(root.right) #right left rotation 
            return self.left_rotate(root)

        #return the update root node 
        return root

    # ===== Search by coordenates =====
    def search(self, root, value):
        #case 0 or base: Node not found
        if not root:
            return None
        cmp = self.compare(value, root.value)
        if cmp == 0: #find node
            return root
        elif cmp < 0:
            return self.search(root.left, value) #search in the left subtree
        else:
            return self.search(root.right, value) #search in the right subtree 

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

    # ===== consultation of visible obstacles =====
    def range_query(self, root, x_min, x_max, y_min, y_max, result=None):
        #return all the nodes that his coordinates (x, y) inside of the rectangle define by [x_min, x_max] × [y_min, y_max]

        if result is None:
            result = []
        if not root:
            return result

        x, y = root.value
        if x_min <= x <= x_max and y_min <= y <= y_max:
            result.append(root)

        if root.left and x >= x_min:
            self.range_query(root.left, x_min, x_max, y_min, y_max, result)
        if root.right and x <= x_max:
            self.range_query(root.right, x_min, x_max, y_min, y_max, result)

        return result