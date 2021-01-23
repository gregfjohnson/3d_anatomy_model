#!/usr/bin/env python3

import requests, os
import math
import sys
import numpy as np
np.set_printoptions(linewidth = 80)
import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pprint as pp
plt.ion()
# import pdb; pdb.set_trace()

isa_root = 'FMA62955'
partof_root = 'FMA20394'
# not every fma is a parent node; for example:
# FMA49908    superior pulmonary vein FMA49914    right superior pulmonary vein
#                                     ^^^^^^^^ not a parent.

class PartsListElement:
    def __str__(self):
        s = f'fma {self.fma}, 3d_rep {self.bp}, {self.desc}'
        return s

    def __repr__(self):
        return self.__str__()

    def __init__(self, text_line):
        self.fma, self.desc, self.file = \
            re.match('^(\S+)\s(\S+)\s(.*)', text_line).groups()

class AssocNode:
    def __str__(self):
        s = f'fma {self.fma} ({self.desc}), {len(self.child_nodes)} child node'
        if self.child_nodes != 1:
            s = s + 's'
        return s

    def __repr__(self):
        return self.__str__()

    def __init__(self, fma, desc):
        self.fma = fma
        self.desc = desc
        self.child_nodes = []
        self.parent_nodes = []
        self.depth = 1
        self.subtree_count = 0

    @staticmethod
    def child_fields(text_line):
        fma, desc = re.match('.*\t([^\t]+)\t([^\t]+)$', text_line).groups()
        return fma, desc

    @staticmethod
    def parent_fields(text_line):
        fma, desc = re.match('^([^\t]+)\t([^\t]+)\t', text_line).groups()
        return fma, desc

if False:
    ac = AssocNode('FMA3710', 'vascular tree')
    print(ac)
    sys.exit(0)

class AssocList:
    def __str__(self):
        return ''

    def __repr__(self):
        return self.__str__()

    def __init__(self, file):
        self.nodes = {}
        lines = open(file).readlines()
        lines = [ l.strip() for l in lines]
        lines = lines[1:]

        for line in lines:
            parent = AssocNode(*AssocNode.parent_fields(line))
            child  = AssocNode(*AssocNode.child_fields(line))

            if parent.fma in self.nodes:
                parent = self.nodes[parent.fma]
            else:
                self.nodes[parent.fma] = parent

            if child.fma in self.nodes:
                child = self.nodes[child.fma]
            else:
                self.nodes[child.fma] = child

            parent.child_nodes.append(child)
            child.parent_nodes.append(parent)

if False:
    line = 'FMA3710	BP8338	vascular tree'
    t = PartsListElement(line)
    print(t)

def read_PartsList(fname):
    lines = open(fname, 'r').readlines()
    lines = [ l.strip() for l in lines ]
    lines = lines[1:]
    list = {}
    for line in lines:
        x = PartsListElement(line)
        list[x.fma] = x

    return list

#----------------------- isa_parts_list_e.txt ------------
isa_parts_list = read_PartsList('isa_parts_list_e.txt')
"""
print(f'len {len(isa_parts_list)}')

for k in isa_parts_list:
    print(isa_parts_list[k])

print()
"""

#----------------------- partof_parts_list_e.txt ------------
partof_parts_list = read_PartsList('partof_parts_list_e.txt')
"""
print(f'len {len(partof_parts_list)}')

for k in partof_parts_list:
    print(partof_parts_list[k])
"""

#----------------------- isa_inclusion_relation_list.txt ------------
isa_inclusion_list = AssocList('isa_inclusion_relation_list.txt')
"""
print(f'len {len(isa_inclusion_list.nodes)}')

for k in isa_inclusion_list.nodes:
    print(isa_inclusion_list.nodes[k])
"""

#----------------------- partof_inclusion_relation_list.txt ------------
partof_inclusion_list = AssocList('partof_inclusion_relation_list.txt')
"""
print(f'len {len(partof_inclusion_list.nodes)}')

for k in partof_inclusion_list.nodes:
    print(partof_inclusion_list.nodes[k])
"""

