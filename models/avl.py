# models/avl.py
from models.node import Node

class AVLTree:
    """
    AVL tree specialized to store obstacles where ordering is based on (x1, y1).
    The stored node.value is expected to be a tuple: (x1, y1, x2, y2).
    """

    def __init__(self):
        self.root = None

    # ---- Utilities ----
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def _update_height(self, node):
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    # ---- Rotations ----
    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        self._update_height(z)
        self._update_height(y)
        return y

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        self._update_height(z)
        self._update_height(y)
        return y

    # ---- Comparison by (x1, y1) ----
    def compare(self, v1, v2):
        if not (isinstance(v1, tuple) and isinstance(v2, tuple)):
            raise TypeError("compare expects tuple values")
        # compare x1
        if v1[0] < v2[0]:
            return -1
        if v1[0] > v2[0]:
            return 1
        # tie on x1 -> compare y1
        if v1[1] < v2[1]:
            return -1
        if v1[1] > v2[1]:
            return 1
        return 0

    # ---- Insert ----
    def insert(self, root, value, tipo):
        """
        Insert value=(x1,y1,x2,y2) with type into tree and return new root.
        Duplicates by (x1,y1) are ignored.
        """
        if root is None:
            return Node(value, tipo)

        cmp = self.compare(value, root.value)
        if cmp < 0:
            root.left = self.insert(root.left, value, tipo)
        elif cmp > 0:
            root.right = self.insert(root.right, value, tipo)
        else:
            # duplicate (same x1,y1) -> ignore
            return root

        self._update_height(root)
        balance = self.get_balance(root)

        # LL
        if balance > 1 and self.compare(value, root.left.value) < 0:
            return self.right_rotate(root)
        # RR
        if balance < -1 and self.compare(value, root.right.value) > 0:
            return self.left_rotate(root)
        # LR
        if balance > 1 and self.compare(value, root.left.value) > 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        # RL
        if balance < -1 and self.compare(value, root.right.value) < 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    # ---- Search (by full tuple) ----
    def search(self, root, key):
        if root is None:
            return None
        if key == root.value:
            return root
        if self.compare(key, root.value) < 0:
            return self.search(root.left, key)
        else:
            return self.search(root.right, key)

    # ---- Min (helper for delete) ----
    def get_min(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    # ---- Delete ----
    def delete(self, root, value):
        """
        Delete node with value (x1,y1,x2,y2) and return new root.
        """
        if root is None:
            return root

        cmp = self.compare(value, root.value)
        if cmp < 0:
            root.left = self.delete(root.left, value)
        elif cmp > 0:
            root.right = self.delete(root.right, value)
        else:
            # found
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            temp = self.get_min(root.right)
            root.value = temp.value
            root.type = temp.tipo 
            root.right = self.delete(root.right, temp.value)

        self._update_height(root)
        balance = self.get_balance(root)

        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    # ---- Traversals ----
    def inorder(self, root):
        if root:
            yield from self.inorder(root.left)
            yield root
            yield from self.inorder(root.right)

    def preorder(self, root):
        if root:
            yield root
            yield from self.preorder(root.left)
            yield from self.preorder(root.right)

    def postorder(self, root):
        if root:
            yield from self.postorder(root.left)
            yield from self.postorder(root.right)
            yield root

    def bfs(self, root):
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

    # ---- Range query ----
    def range_query(self, root, x_min, x_max, y_min, y_max, result=None):
        """
        Collect obstacles whose rectangle intersects the query box.
        Returns list of dicts: {"x1":..., "y1":..., "x2":..., "y2":..., "tipo":...}
        """
        if result is None:
            result = []
        if not root:
            return result

        x1, y1, x2, y2 = root.value

        if not (x2 < x_min or x1 > x_max or y2 < y_min or y1 > y_max):
            result.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "tipo": root.tipo})

        # prune by comparing x-values (because tree ordered by x1)
        if root.left and x1 >= x_min:
            self.range_query(root.left, x_min, x_max, y_min, y_max, result)
        if root.right and x2 <= x_max:
            self.range_query(root.right, x_min, x_max, y_min, y_max, result)

        return result