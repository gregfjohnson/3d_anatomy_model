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
import pprint as pp
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

use_isa = False

for arg in sys.argv:
    if arg == '--isa':
        use_isa = True

if use_isa:
    inclusion_list = assoc.AssocList('isa_inclusion_relation_list.txt')
else:
    inclusion_list = assoc.AssocList('partof_inclusion_relation_list.txt')

print(f'inclusion_list count:  {len(inclusion_list.nodes)}')
for key in inclusion_list.nodes:
    if len(inclusion_list.nodes[key].parent_nodes) == 0:
        partof_root = inclusion_list.nodes[key]
        break

# update selection status of elements in the GUI GTreeView object.
# based on the tree's current fma_selection.
def rec_update_implied_states(gui_tree, data_parent):
    item_dict = gui_tree.item(data_parent.fma)
    values = item_dict['values']

    if len(data_parent.fj_files) > 0:
        if data_parent.fj_files.issubset(tree.fj_files):
            values[1] = '*'
        else:
            values[1] = ' '

        tree.item(data_parent.fma, values=values)

    for child in data_parent.child_nodes:

        rec_update_implied_states(tree, child)

# insert elements into the GUI GTreeView object.
def rec_insert(tree, assoc_list, parent_node):
    for child in parent_node.child_nodes:
        # import pdb; pdb.set_trace()
        child.fj_files = fma_to_filename([child.fma])
        if len(child.fj_files) > 0:
            values = ("x", " ", " ")
        else:
            values = (" ", " ", " ")
        child.tree_id = tree.insert(parent_node.tree_id, "end", \
                                    child.fma, text=child.desc, \
                                    values=values)
        rec_insert(tree, assoc_list, child)

def activate_exit():
    os.system('killall obj_view')
    root.destroy()
    sys.exit(0)

root = Tk()
root.minsize(width=800, height=500)
root.protocol("WM_DELETE_WINDOW", activate_exit)

tree = ttk.Treeview(root, height=500, selectmode="browse", columns=("Select", "Implied", "Identify"))
tree.column("#0", width=700, minwidth=700)

tree.fma_selections = set()
tree.fj_files = set()

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

        # import pdb; pdb.set_trace()

        prev_set_count = len(tree.fma_selections)

        if values[0] == 'x':
            values[0] = '*'
            tree.fma_selections = tree.fma_selections | {fma}
        elif values[0] == '*':
            values[0] = 'x'
            tree.fma_selections = tree.fma_selections - {fma}

        tree.item(tree.selection(), values=values)
        print(f'new fma_selections:  {tree.fma_selections}')

        if prev_set_count != len(tree.fma_selections):
            os.system('killall obj_view')

            print(f'prev fj files:  {tree.fj_files}')
            tree.fj_files = fma_to_filename(list(tree.fma_selections))
            print(f'updated fj files:  {tree.fj_files}')

            rec_update_implied_states(tree, partof_root)

            if len(tree.fj_files) > 0:
                fj_file_string = ' '.join(tree.fj_files)
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

tree.column("Implied", width=sel_width, minwidth=sel_width)
tree.heading("Implied", text="Implied")

tree.column("Identify", width=sel_width, minwidth=sel_width)
tree.heading("Identify", text="Identify")

partof_root.fj_files = fma_to_filename([partof_root.fma])

if len(partof_root.fj_files) > 0:
    partof_root.tree_id = tree.insert("", "end", partof_root.fma,
                                      text=partof_root.desc,
                                      values=("x", " ", " "))

rec_insert(tree, inclusion_list, partof_root)

# tcp_client = connect_to_server()
tree.pack()
root.mainloop()