def rec_loop_check(assoc_list, node):
    node.subtree_count = 1

    for child in node.child_nodes:
        if child.fma in assoc_list.nodes:
            count, d = rec_loop_check(assoc_list, assoc_list.nodes[child.fma])
            if node.depth < d+1:
                node.depth = d+1
            node.subtree_count = node.subtree_count + count

    return node.subtree_count, node.depth

def loop_check(assoc_list):
    # import pdb; pdb.set_trace()
    max_depth = 0

    for key in assoc_list.nodes:
        elt = assoc_list.nodes[key]

        count, depth = rec_loop_check(assoc_list, elt)
        if max_depth < depth:
            max_depth = depth

    return max_depth

print(f'max depth:  {loop_check(isa_inclusion_list)}')

print(f'max depth:  {loop_check(partof_inclusion_list)}')

# return fma's of (recursive) children of node
def find_children(assoc_list, node):
    result = set()

    for child in node.child_nodes:
        result = result | {child.fma}
        if child.fma in assoc_list.nodes:
            result = result | find_children(assoc_list, assoc_list.nodes[child.fma])
        result = result | find_children(assoc_list, child)

    if isa_root in result:
        print('isa_root?', node)

    return result

def rec_prt(assoc_list, node, depth=0):
    for d in range(depth):
        sys.stdout.write(' ')
    print(node)
    for child in node.child_nodes:
        rec_prt(assoc_list, child, depth+1)

# all child nodes are in the nodes list..
"""
all_children = set()
for key in isa_inclusion_list.nodes:
    value = isa_inclusion_list.nodes[key]
    all_children = all_children | find_children(isa_inclusion_list, value)

print(f'all isa children {len(all_children)}')

for key in isa_inclusion_list.nodes:
    value = isa_inclusion_list.nodes[key]
    if not key in all_children:
        print(f"not anyone's child?  {value}")

print(isa_root in all_children)
"""

# import pdb; pdb.set_trace()
print('\nisa_inclusion tree:')
key = isa_root
value = isa_inclusion_list.nodes[key]
rec_prt(isa_inclusion_list, value)
print('\ndone isa_inclusion tree\n')

print('\npartof_inclusion tree:')
key = partof_root
value = partof_inclusion_list.nodes[key]
rec_prt(partof_inclusion_list, value)
print('\ndone partof_inclusion tree\n')

def steps_to_root(node):
    steps = 0
    while len(node.parent_nodes) > 0:
        steps = steps + 1
        node = node.parent_nodes[0]
    return steps

for key in isa_inclusion_list.nodes:
    value = isa_inclusion_list.nodes[key]
    print(f'node {key}:  ' \
          + f'parent count:  {len(value.parent_nodes)}, ' \
          + f'child count:  {len(value.child_nodes)}, ' \
          + f'descendant count:  {value.subtree_count}, ' \
          + f'height:  {value.depth}, ' \
          + f'to_root:  {steps_to_root(value)}' \
          )

# FJ1252 BP7409 FMA59763

fma_fj_map = {}
fj_map_lines = [ l.strip() for l in open('fj_bp_fma.map').readlines() ]
for line in fj_map_lines:
    fj, bp, fma = re.match('(\S+)\s(\S+)\s(\S+)', line).groups()
    fma_fj_map[fma] = fj

if len(sys.argv) > 1:
    fj_files = set()

    for fma_code in sys.argv[1:]:
        node = partof_inclusion_list.nodes[fma_code]
        fma_subtree_list = find_children(partof_inclusion_list, node)

        for sub_fma in fma_subtree_list:
            if sub_fma in fma_fj_map:
                fj_files = fj_files | {fma_fj_map[sub_fma]}

    print(f'got {len(fj_files)} fj_files')
    first = True
    for fj in fj_files:
        if first:
            first = False
        else:
            sys.stdout.write(' ')

        sys.stdout.write(f'{fj}')

    print()
