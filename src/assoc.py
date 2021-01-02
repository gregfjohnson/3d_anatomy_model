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

        # obtain an arbitrary
        for r in self.nodes:
            root = self.nodes[r]
            break
        while len(root.parent_nodes) > 0:
            root = root.parent_nodes[0]

        self.set_subtree_counts(root)

    def set_subtree_counts(self, node):
        node.subtree_count = 1

        for child in node.child_nodes:
            if child.fma in self.nodes:
                child_node = self.nodes[child.fma]
                self.set_subtree_counts(child_node)
                node.subtree_count = node.subtree_count + child_node.subtree_count

