import copy
import random
from CVRP import *
from pathplotlib import *


class Hillclimber:
    """ Solution class stores the solution and search functions """

    def __init__(self, cvrp):
        self.cvrp = cvrp


    def findSolution(self):
        print("\n\nBeginning algorithm:\nInitiating algorithm using customer angles (relative to depot position)...")
        self.initiateSolutions()
        print("Complete.")
        self.printScore()
        self.plotSolution()

        print("\nRunning local Hillclimbing algorithm...")
        self.localHillclimbing()
        print("Complete.")
        self.printScore()
        self.plotSolution()

        plt.show()


    def initiateSolutions(self):
        solution = sorted(self.cvrp.angle_matrix, key=self.cvrp.angle_matrix.get)
        # print(solution)
        del (solution[0])
        solution = [x + 1 for x in solution]
        self.current_solution = self.splitRoutes(solution)


    def localHillclimbing(self):
        """ Find a 'local' solution by optimising the individual paths,
            *without* changing the customers inside each path, changing only their order.
        1st: Try placing each customer in all possible positions on that path
        2nd: Reverse whole path sections to avoid overlap between paths """

        # Swap positions of individual customers to find the best individual paths
        for iterations in range(200):  # Repeat until no more improvements are possible

            # For each of the solution's individual paths
            for i in range(len(self.current_solution)):
                list_of_paths = []
                list_of_scores = []
                # Pick a random customer from that path
                customer_position = random.randint(1, len(self.current_solution[i]) - 2)
                # Save the customer's number
                customer = self.current_solution[i][customer_position]
                # Remove the customer from the path
                original_path = copy.deepcopy(self.current_solution[i])
                del original_path[customer_position]

                # Try inserting that customer in all possible positions on the path
                for new_position in range(1, len(original_path)):
                    edited_path = copy.deepcopy(original_path)
                    edited_path.insert(new_position, customer)
                    # Calculate and save the score for that edited version of the path
                    list_of_scores.append(self.calculateScore(edited_path[1:-1]))
                    list_of_paths.append(edited_path)

                # Choose the edited path with the lowest score
                index = np.argmin(list_of_scores)  # Find the index of the lowest score
                self.current_solution[i] = list_of_paths[index]  # Find the path with that index

        # Optimise individual paths by reversing sections of the path
        for iterations in range(200):

            # For each of the solution's individual paths
            for i in range(len(self.current_solution)):
                # Select a random section of the path
                start_of_path = random.randint(1, len(self.current_solution[i]) - 3)
                end_of_path = random.randint(start_of_path + 1, len(self.current_solution[i]) - 2)
                edited_path = copy.deepcopy(self.current_solution[i])
                # Reverse the order of the customers within that section
                reversed_section = edited_path[start_of_path:end_of_path]
                reversed_section.reverse()
                edited_path = edited_path[:start_of_path] + reversed_section + edited_path[end_of_path:]
                # Keep the edited path with the lowest score
                if self.calculateScore(edited_path[1:-1]) < self.calculateScore(self.current_solution[i][1:-1]):
                    self.current_solution[i] = edited_path


    def calculateScore(self, solution):
        # Calculates the length of a path. Input format: solution, without the Depot at the 1st and last position
        score = 0
        current_stop = 0
        idx = 0
        # Calculate the score
        while idx < len(solution):
            next_stop = solution[idx]-1
            score += self.cvrp.distance_matrix[next_stop, current_stop]
            current_stop = next_stop
            if next_stop != 0:
                idx += 1
        score += self.cvrp.distance_matrix[current_stop, 0]

        return score


    def printScore(self):
        print("Current solution:", self.current_solution)
        final_score = 0
        for i in range(len(self.current_solution)):
            final_score += self.calculateScore(self.current_solution[i][1:-1])
        print("Score:", final_score)


    def plotSolution(self):
        plotPaths(self.current_solution, self.cvrp.coords)


    def splitRoutes(self, unformatted_solution):
        """ Takes a list of customers and splits it up into truck paths, based on customer demands and truck capacity"""
        solution_score = 0
        truck_solutions = []
        new_path = [1]
        stock = self.cvrp.truck_capacity
        current_stop = 0
        idx = 0
        while idx < len(unformatted_solution):
            next_stop = unformatted_solution[idx]-1

            if stock < self.cvrp.demand[next_stop]:
                next_stop = 0
                new_path.append(1)
                truck_solutions.append(new_path)
                new_path=[]

            solution_score += self.cvrp.distance_matrix[next_stop, current_stop]

            if next_stop != 0:
                idx += 1

            current_stop = next_stop

            stock -= self.cvrp.demand[current_stop]
            if current_stop == 0:
                stock = self.cvrp.truck_capacity
            new_path.append(current_stop+1)

        final_stop = unformatted_solution[-1] - 1
        solution_score += self.cvrp.distance_matrix[final_stop, current_stop]
        new_path.append(1)
        truck_solutions.append(new_path)

        return truck_solutions