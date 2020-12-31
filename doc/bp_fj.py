#!/usr/bin/env python3

import requests, os
import math
import sys
import numpy as np
np.set_printoptions(linewidth = 80)
from scipy import signal, stats
import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
plt.ion()

flines = open('partof_summary').readlines()
lines = [ l.strip() for l in flines ]
print(lines)

for i in range(0, len(lines), 5):
    print(re.sub('.*: ', '', lines[i]), \
          re.sub('.*: ', '', lines[i+1]), \
          re.sub('.*: ', '', lines[i+2]))
