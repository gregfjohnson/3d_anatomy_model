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

def activate_exit():
    os.system('killall obj_view')
    root.destroy()
    sys.exit(0)

root = Tk()
root.minsize(width=800, height=500)
root.protocol("WM_DELETE_WINDOW", activate_exit)

tree = ttk.Treeview(root, height=500, selectmode="browse", columns=("Select", "Identify", "Clear all"))
tree.column("#0", width=700, minwidth=700)

tree.fma_selections = set()
# mylist = list(dict.fromkeys(mylist))

def button1(event):
    global tree
    print('left mouse button!', event, tree.identify_region(event.x, event.y))
    print('more left mouse button!', tree.identify_element(event.x, event.y))
    print(f'row {tree.identify_row(event.y)}, col {tree.identify_column(event.x)}')
    tree.button_event = event

    # import pdb; pdb.set_trace()
    fma = tree.identify_row(event.y)
    print(f'fma {fma}')
    fj_files = fma_to_filename([fma])
    fj_files = " ".join(fj_files)


tree.bind('<Button-1>', button1)

def TreeviewSelect(event):
    global tree
    print('TreeviewSelect!', event, tree.button_event)
    event = tree.button_event
    if tree.identify_column(event.x) == '#1':
        print(f'identify_element:  {tree.identify_element(event.x, event.y)}')
        fma = tree.selection()[0]
        print(f'selection:  {fma}') 
        print(f'item:  {tree.item(fma)}')
        item_dict = tree.item(fma)
        values = item_dict['values']
        prev_set_count = len(tree.fma_selections)
        if values[0] == 'x':
            values[0] = '*'
            tree.fma_selections = tree.fma_selections | {fma}
        else:
            values[0] = 'x'
            tree.fma_selections = tree.fma_selections - {fma}

        tree.item(tree.selection(), values=values)
        print(f'fma_selections:  {tree.fma_selections}')

        if prev_set_count != len(tree.fma_selections):
            os.system('killall obj_view')

            if len(tree.fma_selections) != 0:
                fj_files = fma_to_filename(list(tree.fma_selections))
                fj_file_string = ' '.join(fj_files)
                os.system('run_obj_view ' + fj_file_string + ' -t FJ2810')

tree.bind('<<TreeviewSelect>>', TreeviewSelect)

def TreeviewOpen(event):
    print('TreeviewOpen!', event)

tree.bind('<<TreeviewOpen>>', TreeviewOpen)

def TreeviewClose(event):
    print('TreeviewClose!', event)

tree.bind('<<TreeviewClose>>', TreeviewClose)

sel_width=75
tree.column("Select", width=sel_width, minwidth=sel_width)
tree.heading("Select", text="Select")

tree.column("Identify", width=sel_width, minwidth=sel_width)
tree.heading("Identify", text="Identify")

tree.column("Clear all", width=sel_width, minwidth=sel_width)
tree.heading("Clear all", text="Clear all")

node_count = 0
partof_root.tree_id = tree.insert("", "end", partof_root.fma, text=partof_root.desc, values=("x", "x", "x"))
node_count = node_count + 1
rec_insert(tree, partof_inclusion_list, partof_root)

# tcp_client = connect_to_server()
tree.pack()
root.mainloop()
