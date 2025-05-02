import numpy
import random

Nd = 16  # Number of digits for a 16x16 Sudoku

class Population(object):
    """ A set of candidate solutions to the Sudoku puzzle. """

    def __init__(self):
        self.candidates = []
        return

    def seed(self, Nc, given):
        self.candidates = []

        # Determine legal values for each square.
        helper = Candidate()
        helper.values = [[[] for j in range(Nd)] for i in range(Nd)]
        for row in range(Nd):
            for column in range(Nd):
                for value in range(1, Nd + 1):
                    if (given.values[row][column] == 0 and
                        not (given.is_column_duplicate(column, value) or
                             given.is_block_duplicate(row, column, value) or
                             given.is_row_duplicate(row, value))):
                        helper.values[row][column].append(value)
                    elif given.values[row][column] != 0:
                        helper.values[row][column].append(given.values[row][column])
                        break

        # Seed a new population.
        for p in range(Nc):
            g = Candidate()
            for i in range(Nd):
                row = numpy.zeros(Nd)

                # Fill in the givens.
                for j in range(Nd):
                    if given.values[i][j] != 0:
                        row[j] = given.values[i][j]
                    else:
                        row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j]) - 1)]

                # Ensure no duplicates in the row.
                while len(list(set(row))) != Nd:
                    for j in range(Nd):
                        if given.values[i][j] == 0:
                            row[j] = helper.values[i][j][random.randint(0, len(helper.values[i][j]) - 1)]

                g.values[i] = row

            self.candidates.append(g)

        self.update_fitness()
        print("Seeding complete.")
        return

    def update_fitness(self):
        """ Update fitness of every candidate. """
        for candidate in self.candidates:
            candidate.update_fitness()
        return

    def sort(self):
        """ Sort the population based on fitness. """
        self.candidates.sort(key=lambda x: x.fitness, reverse=True)
        return

class Candidate(object):
    """ A candidate solution to the Sudoku puzzle. """
    def __init__(self):
        self.values = numpy.zeros((Nd, Nd), dtype=int)
        self.fitness = None  # Initialize fitness to None
        return

    def update_fitness(self):
        """ Calculate fitness based on Sudoku rules. """
        row_count = numpy.zeros(Nd)
        column_count = numpy.zeros(Nd)
        block_count = numpy.zeros(Nd)
        row_sum = 0
        column_sum = 0
        block_sum = 0

        # Check rows
        for i in range(Nd):
            for j in range(Nd):
                row_count[self.values[i][j] - 1] += 1
            row_sum += (1.0 / len(set(row_count))) / Nd
            row_count = numpy.zeros(Nd)

        # Check columns
        for i in range(Nd):
            for j in range(Nd):
                column_count[self.values[j][i] - 1] += 1
            column_sum += (1.0 / len(set(column_count))) / Nd
            column_count = numpy.zeros(Nd)

        # Check 4x4 blocks
        for i in range(0, Nd, 4):  # Step of 4 for 16x16 grid
            for j in range(0, Nd, 4):
                for x in range(4):
                    for y in range(4):
                        block_count[self.values[i + x][j + y] - 1] += 1
                block_sum += (1.0 / len(set(block_count))) / Nd
                block_count = numpy.zeros(Nd)

        # Calculate overall fitness
        if int(row_sum) == 1 and int(column_sum) == 1 and int(block_sum) == 1:
            fitness = 1.0
        else:
            fitness = column_sum * block_sum

        self.fitness = fitness  # Assign calculated fitness
        return

    def mutate(self, mutation_rate, given):
        """ Mutate by swapping values in a row. """
        r = random.uniform(0, 1.1)
        while r > 1:
            r = random.uniform(0, 1.1)

        success = False
        if r < mutation_rate:
            while not success:
                row1 = random.randint(0, Nd - 1)
                row2 = row1  # Swap within the same row

                from_column = random.randint(0, Nd - 1)
                to_column = random.randint(0, Nd - 1)
                while from_column == to_column:
                    from_column = random.randint(0, Nd - 1)
                    to_column = random.randint(0, Nd - 1)

                # Check if positions are free and avoid duplicates
                if (given.values[row1][from_column] == 0 and
                    given.values[row1][to_column] == 0 and
                    not given.is_column_duplicate(to_column, self.values[row1][from_column]) and
                    not given.is_column_duplicate(from_column, self.values[row2][to_column]) and
                    not given.is_block_duplicate(row2, to_column, self.values[row1][from_column]) and
                    not given.is_block_duplicate(row1, from_column, self.values[row2][to_column])):

                    # Swap values
                    temp = self.values[row2][to_column]
                    self.values[row2][to_column] = self.values[row1][from_column]
                    self.values[row1][from_column] = temp
                    success = True

        return success


