from maze import *

m = Maze()
m.create(51, 51, Maze.Create.KRUSKAL)
m.save_maze()
# m.solve((0, 0), (20, 20), Maze.Solve.DEPTH)
# m.save_solution()
