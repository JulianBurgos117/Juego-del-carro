import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import simpledialog, messagebox
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from app.app import App
#from app.utils import utils

class graphicInterface():

# Method to print the tree in console 
    def print_tree(self, node=None, prefix="", is_left=True):
        if node is not None:
            # Print right subtree
            if node.right:
                new_prefix = prefix + ("│   " if is_left else "    ")
                self.print_tree(node.right, new_prefix, False)

            # Print current node
            connector = "└── " if is_left else "┌── "
            print(prefix + connector + str(node.value))

            # Print left subtree
            if node.left:
                new_prefix = prefix + ("    " if is_left else "│   ")
                self.print_tree(node.left, new_prefix, True)

    def plot(self, canvas_frame):
        coordinate_tree.update_heights()
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.axis('off')
        def _plot(node, x, y, dx):
            if node:
                ax.text(x, y+0.3, str(node.height), ha='center', va='center', color='blue', fontsize=10)
                ax.text(x, y, str(node.value), ha='center', va='center',
                        bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
                if node.left:
                    ax.plot([x, x-dx], [y, y-1], color='black')
                    _plot(node.left, x-dx, y-1, dx/2)
                if node.right:
                    ax.plot([x, x+dx], [y, y-1], color='black')
                    _plot(node.right, x+dx, y-1, dx/2)
        _plot(coordinate_tree.tree.root, 0, 0, 8)
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)  # close fig

if __name__ == "__main__":   
         
    coordinate_tree = App()
    gui = graphicInterface()  
    
    def update_tree_graph():
        gui.plot(tree_frame)

    def insert_node():
        valor = simpledialog.askinteger("Insertar nodo", "Ingrese el valor a insertar:")
        if valor is not None:
            coordinate_tree.insert(valor)
            update_tree_graph()

    def delete_node():
        valor = simpledialog.askinteger("Eliminar nodo", "Ingrese el valor a eliminar:")
        if valor is not None:
            coordinate_tree.delete(valor)
            update_tree_graph()
    
    def preorder_travesal():
        resultado = []
        def _inorder(node):
            resultado.append(str(node.value))
            
            if node.left:
                _inorder(node.left)
            
            if node.right:
                _inorder(node.right)
        if coordinate_tree.tree.root is None:
            messagebox.showinfo("Árbol vacío", "El árbol está vacío.")
        else:
            _inorder(coordinate_tree.tree.root)
            messagebox.showinfo("Recorrido preorder", ", ".join(resultado))
                
    def inorder_travesal():
        resultado = []
        def _inorder(node):
            if node.left:
                _inorder(node.left)
                
            resultado.append(str(node.value))
            
            if node.right:
                _inorder(node.right)
                
        if coordinate_tree.tree.root is None:
            messagebox.showinfo("Árbol vacío", "El árbol está vacío.")
        else:
            _inorder(coordinate_tree.tree.root)
            messagebox.showinfo("Recorrido inorder", ", ".join(resultado))
            
    def postorder_travesal():
        resultado = []
        def _inorder(node):
            if node.left:
                _inorder(node.left)
            
            if node.right:
                _inorder(node.right)
            
            resultado.append(str(node.value))
            
        if coordinate_tree.tree.root is None:
            messagebox.showinfo("Árbol vacío", "El árbol está vacío.")
        else:
            _inorder(coordinate_tree.tree.root)
            messagebox.showinfo("Recorrido postorder", ", ".join(resultado))

    def get_out():
        app.destroy()

    #----------------------------WINDOW, BUTTOMS AND MENU-----------------------------
    
    app = tk.Tk()
    app.geometry("600x400")
    app.configure(background="black")

    button_frame = tk.Frame(app, bg="black")
    button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    tree_frame = tk.Frame(app, bg="black")
    tree_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Button(
        button_frame,
        text='1. Insertar nodo',
        fg= 'white',
        bg= 'black',
        relief= 'flat',
        command=insert_node
        ).pack(pady=5, fill=tk.X)
    
    tk.Button(
        button_frame,
        text='2. Eliminar nodo',
        fg= 'white',
        bg= 'black',
        relief= 'flat',
        command=delete_node
        ).pack(pady=5, fill=tk.X)
    
    tk.Button(
        button_frame,
        text='3. Mostrar árbol (preorder)',
        fg= 'white',
        bg= 'black',
        relief= 'flat',
        command=preorder_travesal
        ).pack(pady=5, fill=tk.X)
    
    tk.Button(
        button_frame,
        text='3. Mostrar árbol (inorder)',
        fg= 'white',
        bg= 'black',
        relief= 'flat',
        command=inorder_travesal
        ).pack(pady=5, fill=tk.X)
    
    tk.Button(
        button_frame,
        text='3. Mostrar árbol (postorder)',
        fg= 'white',
        bg= 'black',
        relief= 'flat',
        command=postorder_travesal
        ).pack(pady=5, fill=tk.X)

    tk.Button(
        button_frame,
        text='5. Salir',
        fg= 'white',
        bg= 'black',
        relief= 'flat',
        command=get_out
        ).pack(pady=5, fill=tk.X)

    update_tree_graph()  # Muestra el árbol al iniciar
    app.mainloop()