class Given(Candidate):
    """ The grid containing the given/known values. """

    def __init__(self, values):
        self.values = values
        return

    def is_row_duplicate(self, row, value):
        """ Check for duplicates in a row. """
        for column in range(Nd):
            if self.values[row][column] == value:
               return True
        return False

    def is_column_duplicate(self, column, value):
        """ Check for duplicates in a column. """
        for row in range(Nd):
            if self.values[row][column] == value:
               return True
        return False

    def is_block_duplicate(self, row, column, value):
        """ Check for duplicates in a 4x4 block. """
        i = 4 * (row // 4)  # Block start row
        j = 4 * (column // 4) # Block start column

        for x in range(4):
            for y in range(4):
                if self.values[i + x][j + y] == value:
                    return True
        return False
class Tournament(object):
    """ The crossover function requires two parents to be selected. """

    def __init__(self):
        return

    def compete(self, candidates):
        """ Pick 2 random candidates and get them to compete. """
        c1 = candidates[random.randint(0, len(candidates) - 1)]
        c2 = candidates[random.randint(0, len(candidates) - 1)]
        f1 = c1.fitness
        f2 = c2.fitness

        # Find the fittest and the weakest.
        if f1 > f2:
            fittest = c1
            weakest = c2
        else:
            fittest = c2
            weakest = c1

        selection_rate = 0.85
        r = random.uniform(0, 1.1)
        while r > 1:  # Outside [0, 1] boundary. Choose another.
            r = random.uniform(0, 1.1)
        if r < selection_rate:
            return fittest
        else:
            return weakest

class CycleCrossover(object):
    """ Crossover relates to the analogy of genes within each parent
    candidate mixing together in the hopes of creating a fitter child candidate.
    """

    def __init__(self):
        return

    def crossover(self, parent1, parent2, crossover_rate):
        """ Create two new child candidates by crossing over parent genes. """
        child1 = Candidate()
        child2 = Candidate()

        # Make a copy of the parent genes.
        child1.values = numpy.copy(parent1.values)
        child2.values = numpy.copy(parent2.values)

        r = random.uniform(0, 1.1)
        while r > 1:  # Outside [0, 1] boundary. Choose another.
            r = random.uniform(0, 1.1)

        # Perform crossover.
        if r < crossover_rate:
            # Pick a crossover point. Crossover must have at least 1 row.
            crossover_point1 = random.randint(0, Nd - 1)
            crossover_point2 = random.randint(1, Nd)
            while crossover_point1 == crossover_point2:
                crossover_point1 = random.randint(0, Nd - 1)
                crossover_point2 = random.randint(1, Nd)

            if crossover_point1 > crossover_point2:
                crossover_point1, crossover_point2 = crossover_point2, crossover_point1

            for i in range(crossover_point1, crossover_point2):
                child1.values[i], child2.values[i] = self.crossover_rows(child1.values[i], child2.values[i])

        return child1, child2

    def crossover_rows(self, row1, row2):
        child_row1 = numpy.zeros(Nd)
        child_row2 = numpy.zeros(Nd)

        remaining = list(range(1, Nd + 1))
        cycle = 0

        while (0 in child_row1) and (0 in child_row2):  # While child rows not complete...
            if cycle % 2 == 0:  # Even cycles.
                index = self.find_unused(row1, remaining)
                start = row1[index]
                remaining.remove(row1[index])
                child_row1[index] = row1[index]
                child_row2[index] = row2[index]
                next_val = row2[index]

                while next_val != start:  # While cycle not done...
                    index = self.find_value(row1, next_val)
                    child_row1[index] = row1[index]
                    remaining.remove(row1[index])
                    child_row2[index] = row2[index]
                    next_val = row2[index]

                cycle += 1

            else:  # Odd cycle - flip values.
                index = self.find_unused(row1, remaining)
                start = row1[index]
                remaining.remove(row1[index])
                child_row1[index] = row2[index]
                child_row2[index] = row1[index]
                next_val = row2[index]

                while next_val != start:  # While cycle not done...
                    index = self.find_value(row1, next_val)
                    child_row1[index] = row2[index]
                    remaining.remove(row1[index])
                    child_row2[index] = row1[index]
                    next_val = row2[index]

                cycle += 1

        return child_row1, child_row2

    def find_unused(self, parent_row, remaining):
        for i in range(len(parent_row)):
            if parent_row[i] in remaining:
                return i

    def find_value(self, parent_row, value):
        for i in range(len(parent_row)):
            if parent_row[i] == value:
                return i

class Sudoku(object):
    """ Solves a given Sudoku puzzle using a genetic algorithm. """

    def __init__(self):
        self.given = None
        return

    def load(self, path):
        """ Load a Sudoku puzzle from a file. """
        with open(path, "r") as f:
            values = numpy.loadtxt(f).reshape((Nd, Nd)).astype(int)
            self.given = Given(values)
        return
    def load_grid(self, grid):
        """Load a Sudoku configuration directly from a grid.
        
        Args:
            grid: A 9x9 list of lists or 2D array representing the Sudoku puzzle.
                 Use 0 for empty cells.
        """
        values = numpy.array(grid).reshape((Nd, Nd)).astype(int)
        self.given = Given(values)
        return

    def save(self, path, solution):
        """ Save the solution to a file. """
        with open(path, "w") as f:
            numpy.savetxt(f, solution.values.reshape(Nd * Nd), fmt='%d')
        return

    def solve(self):
        """ Solve the Sudoku puzzle using a genetic algorithm. """
        Nc = 100  # Number of candidates (i.e. population size).
        Ne = int(0.07 * Nc)  # Number of elites.
        Ng = 1000  # Number of generations.
        Nm = 0  # Number of mutations.

        # Mutation parameters.
        phi = 0
        sigma = 1
        mutation_rate = 0.06

        # Create an initial population.
        self.population = Population()
        self.population.seed(Nc, self.given)

        # For up to Ng generations...
        stale = 0
        for generation in range(Ng):
            print("Generation %d" % generation)

            # Check for a solution.
            best_fitness = 0.0
            for c in range(Nc):
                fitness = self.population.candidates[c].fitness
                if fitness == 1:
                    print("Solution found at generation %d!" % generation)
                    print(self.population.candidates[c].values)
                    return self.population.candidates[c]

                # Find the best fitness.
                if fitness > best_fitness:
                    best_fitness = fitness

            print("Best fitness: %f" % best_fitness)

            # Create the next population.
            next_population = []

            # Select elites and preserve them.
            self.population.sort()
            elites = []
            for e in range(Ne):
                elite = Candidate()
                elite.values = numpy.copy(self.population.candidates[e].values)
                elites.append(elite)

            # Create the rest of the candidates.
            for count in range(Ne, Nc, 2):
                # Select parents via a tournament.
                t = Tournament()
                parent1 = t.compete(self.population.candidates)
                parent2 = t.compete(self.population.candidates)

                # Cross-over.
                cc = CycleCrossover()
                child1, child2 = cc.crossover(parent1, parent2, crossover_rate=1.0)

                # Mutate child1.
                old_fitness = child1.fitness
                success = child1.mutate(mutation_rate, self.given)
                child1.update_fitness()
                if success and old_fitness is not None:  # Check if old_fitness is not None
                    Nm += 1
                    if child1.fitness > old_fitness:
                        phi = phi + 1

                # Mutate child2.
                old_fitness = child2.fitness
                success = child2.mutate(mutation_rate, self.given)
                child2.update_fitness()
                if success and old_fitness is not None:  # Check if old_fitness is not None
                    Nm += 1
                    if child2.fitness > old_fitness:
                        phi = phi + 1

                # Add children to new population.
                next_population.append(child1)
                next_population.append(child2)

            # Append elites onto the end.
            next_population.extend(elites)

            # Select next generation.
            self.population.candidates = next_population
            self.population.update_fitness()

            # Calculate new adaptive mutation rate.
            if Nm == 0:
                phi = 0  # Avoid divide by zero.
            else:
                phi = phi / Nm

            if phi > 0.2:
                sigma = sigma / 0.998
            elif phi < 0.2:
                sigma = sigma * 0.998

            mutation_rate = abs(numpy.random.normal(loc=0.0, scale=sigma, size=None))
            Nm = 0
            phi = 0

            # Check for stale population.
            self.population.sort()
            if self.population.candidates[0].fitness != self.population.candidates[1].fitness:
                stale = 0
            else:
                stale += 1

            # Re-seed the population if stale.
            if stale >= 100:
                print("The population has gone stale. Re-seeding...")
                self.population.seed(Nc, self.given)
                stale = 0
                sigma = 1
                phi = 0
                Nm = 0
                mutation_rate = 0.06

        print("No solution found.")
        return None

# Example usage:
# s = Sudoku()
# s.load("16x16Grid.txt")  # Replace with your puzzle file
# solution = s.solve()
# if solution:
#     s.save("solution.txt", solution)