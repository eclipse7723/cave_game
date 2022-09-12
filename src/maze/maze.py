import numpy as np
import collections
import random

import src.maze.utils as utils
import src.maze.base as base


class Maze(base.MazeBase):
    """This class contains the relevant algorithms for creating and solving."""
    def __init__(self):
        """Constructor."""
        super(Maze, self).__init__()

        self._dir_one = [
            lambda x, y: (x + 1, y),
            lambda x, y: (x - 1, y),
            lambda x, y: (x, y - 1),
            lambda x, y: (x, y + 1)
        ]
        self._dir_two = [
            lambda x, y: (x + 2, y),
            lambda x, y: (x - 2, y),
            lambda x, y: (x, y - 2),
            lambda x, y: (x, y + 2)
        ]
        self._range = list(range(4))

    def create(self, row_count, col_count, algorithm):
        """Creates a maze for a given row and column count."""
        if (row_count or col_count) <= 0:
            raise utils.MazeError("Row or column count cannot be smaller than zero.")

        self.maze = np.zeros((row_count, col_count , 3), dtype=np.uint8)

        if algorithm == Maze.Create.KRUSKAL:
            return self._kruskal()

        raise utils.MazeError(
            "Wrong algorithm <{}>.\n"
            "Use \"Maze.Create.<algorithm>\" to choose an algorithm.".format(algorithm)
        )

    @property
    def _random(self):
        """Returns a random range to iterate over."""
        random.shuffle(self._range)
        return self._range

    def _out_of_bounds(self, x, y):
        """Checks if indices are out of bounds."""
        return x < 0 or y < 0 or x >= self.row_count_with_walls or y >= self.col_count_with_walls

    def solve(self, start, end, algorithm):
        """Solves a maze from start to finish."""
        if self.maze is None:
            raise utils.MazeError(
                "Maze is not assigned.\n"
                "Use the \"create\" or \"load_maze\" method to create or load a maze."
            )

        start = start if start else (0, 0)
        end = end if end else (self.row_count - 1, self.col_count - 1)

        if not (0 <= start[0] < self.row_count and 0 <= start[1] < self.col_count):
            raise utils.MazeError("Start point <{}> is out of range.".format(start))
        if not (0 <= end[0] < self.row_count and 0 <= end[1] < self.col_count):
            raise utils.MazeError("End point <{}> is out of range.".format(end))

        start = tuple([x for x in start])
        end = tuple([x  for x in end])

        self.solution = self.maze.copy()

        if algorithm == Maze.Solve.C:
            return self._depth_first_search_c(start, end)
        if algorithm == Maze.Solve.DEPTH:
            return self._depth_first_search(start, end)
        if algorithm == Maze.Solve.BREADTH:
            return self._breadth_first_search(start, end)

        raise utils.MazeError(
            "Wrong algorithm <{}>.\n"
            "Use \"Algorithm.Solve.<algorithm>\" to choose an algorithm.".format(algorithm)
        )


    def _kruskal(self):
        """Creates a maze using Kruskal's algorithm."""
        xy_to_set = np.zeros((self.row_count_with_walls, self.col_count_with_walls), dtype=np.uint32)
        set_to_xy = []  # List of sets in order, set 0 at index 0 [[(x, y),...], ...]
        edges = collections.deque()  # List of possible edges [(x, y, direction), ...]
        set_index = 0

        for x in range(1, self.row_count_with_walls - 1, 2):
            for y in range(1, self.col_count_with_walls - 1, 2):
                # Assign sets
                xy_to_set[x, y] = set_index
                set_to_xy.append([(x, y)])
                set_index += 1

                # Create edges
                if not self._out_of_bounds(x + 2, y):
                    edges.append((x + 1, y, "v"))  # Vertical edge
                if not self._out_of_bounds(x, y + 2):
                    edges.append((x, y + 1, "h"))  # Horizontal edge

        random.shuffle(edges)  # Shuffle to pop random edges
        while edges:
            x, y, direction = edges.pop()

            x1, x2 = (x - 1, x + 1) if direction == "v" else (x, x)
            y1, y2 = (y - 1, y + 1) if direction == "h" else (y, y)

            if xy_to_set[x1, y1] != xy_to_set[x2, y2]:  # Check if cells are in different sets
                self.maze[x, y] = self.maze[x1, y1] = self.maze[x2, y2] = [255, 255, 255]  # Mark as visited

                new_set = xy_to_set[x1, y1]
                old_set = xy_to_set[x2, y2]

                # Extend new set with old set
                set_to_xy[new_set].extend(set_to_xy[old_set])

                # Correct sets in xy sets
                for pos in set_to_xy[old_set]:
                    xy_to_set[pos] = new_set

    def _depth_first_search_c(self, start, end):
        """Solves a maze using depth-first search in C."""
        start = start[0] * self.col_count_with_walls + start[1]
        end = end[0] * self.col_count_with_walls + end[1]

        self.solution = self.solution.flatten()
        self.get_dll().depth_first_search(
            self.maze[:, :, ::3].flatten(), self.solution, self.col_count, start, end
        )
        self.solution = self.solution.reshape((self.row_count_with_walls, self.col_count_with_walls, 3))

    def _solve_walk(self, x, y, visited):
        """Walks over a maze."""
        for idx in range(4):  # Check adjacent cells
            bx, by = self._dir_one[idx](x, y)
            if visited[bx, by, 0] == 255:  # Check if unvisited
                tx, ty = self._dir_two[idx](x, y)
                visited[bx, by, 0] = visited[tx, ty, 0] = 0  # Mark as visited
                return tx, ty  # Return new cell

        return None, None  # Return stop values

    def _solve_backtrack(self, stack, visited):
        """Backtracks a stacks."""
        while stack:
            x, y = stack.pop()
            for direction in self._dir_one:  # Check adjacent cells
                tx, ty = direction(x, y)
                if visited[tx, ty, 0] == 255:  # Check if unvisited
                    return x, y  # Return cell with unvisited neighbour

        return None, None  # Return stop values if stack is empty and no new cell was found

    def _depth_first_search(self, start, end):
        """Solves a maze using depth-first search."""
        visited = self.maze.copy()  # List of visited cells, value of visited cell is 0
        stack = collections.deque()  # List of visited cells [(x, y), ...]

        x, y = start
        visited[x, y, 0] = 0  # Mark as visited

        while x and y:
            while x and y:
                stack.append((x, y))
                if (x, y) == end:  # Stop if end has been found
                    return utils.draw_path(self.solution, stack)
                x, y = self._solve_walk(x, y, visited)
            x, y = self._solve_backtrack(stack, visited)

        raise utils.MazeError("No solution found.")

    def _enqueue(self, queue, visited):
        """Queues next cells."""
        cell = queue.popleft()
        x, y = cell[0]
        for idx in range(4):  # Check adjacent cells
            bx, by = self._dir_one[idx](x, y)
            if visited[bx, by, 0] == 255:  # Check if unvisited
                tx, ty = self._dir_two[idx](x, y)
                visited[bx, by, 0] = visited[tx, ty, 0] = 0  # Mark as visited
                queue.append(utils.stack_push(cell, (tx, ty)))

    def _breadth_first_search(self, start, end):
        """Solves a maze using breadth-first search."""
        visited = self.maze.copy()  # List of visited cells, value of visited cell is 0
        queue = collections.deque()  # List of cells [cell, ...]
        cell = utils.stack_empty()  # Tuple of current cell with according stack ((x, y), stack)

        x, y = start
        cell = utils.stack_push(cell, (x, y))
        queue.append(cell)
        visited[x, y, 0] = 0  # Mark as visited

        while queue:
            self._enqueue(queue, visited)
            if queue[0][0] == end:  # Stop if end has been found
                cell = utils.stack_push(queue[0], end)  # Push end into cell
                return utils.draw_path(self.solution, utils.stack_deque(cell))

        raise utils.MazeError("No solution found.")
