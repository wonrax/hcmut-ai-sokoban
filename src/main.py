import sys
import os
import time

# Map symbol constants used in parsing maze from file
MAZE_HERO       = 'X'
MAZE_SPACE      = ' '
MAZE_WALL       = '#'
MAZE_BOX        = 'U'
MAZE_SHELF      = '*'
MAZE_SHELF_BOX  = 'O'       # the shelf with box

class Move:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

class Maze:
    def __init__(self, mapFilePath) -> None:
        # Width and height of the bounding box (also the size of the 2D array)
        self.height = 0
        self.width = 0

        # Number of shelves
        self.shelves = 0

        # Number of boxes
        self.boxes = 0

        # Number of shelfbox (the shelves that are filled with box)
        self.shelfbox = 0

        with open(mapFilePath, "r") as txt_file:
            lines = txt_file.readlines()
            str_maze = []
            for line in lines:
                line = line.rstrip()
                if not line:
                    continue
                self.height += 1
                str_maze.append(line)
                self.width = max(self.width, len(line))

        self.maze = [None] * self.height
        for i in range(len(str_maze)):
            row = str_maze[i]
            self.maze[i] = [MAZE_SPACE] * self.width
            for x in range(len(row)):
                c = row[x]
                if c == MAZE_HERO:
                    self.hero_x = x
                    self.hero_y = i
                    c = MAZE_SPACE
                elif c == MAZE_SHELF:
                    self.shelves += 1
                elif c == MAZE_BOX:
                    self.boxes += 1
                elif c == MAZE_SHELF_BOX:
                    self.shelfbox += 1
                    self.shelves += 1
                    self.boxes += 1
                self.maze[i][x] = c
    
    def move(self, nextMove: Move) -> bool:
        facingObject_x = -1
        facingObject_y = -1
        nextFacingObject_x = -1
        nextFacingObject_y = -1
        if nextMove == Move.LEFT:
            facingObject_x = self.hero_x - 1
            facingObject_y = self.hero_y
            nextFacingObject_x = facingObject_x - 1
            nextFacingObject_y = facingObject_y
        elif nextMove == Move.RIGHT:
            facingObject_x = self.hero_x + 1
            facingObject_y = self.hero_y
            nextFacingObject_x = facingObject_x + 1
            nextFacingObject_y = facingObject_y
        elif nextMove == Move.UP:
            facingObject_x = self.hero_x
            facingObject_y = self.hero_y - 1
            nextFacingObject_x = facingObject_x
            nextFacingObject_y = facingObject_y - 1
        elif nextMove == Move.DOWN:
            facingObject_x = self.hero_x
            facingObject_y = self.hero_y + 1
            nextFacingObject_x = facingObject_x
            nextFacingObject_y = facingObject_y + 1
        
        if self.maze[facingObject_x][facingObject_y] in [MAZE_SPACE, MAZE_SHELF]:
            self.hero_x = facingObject_x
            self.hero_x = facingObject_y
        elif self.maze[facingObject_x][facingObject_y] == MAZE_BOX:
            if self.maze[nextFacingObject_x][nextFacingObject_y] in [MAZE_BOX, MAZE_SHELF_BOX, MAZE_WALL]:
                return False
            else:
                self.hero_x = facingObject_x
                self.hero_x = facingObject_y
                self.maze[facingObject_x][facingObject_y] = MAZE_SPACE
                self.maze[nextFacingObject_x][nextFacingObject_y] = MAZE_BOX
                return True
        return False

    def movable(nextMove):
        pass

def drawMaze(maze):
    os.system('cls||clear')
    # if not noClear:
    #     cursor_up = '\x1b[1A';
    #     erase_line = '\x1b[2K';
    #     print((cursor_up + erase_line)*height + cursor_up);

    symbolMappings = {MAZE_HERO: "☻", MAZE_BOX: "U", MAZE_WALL: "█", MAZE_SPACE: " ", MAZE_SHELF: "*", MAZE_SHELF_BOX: "O"}
    for i, row in enumerate(maze.maze):
        for j, c in enumerate(row):
            if maze.hero_x == i and maze.hero_y == j:
                print(symbolMappings[MAZE_HERO])
            else:
                print(symbolMappings[c], end="")
        print("")
        

maze = Maze("src/map.txt")
drawMaze(maze)
time.sleep(0.2)
print(maze.move(Move.LEFT))
drawMaze(maze)
time.sleep(10)
print(maze.move(Move.RIGHT))
drawMaze(maze)
time.sleep(0.2)
print(maze.move(Move.UP))
drawMaze(maze)
time.sleep(0.2)
print(maze.move(Move.DOWN))
drawMaze(maze)
# maze.maze[0][0] = "X"
# time.sleep(0.2)
# drawMaze(maze)
# maze.maze[0][1] = "X"
# time.sleep(0.2)
# drawMaze(maze)
