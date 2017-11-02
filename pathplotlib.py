import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from random import randint
import numpy as np

# Create an array of colours so that the paths are plotted in a consistent manner
colours = []
for i in range(10):
    colours.append('%06X' % randint(0, 0xFFFFFF))
plt.gca().set_color_cycle(colours)

""" Plots the paths and the customers using matplotlib. Non blocking, although it's a bit temperamental """
def plotPaths(solution_paths, coordinates):
    plt.clf()
    # Add dummy data at position 0 so that index 1 = customer 1
    coordinates = np.concatenate(([[0,0]], coordinates))
    # For each truck path...
    for path in solution_paths:
        x_path = []
        y_path = []
        # ... split the x and y coordinates ...
        for customer in path:
            x_path.append(coordinates[customer][0])
            y_path.append(coordinates[customer][1])
        # ... and plot that path.
        plt.plot(x_path,y_path, linewidth=0.8, zorder=-1)

    # Plot all the customer nodes on top of the paths
    plt.scatter(coordinates[1][0], coordinates[1][1], s=50, edgecolors="black", facecolors="black")
    for customer in coordinates[2:]:
        plt.scatter(customer[0], customer[1], s=1, edgecolors="black")
    # Non-blocking. Still causes some sort of lag, maybe improve this?
    plt.pause(0.1)
    plt.show(block=False)