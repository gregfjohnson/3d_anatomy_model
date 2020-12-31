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

lines = [ l.strip() for l in open(sys.argv[1]).readlines() ]

for i in range(0, len(lines), 5):
    print(  f"{re.sub('.*: ', '', lines[i])} " \
          + f"{re.sub('.*: ', '', lines[i+1])} " \
          + f"{re.sub('.*: ', '', lines[i+2])} ")
