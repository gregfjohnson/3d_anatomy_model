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
def rec_update_select_states(gui_tree, data_parent, fj_files):
    item_dict = gui_tree.item(data_parent.fma)
    values = item_dict['values']

    if len(data_parent.fj_files) > 0:
        if data_parent.fj_files.issubset(gui_tree.fj_files):
            values[1] = '*'
        else:
            values[1] = ' '

        gui_tree.item(data_parent.fma, values=values)

    for child in data_parent.child_nodes:
        rec_update_implied_states(gui_tree, child)

# insert elements into the GUI TreeView object.
#
def rec_insert(gui_tree, assoc_list, parent_data_node):
    for child in parent_data_node.child_nodes:
        # import pdb; pdb.set_trace()
        child.fj_files = fma_to_filename([child.fma])
        if len(child.fj_files) > 0:
            values = ("x", " ", " ")
        else:
            values = (" ", " ", " ")
        child.tree_id = gui_tree.insert(parent_data_node.tree_id, "end", \
                                        child.fma, text=child.desc, \
                                        values=values)
        rec_insert(gui_tree, assoc_list, child)

def activate_exit():
    os.system('killall obj_view 2> /dev/null')
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

def button3(event):
    global tree

    print('right mouse button!', event, tree.identify_region(event.x, event.y))
    print('more right mouse button!', tree.identify_element(event.x, event.y))
    print(f'row {tree.identify_row(event.y)}, col {tree.identify_column(event.x)}')

    tree.button_event = event
    update_selection(tree, tree.identify_row(event.y), event)

tree.bind('<Button-1>', button1)
tree.bind('<Button-3>', button3)

def has_selected_subtrees(tree, node):
    item_dict = tree.item(node.fma)
    values = item_dict['values']

    if values[0][0] == '*':
        return True

    for c in node.child_nodes:
        if has_selected_subtrees(tree, c):
            return True

    return False

def update_subtree_states(tree, node, new_state):
    item_dict = tree.item(node.fma)
    values = item_dict['values']

    if new_state == True and values[0][0] == 'x':
        tree.fma_selections = tree.fma_selections | {node.fma}
        update_select_state(node, True)

    elif new_state == False and values[0][0] == '*':
        tree.fma_selections = tree.fma_selections - {node.fma}
        update_select_state(node, False)

    for c in node.child_nodes:
        update_subtree_states(tree, c, new_state)

def update_selection(tree, fma, event):
    item_dict = tree.item(fma)
    values = item_dict['values']

    print(f'identify_element:  {tree.identify_element(event.x, event.y)}')
    print(f'identify_row:  {tree.identify_row(event.y)}')
    print(f'selection:  {fma}') 
    print(f'item:  {tree.item(fma)}')

    # import pdb; pdb.set_trace()

    prev_set_count = len(tree.fma_selections)

    # right-button click on any select entry clears its subtree.
    # left-button click on blank select entry enables its subtree.
    #
    if values[0][0] == ' ' or tree.button_event.num == 3:
        new_state = tree.button_event.num == 1  # left-mouse
        update_subtree_states(tree, inclusion_list.nodes[fma], new_state)

    # left-button click on a select entry with associated
    # fj files toggles the state of that one entry.
    #
    else:
        if values[0][0] == 'x':
            tree.fma_selections = tree.fma_selections | {fma}
            new_state = True
        elif values[0][0] == '*':
            tree.fma_selections = tree.fma_selections - {fma}
            new_state = False

        update_select_state(inclusion_list.nodes[fma], new_state)

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

def TreeviewSelect(event):
    global tree
    print('TreeviewSelect!', event, tree.button_event)
    event = tree.button_event

    # the "Select" column was moused
    #
    if tree.identify_column(event.x) == '#1':
        fma = tree.selection()[0]
        update_selection(tree, fma, event)

        """
        item_dict = tree.item(fma)
        values = item_dict['values']

        print(f'identify_element:  {tree.identify_element(event.x, event.y)}')
        print(f'identify_row:  {tree.identify_row(event.y)}')
        print(f'selection:  {fma}') 
        print(f'item:  {tree.item(fma)}')

        # import pdb; pdb.set_trace()

        prev_set_count = len(tree.fma_selections)

        # right-button click on any select entry clears its subtree.
        # left-button click on blank select entry enables its subtree.
        #
        if values[0][0] == ' ' or tree.button_event.num == 3:
            new_state = tree.button_event.num == 1  # left-mouse
            update_subtree_states(tree, inclusion_list.nodes[fma], new_state)

        # left-button click on a select entry with associated
        # fj files toggles the state of that one entry.
        #
        else:
            if values[0][0] == 'x':
                tree.fma_selections = tree.fma_selections | {fma}
                new_state = True
            elif values[0][0] == '*':
                tree.fma_selections = tree.fma_selections - {fma}
                new_state = False

            update_select_state(inclusion_list.nodes[fma], new_state)

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
        """

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
    values = ("x", " ", " ")
else:
    values = (" ", " ", " ")
partof_root.tree_id = tree.insert("", "end", partof_root.fma,
                                  text=partof_root.desc,
                                  values=values)
rec_insert(tree, inclusion_list, partof_root)

# each node has zero of more subtree nodes (not counting itself)
# that have one or more fj_files and are selectable.

def rec_selectable_subtree_count(inclusion_list, data_node):
    selectable_subtree_count = 0
    for child in data_node.child_nodes:
        if len(child.fj_files) > 0:
            selectable_subtree_count = selectable_subtree_count + 1

        rec_selectable_subtree_count(inclusion_list, child)
        selectable_subtree_count = selectable_subtree_count + child.selectable_subtree_count

    data_node.selectable_subtree_count = selectable_subtree_count

rec_selectable_subtree_count(inclusion_list, partof_root)

def update_select_state(data_node, state):
    item_dict = tree.item(data_node.fma)
    values = item_dict['values']

    if len(data_node.fj_files) == 0:
        new_value = ' '
    elif state:
        new_value = '*'
    else:
        new_value = 'x'

    if data_node.selectable_subtree_count > 0:
        new_value = new_value + f' ({data_node.selectable_subtree_count})'

    values[0] = new_value
    tree.item(data_node.fma, values=values)

for node in inclusion_list.nodes:
    update_select_state(inclusion_list.nodes[node], False)

# tcp_client = connect_to_server()
tree.pack()
root.mainloop()
