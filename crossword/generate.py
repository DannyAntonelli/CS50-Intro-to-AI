import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            to_remove = set()

            # Each word that hasn't the right length is added to a set
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    to_remove.add(word)

            # Each word in the set is removed from the variable's domain
            for word in to_remove:
                self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        i, j = self.crossword.overlaps[x, y]
        to_remove = set()

        if i and j:
            to_remove = set()

            # Each word in x's domain is compared with each word in y's domain
            for x_word in self.domains[x]:
                has_match = False
                for y_word in self.domains[y]:
                    if x_word[i] == y_word[j]:
                        has_match = True

                # If the word has no possible match it's added to a set of words to remove
                if not has_match:
                    to_remove.add(x_word)

        # The revision was made if the set has at least one element
        revision = len(to_remove) > 0
        for word in to_remove:
            self.domains[x].remove(word)

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initialization of the queue based on the arcs provided
        if arcs:
            queue = arcs
        else:
            queue = [(x, y) for x in self.crossword.variables for y in self.crossword.variables
            if x != y and self.crossword.overlaps[x, y]]

        while queue:
            x, y = queue.pop(0)

            # Check if any change was made
            if self.revise(x, y):
                # If there are no more words in x's domain return False
                if not self.domains[x]:
                    return False

                # Else add neighbors (different from y) to the queue
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            # If at least one variable isn't in the assignment return False
            if variable not in assignment:
                return False
        # Else return True
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if there are duplicates
        if len(list(assignment.values())) != len(set(assignment.values())):
            return False

        # Check if the length is correct
        if any(variable.length != len(word) for variable, word in assignment.items()):
            return False

        # Check if there are conflicts between neighbors
        for x in assignment:
            for y in self.crossword.neighbors(x):

                if y in assignment:
                    i, j = self.crossword.overlaps[x, y]
                    if assignment[x][i] != assignment[y][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Dictionary of the number of choices eliminated for each word
        eliminated = {}

        for v_word in self.domains[var]:
            counter = 0
            
            # Check for every neighbor which is not already assigned
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]

                    # If two words doesn't match the counter is increased
                    for n_word in self.domains[neighbor]:
                        if v_word[i] != n_word[j]:
                            counter += 1
            
            # The dictionary is updated
            eliminated[v_word] = counter

        return [w[0] for w in sorted(eliminated.items(), key=lambda x:x[1])]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = list(self.crossword.variables - assignment.keys())

        # Sort the variables by the number of values
        num_values = [(len(self.domains[var]), var) for var in unassigned]

        # Remove the elements that don't have the highest number of values
        target = min(num_values, key=lambda var: var[0])[0]
        for n, var in num_values:
            if n != target:
                unassigned.remove(var)

        # Sort the remaining variables by the number of neighbors, and return the best
        num_degrees = [(len(self.crossword.neighbors(var)), var) for var in unassigned]
        return max(num_degrees, key=lambda var: var[0])[1]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If the assignement is complete we have finished
        if self.assignment_complete(assignment):
            return assignment

        # Select a variable
        variable = self.select_unassigned_variable(assignment)

        for word in self.order_domain_values(variable, assignment):
            assignment_copy = assignment.copy()
            assignment_copy[variable] = word
            
            # Check if the word is consistent, if so change the assignment and call backtrack with the new assignment
            if self.consistent(assignment_copy):
                assignment[variable] = word
                res = self.backtrack(assignment)

                # As soon as we find an assignment that is not None, we return it
                if res:
                    return res

        # If no assignment was found, return None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
