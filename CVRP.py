import numpy as np
from Hillclimber import *
class CVRP:
    """ Problem class stores the CVRP paramters """

    def __init__(self, data_path):

        self.solutions = []

        """ Read the data from the file """

        f = open(data_path, 'r')  # Open the file for reading
        self.dimension = [int(s) for s in str.split(f.readline()) if s.isdigit()][0]  # Read dimension (# of customers)
        self.truck_capacity = [int(s) for s in str.split(f.readline()) if s.isdigit()][0]  # Read the truck capacity
        f.readline()  # Skip one line

        # Load the coordinates for all customers
        coords = []
        for i in range(self.dimension):
            string = f.readline()
            coords.append([int(s) for s in str.split(string)])
        self.coords = np.array(coords)[:, 1:]

        # Load the demand for all customers
        self.demand = np.genfromtxt('fruitybun250.vrp', skip_header=3 + self.dimension + 1).astype(int)[:, 1]

        # Calculate the matrix of distances between all customers
        self.createDistanceMatrix()
        # Calculate the matrix of angles between the depot and the customers
        self.createAngleMatrix()

        f.close()


    def solveProblem(self):
        self.solutions.append(Hillclimber(self))
        self.solutions[-1].findSolution()


    def printProblem(self):
        print("CVRP problem with %d customers. Truck capacity = %d" % (self.dimension, self.truck_capacity))


    def createDistanceMatrix(self):
        """ create a distance matrix for the city coords, using straight line distance """
        self.distance_matrix = {}
        for i, (x1, y1) in enumerate(self.coords):
            for j, (x2, y2) in enumerate(self.coords):
                dx, dy = x1 - x2, y1 - y2
                dist = np.sqrt(dx * dx + dy * dy)
                self.distance_matrix[i, j] = dist


    def createAngleMatrix(self):
        '''create a distance matrix for the city coords
          that uses straight line distance'''
        self.angle_matrix = {}
        for i, (x1, y1) in enumerate(self.coords):
            dx = self.coords[i][0] - self.coords[0][0]
            dy = self.coords[i][1] - self.coords[0][1]
            self.angle_matrix[i] = (np.rad2deg(np.arctan2(dy, dx)) + 360) % 360
