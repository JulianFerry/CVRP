import copy
import random
import numpy as np
from pathplotlib import *


class Hillclimber:
    """ Hillclimber class stores the current solution and search functions """

    def __init__(self, cvrp):
        self.cvrp = cvrp

    def findSolution(self):
        # Main function - cycles through the various heuristics to solve the problem
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

        print("\nRunning combinational Hillclimbing algorithm once (approx 1 minute)...")
        for iteration in range(50000):
            # Select two neighbouring paths at random and try to combine them in a more optimal solution
            path_one = random.randint(0, len(self.current_solution) - 1)
            path_two = (path_one + 1) % len(self.current_solution)
            self.current_solution[path_one], self.current_solution[path_two] = \
                self.combinePaths(self.current_solution[path_one], self.current_solution[path_two])
            # In the *exceptional* case that we managed to make a path completely empty (also acts as a good debugger):
            if self.current_solution[path_one] == [1, 1]:
                del self.current_solution[path_one]
                print("REMOVED path")
            if self.current_solution[path_two] == [1, 1]:
                del self.current_solution[path_two]
                print("REMOVED path")
        print("Complete.")
        self.printScore()
        self.plotSolution()

        print("\nRe-applying local Hillclimbing algorithm...")
        self.localHillclimbing()
        print("Complete.")
        self.printScore()
        self.plotSolution()
        plt.show()


    # Heuristic functions

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

        # 1: Moving individual nodes
        # Swap positions of individual customers to find the best individual paths
        for iterations in range(200):  # Repeat until no more improvements are possible

            # For each of the solution's individual paths
            for i in range(len(self.current_solution)):
                list_of_paths = []
                list_of_scores = []
                # Pick a random customer from that path
                customer_position = random.randint(1, len(self.current_solution[i]) - 2)
                # Save the customer's id
                customer = self.current_solution[i][customer_position]
                # Remove the customer from the path
                original_path = copy.deepcopy(self.current_solution[i])
                del original_path[customer_position]

                # Try inserting that customer id in all possible positions on the path
                for new_position in range(1, len(original_path)):
                    edited_path = copy.deepcopy(original_path)
                    edited_path.insert(new_position, customer)
                    # Calculate and save the score for that edited version of the path
                    list_of_scores.append(self.calculateScore(edited_path[1:-1]))
                    list_of_paths.append(edited_path)

                # Choose the edited path with the lowest score
                index = np.argmin(list_of_scores)
                self.current_solution[i] = list_of_paths[index]

        # 2: Moving multiple nodes
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


    def combinePaths(self, path_A, path_B):
        """ Takes two paths, splits them into sections, and tries to combine those sections into even better paths """

        # Save the original paths and their score - this will be used as the baseline for the newly created paths
        original_score = self.calculateScore(path_A[1:-1]) + self.calculateScore(path_B[1:-1])
        original_paths = [copy.deepcopy(path_A), copy.deepcopy(path_B)]

        # Divide the paths into 3 sections each, by creating 2 cutoff points for each path
        section_cutoffs = [[], []]
        for i in range(2):
            section_cutoffs[i].append(random.randint(1, len(original_paths[i]) - 2))
            section_cutoffs[i].append(random.randint(section_cutoffs[i][-1], len(original_paths[i]) - 2))
        sections = []
        for i in range(2):
            sections.append(original_paths[i][1:section_cutoffs[i][0]])
            sections.append(original_paths[i][section_cutoffs[i][0]:section_cutoffs[i][1]])
            sections.append(original_paths[i][section_cutoffs[i][1]:-1])

        # Construct the new path from three random sections
        # Create a matrix of the sections which is shuffled to represent their order in the newly constructed paths
        temp_indexes = list(range(0, 6))
        random.shuffle(temp_indexes)
        id_matrix = []
        for i in range(0, 6, 3):
            id_matrix.append(temp_indexes[i:i + 3])
        # Create new paths, according to the new matrix of section ids
        new_paths = [[0 for _ in range(3)] for _ in range(2)]
        for i in range(2):
            for j in range(3):
                new_paths[i][j] = (sections[id_matrix[i][j]])

        # If the demand of one of the paths is too large, choose that path to be edited
        chosen_path = -1
        for i in range(2):
            demand_i = self.calculateDemand([1] + [node for path in new_paths[i] for node in path] + [1])
            if demand_i > self.cvrp.truck_capacity:
                chosen_path = i

        # Shorten chosen_path (if the paths are of the right length, then chosen_path is -1 and this part is skipped)
        if chosen_path >= 0:
            # While the path is too big
            while (self.calculateDemand([1] + [node for path in new_paths[chosen_path] for node in path] + [1]))  \
                    > self.cvrp.truck_capacity:

                # Choose one of the three sections from the new path at random (make sure it isn't an empty section)
                chosen_section = random.randint(0, 2)
                while not new_paths[chosen_path][chosen_section]:
                    chosen_section = random.randint(0, 2)
                # Find what section id that corresponds to
                section_id = id_matrix[chosen_path][chosen_section]  # Index of the chosen section
                path_origin = int(section_id / 3)  # Sections 0 -> 2 came from path A, Sections 3 -> 5 came from path B

                # Prepare to shorten the chosen section by changing the cutoff value
                if (section_id % 3) == 0:
                    # Shorten section 1 (start of the path) by changing the cutoff value for the end of that section
                    section_cutoffs[path_origin][0] -= 1
                elif (section_id % 3) == 2:
                    # Change section 3 (end of the path) by changing the cutoff value for the start of that section
                    section_cutoffs[path_origin][1] += 1
                elif (section_id % 3) == 1:
                    # Change section 2 (middle of the path) by changing either the start or end cutoff of that section
                    if random.randint(0, 1) == 0:
                        section_cutoffs[path_origin][0] += 1
                    else:
                        section_cutoffs[path_origin][1] -= 1

                # Re-create the path sections with the new cutoff values
                sections = [original_paths[0][1:section_cutoffs[0][0]],
                            original_paths[0][section_cutoffs[0][0]:section_cutoffs[0][1]],
                            original_paths[0][section_cutoffs[0][1]:-1]]  \
                         + [original_paths[1][1:section_cutoffs[1][0]],
                            original_paths[1][section_cutoffs[1][0]:section_cutoffs[1][1]],
                            original_paths[1][section_cutoffs[1][1]:-1]]
                # Reconstruct the chosen path
                for i in range(3):
                    new_paths[chosen_path][i] = sections[id_matrix[chosen_path][i]]

        # Reconstruct the other path from the remaining sections - (x+1)%2 selects the other path (0 -> 1 or 1 -> 0)
        for i in range(3):
            new_paths[(chosen_path + 1) % 2][i] = sections[id_matrix[(chosen_path + 1) % 2][i]]
        output_path = [[], []]
        output_path[0] = [1] + [node for path in new_paths[chosen_path] for node in path] + [1]
        output_path[1] = [1] + [node for path in new_paths[(chosen_path + 1) % 2] for node in path] + [1]

        # Now check that both paths do not go over the truck's capacity
        demand_A, demand_B = self.calculateDemand(output_path[0]), self.calculateDemand(output_path[1])
        if demand_A <= self.cvrp.truck_capacity and demand_B <= self.cvrp.truck_capacity:
            for path_nr in range(2):

                # Create 8 different combinations of A, B, C and their inverse (refer to documentation)
                A = [new_paths[path_nr][0] if (i < 4) else list(reversed(new_paths[path_nr][0])) for i in range(8)]
                B = [new_paths[path_nr][1] if (i % 4 >= 2) else list(reversed(new_paths[path_nr][1])) for i in range(8)]
                C = [new_paths[path_nr][2] if (i % 2 == 0) else list(reversed(new_paths[path_nr][2])) for i in range(8)]

                # Evaluate all 8 combinations
                output_path[path_nr] = [1] + A[0] + B[0] + C[0] + [1]
                min_score = self.calculateScore(output_path[path_nr][1:-1])
                for i in range(1, 8):
                    temp_score = self.calculateScore(A[i] + B[i] + C[i])
                    if temp_score < min_score:
                        min_score = temp_score
                        output_path[path_nr] = [1] + A[i] + B[i] + C[i] + [1]
                    temp_score = self.calculateScore(A[i] + C[i] + B[i])
                    if temp_score < min_score:
                        min_score = temp_score
                        output_path[path_nr] = [1] + A[i] + C[i] + B[i] + [1]
                    temp_score = self.calculateScore(B[i] + A[i] + C[i])
                    if temp_score < min_score:
                        min_score = temp_score
                        output_path[path_nr] = [1] + B[i] + A[i] + C[i] + [1]

            new_score = self.calculateScore(output_path[0][1:-1]) + self.calculateScore(output_path[1][1:-1])
            # Successful improvement:
            if (new_score < original_score):
                return output_path[0], output_path[1]
            # No improvement, return original paths
            else:
                return path_A, path_B
        else:
            return path_A, path_B                   # The paths were over capacity


    # Helper functions

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

    def calculateScore(self, solution):
        # Calculates the length of a path. Input format: solution, without the Depot (1) at the 1st and last position
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

    def calculateDemand(self, path):
        path_demand = 0
        for i in range(1, len(path)):
            path_demand += self.cvrp.demand[path[i] - 1]
        return path_demand


    def plotSolution(self):
        plotPaths(self.current_solution, self.cvrp.coords)




