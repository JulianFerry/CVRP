# CVRP

The capacitated vehicle routing problem (CVRP) is an [NP-hard](https://en.wikipedia.org/wiki/NP-hardness) optimisation problem. A depot has to deliver goods to its customers, using the shortest path possible.

The depot and the customers are placed on a 2D map. Each customer has a demand of X goods. Each truck, however, has a limited capacity. Therefore the depot has to send multiple trucks to deliver its goods. The best solution is the one that minimises the combined distance covered by these trucks (further requirements could be added such as minimising the number of trucks).

Using a stochastic approach is unlikely to find the optimal solution for this problem, since the search-space is very large. [Therefore an optimisation heuristic is required](https://en.wikipedia.org/wiki/Heuristic_(computer_science)).


## My solution (in progress):

To solve the CVRP, I used an algorithm which runs two different specialised Hillclimbing algorithms in series. Initial attempts included using a Genetic Algorithm, however the problem encountered by general Genetic Algorithms for this problem is that changing just one gene can change the whole solution (as well as the fact that it creates many invalid solutions - dealing with this is a whole problem of its own).

By contrast, the Hillclimber can keep evaluating the validity and score of neighbouring solutions and can converge to a local optimum.
The algorithm finds a very good local optimum, which the human eye could not improve. The advantage of this algorithm is that most local optimums in the CVRP have very similar scores, therefore it gives very consistent results. The drawback of this solution is that because there are so many possible permutations, rerunning the algorithm multiple times is very unlikely to find the CVRP’s global optimum.


### How the algorithm works:

#### Initialisation:

After delivering to customers, each truck has to return to the depot. To minimise the distance covered per customer, the truck should also deliver buns to customers on its way back. A straight line is the fastest path back to the depot; therefore, we need to ensure that there are customers on this line.

To start doing so, we calculate the angle of each customer relative to the depot. A path is then created by taking all customers with similar angles, which are therefore at the same position relative to the depot. The path stops once the customers’ total demand exceeds the truck’s capacity. Then the next truck takes off where the last path stopped.

<img src="https://github.com/JulianFerry/CVRP-/blob/master/images/initiateSolutions.png">

#### Local Hillclimbing:

After initialising the routes, it is apparent that each individual route can be optimised. The Hillclimbing algorithm for this is simple:
```
for each Path:
    select random Customer
    remove Customer from Path
    for all possible positions in Path:
        insert Customer at new Position
    keep Position which gives the shortest Path Distance
 ```
    
This is iterated a few hundred times, and only requires a few seconds to run.
However, after this stage it already finds a path distance of around 6600.
Figure 2 shows that this creates a round-trip which has a very small total distance - since the customers were previously limited to a small range of angles relative to the depot.

<img src="https://github.com/JulianFerry/CVRP-/blob/master/images/localHillclimbing.png" width="720px">

#### Exploratory Hillclimbing:

Once the distance of each individual path has been optimised, the next step is to combine paths together, to try to find the best set of paths with the lowest combined distance. This is done by selecting two neighbouring paths and combining sections of each path together to create a new path. The challenge of this algorithm is that combining random path sections can create a new path with a customer demand larger than the truck capacity. The algorithm addresses this by progressively removing a customer from the end of each section, until the demand of that path is smaller than the truck capacity.

The algorithm: 

```
Two neighbouring paths are selected.
The paths are divided into three sections each. 
The length of each section is chosen at random (this can also be zero - therefore only creating two sections). 
A new path is then created by randomly selecting three of the six sections.
The other path is created by combining the three remaining sections.
```

For example:
If a path is composed of sections A, B and C, then there are 3 possible permutations of those sections: ABC, ACB, BAC (the mirrored versions - CBA, BCA, CAB are ignored).

Each path section can also be inverted. For example, if A = [1->2->3->1], Å = [1->3->2->1]. This means that for each permutation (e.g. BAC) there are 2^3 = 8 versions (e.g. BÅC) of that permutation. 

This gives a total of 3*8 = 24 different versions for that path. The algorithm keeps the new path with the lowest distance.
```

The longer this iterates for, the better the results will become.

<img src="https://github.com/JulianFerry/CVRP-/blob/master/images/exploratoryHillclimbing.png" width="400px">

After iteration is done, the Local Hillclimbing algorithm is run again to minimise distance covered by each newly created path.


## Possible improvements:

The algorithm is constrained to a local search due to the systematic initialisation. A better way of initialising the solutions (still using the angles) would be to randomly select the starting point for the creation of paths. Perhaps there are also better initialisations than using angles as a starting point.

To improve the algorithm itself, the demand of each truck could been taken into account, to reduce the number of trucks used from 26 to 25.
