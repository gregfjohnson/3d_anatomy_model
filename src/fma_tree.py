#!/usr/bin/env python3
### File Name: Tkinter ttk Treeview Simple Demo
### Reference: http://knowpapa.com/ttk-treeview/

import requests, os, socket
import math
import sys
import time
import numpy as np
np.set_printoptions(linewidth = 80)
import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pprint as pp
plt.ion()
# import pdb; pdb.set_trace()
from tkinter import *
from tkinter import ttk
from datetime import datetime
import assoc
from fma_to_file import fma_to_filename

def connect_to_server():
    """Connect as TCP client to TCD_server"""

    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        did_connect = client.connect_ex(('localhost', 7777))
        print(did_connect)
        if did_connect == 0:
            print('connected.')
            client.send(str.encode('hi.\n'))
            print('ok returning..')
            return client
        time.sleep(1)

partof_inclusion_list = assoc.AssocList('partof_inclusion_relation_list.txt')
print(f'partof_inclusion_list count:  {len(partof_inclusion_list.nodes)}')
for key in partof_inclusion_list.nodes:
    if len(partof_inclusion_list.nodes[key].parent_nodes) == 0:
        partof_root = partof_inclusion_list.nodes[key]
        break

def rec_insert(tree, assoc_list, parent_node):
    global node_count
    for child in parent_node.child_nodes:
        # import pdb; pdb.set_trace()
        child.tree_id = tree.insert(parent_node.tree_id, "end", child.fma, text=child.desc, values=("x", "x", "x"))
        node_count = node_count + 1
        rec_insert(tree, assoc_list, child)

root = Tk()
root.minsize(width=800, height=600)

tree = ttk.Treeview(root, height=600, columns=("Select", "Select all", "Clear all"))
tree.column("#0", width=700, minwidth=700)
# tree.heading("Anatomical_components", text="Anatomical_components")

def button1(event):
    print('left mouse button!', event, type(tree.identify_region(event.x, event.y)))
    print('more left mouse button!', type(tree.identify_element(event.x, event.y)))
    print(f'row {tree.identify_row(event.y)}, col {tree.identify_column(event.x)}')
    # import pdb; pdb.set_trace()
    fma = tree.identify_row(event.y)
    print(f'fma {fma}')
    fj_files = fma_to_filename([fma])
    fj_files = " ".join(fj_files)
    os.system('killall obj_view')
    print('run_obj_view ' + fj_files + ' -t FMA20394')
    os.system('run_obj_view ' + fj_files + ' -t FJ2810')
    # tcp_client.send(str.encode(fj_files+'\n'))

def select(event):
    print('select!', event)

tree.bind('<Button-1>', button1)
tree.bind('<<TreeviewSelect>>', select)

sel_width=75
tree.column("Select", width=sel_width, minwidth=sel_width)
tree.heading("Select", text="Select")

tree.column("Select all", width=sel_width, minwidth=sel_width)
tree.heading("Select all", text="Select all")

tree.column("Clear all", width=sel_width, minwidth=sel_width)
tree.heading("Clear all", text="Clear all")

node_count = 0
partof_root.tree_id = tree.insert("", "end", partof_root.fma, text=partof_root.desc, values=("x", "x", "x"))
node_count = node_count + 1
rec_insert(tree, partof_inclusion_list, partof_root)

# tree["columns"] = ("one", "two")
# tree.column("one", width=150)
# tree.column("two", width=100)
# tree.heading("one", text="column A")
# tree.heading("two", text="column B")


### insert format -> insert(parent, index, iid=None, **kw)
### reference: https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview


### insert sub-item, method 1
# id2 = tree.insert("", "end", "dir2", text="Dir 2")
# tree.insert(id2, "end", text="sub dir 2-1", values=("2A", "2B"))
# tree.insert(id2, "end", text="sub dir 2-2", values=("2A-2", "2B-2"))

### insert sub-item, method 2
# tree.insert("", "end", "dir3", text="Dir 3")
# tree.insert("dir3", "end", text=" sub dir 3", values=("3A", "3B"))

# tcp_client = connect_to_server()
tree.pack()
root.mainloop()
