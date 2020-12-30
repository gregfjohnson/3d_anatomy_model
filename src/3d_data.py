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

class PartsListElement:
    def __str__(self):
        s = f'fma {self.fma}, 3d_rep {self.bp}, {self.desc}'
        return s

    def __repr__(self):
        return self.__str__()

    def __init__(self, text_line):
        self.fma, self.bp, self.desc = \
            re.match('^(\S+)\s(\S+)\s(.*)', text_line).groups()

class AssocParent:
    def __str__(self):
        s = f'parent_fma {self.parent_fma} ({self.parent_desc}), {len(self.child_nodes)} child node'
        if self.child_nodes != 1:
            s = s + 's'
        return s

    def __repr__(self):
        return self.__str__()

    def __init__(self, parent_fma, parent_desc):
        self.parent_fma = parent_fma
        self.parent_desc = parent_desc
        self.child_nodes = []

class AssocChild:
    def __str__(self):
        s = f'fma {self.fma}, {self.desc}'
        return s

    def __repr__(self):
        return self.__str__()

    def __init__(self, text_line):
        self.fma, self.desc = \
            re.match('.*\t([^\t]+)\t([^\t]+)$', text_line).groups()
if False:
    import pdb; pdb.set_trace()
    line = 'FMA3710	vascular tree	FMA14284	venous tree organ'
    ac = AssocChild(line)
    print(ac)
    sys.exit(0)

class AssocList:
    def __str__(self):
        s = f'parent_fma {self.parent_fma} ({self.parent_desc}), child_fma {self.child_fma}, {self.child_desc}'
        return s

    def __repr__(self):
        return self.__str__()

    def __init__(self, file):
        self.parent_nodes = {}
        lines = open(file).readlines()
        lines = [ l.strip() for l in lines]
        lines = lines[1:]

        for line in lines:
            x = AssocListElement(line)
            if not x.parent_fma in self.parent_nodes:
                self.parent_nodes[x.parent_fma] = AssocParent(x.parent_fma, x.parent_desc)
            self.parent_nodes[x.parent_fma].child_nodes.append(AssocChild(line))


class AssocListElement:
    def __str__(self):
        s = f'parent_fma {self.parent_fma} ({self.parent_desc}), child_fma {self.child_fma}, {self.child_desc}'
        return s

    def __repr__(self):
        return self.__str__()

    def __init__(self, text_line):
        self.parent_nodes = {}
        self.parent_fma, self.parent_desc, self.child_fma, self.child_desc = \
            re.match('([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)$', text_line).groups()

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
print(f'len {len(isa_parts_list)}')

for k in isa_parts_list:
    print(isa_parts_list[k])

print()

#----------------------- partof_parts_list_e.txt ------------
partof_parts_list = read_PartsList('partof_parts_list_e.txt')
print(f'len {len(partof_parts_list)}')

for k in partof_parts_list:
    print(partof_parts_list[k])

#----------------------- isa_inclusion_relation_list.txt ------------
isa_inclusion_list = AssocList('isa_inclusion_relation_list.txt')
print(f'len {len(isa_inclusion_list.parent_nodes)}')

for k in isa_inclusion_list.parent_nodes:
    print(isa_inclusion_list.parent_nodes[k])

#----------------------- partof_inclusion_relation_list.txt ------------
partof_inclusion_list = AssocList('partof_inclusion_relation_list.txt')
print(f'len {len(partof_inclusion_list.parent_nodes)}')

for k in partof_inclusion_list.parent_nodes:
    print(partof_inclusion_list.parent_nodes[k])
