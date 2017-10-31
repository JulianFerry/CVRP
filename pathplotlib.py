import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from random import randint
import numpy as np

colours = []
for i in range(10):
    colours.append('%06X' % randint(0, 0xFFFFFF))

plt.gca().set_color_cycle(colours)

def plotPaths(solution_paths, coordinates):
    coordinates = np.concatenate(([[0,0]], coordinates))
    plt.clf()
    for path in solution_paths: # For each truck path
        x_path = []
        y_path = []
        for customer in path:   # ... and repeat until the path is completed
            x_path.append(coordinates[customer][0])
            y_path.append(coordinates[customer][1])
            plt.plot(x_path,y_path, linewidth=0.8)

    plt.pause(0.1)
    plt.show(block=False)