import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
from models.tree import Tree
from models.node import Node

class App:
    def __init__(self):
        self.tree = Tree()
        
    # Insert a new value into the tree
    def insert(self, value):
        #avoids same value nodes
        node = self.search(value)
        if (node is not None):
            print("Node with value ", value, " already exists.")
        else:
            #create a new node
            new_node = Node(value)
            #if tree is empty(there isn't root), new node is root
            if self.tree.root is None:
                self.tree.root = new_node
            else:
                #try insert the new node 
                self._insert(self.tree.root, new_node)

    def _insert(self, current_node, new_node):
        # new node goes left and current node is parent of new node if new node is smaller than current node and left is empty
        if new_node.value < current_node.value:
            if current_node.left is None:
                current_node.left = new_node
                new_node.parent = current_node
                new_node.height = 0
            else:
                # if left isnt empty, left node is current node and try again
                self._insert(current_node.left, new_node)
        else:
            # new node goes right and current node is parent of new node if new node is bigger than current node and right is empty
            if current_node.right is None:
                current_node.right = new_node
                new_node.parent = current_node
                new_node.height = 0
            else:
                #if rigth isnt empty, right node is current node and try again
                self._insert(current_node.right, new_node)
    
    # update heigths of nodes in tree
    def update_heights(self):
        def _update(node):
            if node is None:
                return -1
            left_height = _update(node.left)
            right_height = _update(node.right)
            node.height = max(left_height, right_height) + 1
            return node.height
        _update(self.tree.root)
        
    # get the balance of nodes
    def get_balance(self,node):
        if node is None:
            return 0
        node_balance = node.left.height - node.right.hright
        return node_balance
        
    # Search for a value in the tree
    def search(self, value):
        # if tree is empty return None
        if(self.tree.root is None):
            print("The tree is empty.")
            return None
        else:
            return self._search(self.tree.root, value)

    def _search(self, current_node, value):
        # return current node if exist
        if current_node is None or current_node.value == value:
            return current_node
        # goes left
        if value < current_node.value:
            return self._search(current_node.left, value)
        # goes right
        return self._search(current_node.right, value)

    # Find the inorder predecessor (the biggest in the left subtree)
    def _getPredecessor(self, node):
        if node.left is not None:
            current = node.left
            while current.right is not None:
                current = current.right
            return current
        return None

    # Replace one subtree with another (adjusts parent references)
    def changeNodePosition(self, node_to_replace, new_subtree_root):
        if node_to_replace.parent is None:  # If replacing the root
            self.tree.root = new_subtree_root
        else:
            if node_to_replace == node_to_replace.parent.left:
                node_to_replace.parent.left = new_subtree_root
            else:
                node_to_replace.parent.right = new_subtree_root
        #assigns his new father(father of node to replace)
        if new_subtree_root is not None:
            new_subtree_root.parent = node_to_replace.parent

    # Delete a node by value
    def delete(self, value):
        node_to_delete = self.search(value)
        if node_to_delete is not None:
            self._delete(node_to_delete)

    def _delete(self, node_to_delete):
        # Case 1: node is a leaf (no children)
        if node_to_delete.left is None and node_to_delete.right is None:
            self.changeNodePosition(node_to_delete, None)
            return

        # Case 2: node has two children
        if node_to_delete.left is not None and node_to_delete.right is not None:
            predecessor = self._getPredecessor(node_to_delete)
            if predecessor.parent != node_to_delete:  # predecessor is not a direct child
                self.changeNodePosition(predecessor, predecessor.left)
                predecessor.left = node_to_delete.left
                predecessor.left.parent = predecessor
            self.changeNodePosition(node_to_delete, predecessor)
            predecessor.right = node_to_delete.right
            predecessor.right.parent = predecessor
            return

        # Case 3: node has only one child
        if node_to_delete.left is not None:
            self.changeNodePosition(node_to_delete, node_to_delete.left)
        else:
            self.changeNodePosition(node_to_delete, node_to_delete.right)
    
    # perform a simple rotation to left
    def rotate_left(self, current_root):
        new_subroot = current_root.right
        current_root.right = new_subroot.left
        if new_subroot.left is not None:
            new_subroot.left.parent = current_root
        new_subroot.parent = current_root.parent
        if current_root.parent is None:
            self.tree.root = new_subroot
        elif current_root == current_root.parent.left:
            current_root.parent.left = new_subroot
        else:
            current_root.parent.right = new_subroot
        new_subroot.left = current_root
        current_root.parent = new_subroot
        self.update_heights()

    # perform a simple rotation to right
    def rotate_right(self, current_root):
        new_subroot = current_root.left
        current_root.left = new_subroot.right
        if new_subroot.right is not None:
            new_subroot.right.parent = current_root
        new_subroot.parent = current_root.parent
        if current_root.parent is None:
            self.tree.root = new_subroot
        elif current_root == current_root.parent.right:
            current_root.parent.right = new_subroot
        else:
            current_root.parent.left = new_subroot
        new_subroot.right = current_root
        current_root.parent = new_subroot
        self.update_heights()

    # Rotación doble izquierda-derecha
    def rotate_left_right(self, x):
        self.rotate_left(x.left)
        self.rotate_right(x)

    # Rotación doble derecha-izquierda
    def rotate_right_left(self, x):
        self.rotate_right(x.right)
        self.rotate_left(x)