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

        # Number of moves
        self.no_of_moves = 0

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
    
    def getMazeElement(self, x: int, y: int) -> str:
        return self.maze[y][x]

    def setMazeElement(self, x: int, y: int, value: str) -> bool:
        self.maze[y][x] = value
        return True
    
    def wonTheGame(self):
        return self.shelves == self.shelfbox
    
    def move(self, nextMove) -> bool:
        success = self.performMove(nextMove)
        if success:
            self.no_of_moves += 1

        return success

    def performMove(self, nextMove: Move) -> bool:
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
        
        facingObject = self.getMazeElement(facingObject_x, facingObject_y)

        if facingObject in [MAZE_SPACE, MAZE_SHELF]:
            # Perform move only, don't push anything
            self.hero_x = facingObject_x
            self.hero_y = facingObject_y
            return True
        
        elif facingObject in [MAZE_BOX, MAZE_SHELF_BOX]:
            nextFacingObject = self.getMazeElement(nextFacingObject_x, nextFacingObject_y)
            if nextFacingObject in [MAZE_SPACE, MAZE_SHELF]:
                # Push the box to the next position
                self.hero_x = facingObject_x
                self.hero_y = facingObject_y
                self.setMazeElement(facingObject_x, facingObject_y, MAZE_SPACE if facingObject == MAZE_BOX else MAZE_SHELF)
                self.setMazeElement(nextFacingObject_x, nextFacingObject_y, MAZE_BOX if nextFacingObject == MAZE_SPACE else MAZE_SHELF_BOX)
                if facingObject == MAZE_BOX and nextFacingObject == MAZE_SHELF:
                    self.shelfbox += 1
                elif facingObject == MAZE_SHELF_BOX and nextFacingObject == MAZE_SPACE:
                    self.shelfbox -= 1
                return True
        return False

    def movable(nextMove):
        pass

class GameController:
    SYMBOLS_MAPPINGS = {MAZE_HERO: "☻", MAZE_BOX: "U", MAZE_WALL: "█", MAZE_SPACE: " ", MAZE_SHELF: "*", MAZE_SHELF_BOX: "O"}
    drawnRows = 0

    def reDraw(maze: Maze):
        
        # Move the cursor to the beginning
        # prepare for the next draw
        rows_full = GameController.drawnRows + 1
        print("\033[F"*rows_full)

        GameController.drawnRows = 0
        console_output_string = ""
        for i, row in enumerate(maze.maze):
            for j, c in enumerate(row):
                if maze.hero_x == j and maze.hero_y == i:
                    console_output_string += GameController.SYMBOLS_MAPPINGS[MAZE_HERO]
                else:
                    console_output_string += GameController.SYMBOLS_MAPPINGS[c]
            console_output_string += "\n" # new line
            GameController.drawnRows += 1
        if maze.wonTheGame():
            console_output_string += "Won the game!"
        else:
            console_output_string += "No of moves: " + str(maze.no_of_moves)
        print(console_output_string, end="")

def main():
    maze = Maze("src/map.txt")
    GameController.reDraw(maze)

    if len(sys.argv) > 1:
        if sys.argv[1] == "-a":
            # RUN AI CODE
            pass
    else:
        import msvcrt
        while True:
            if msvcrt.kbhit():
                getChr = msvcrt.getch()
                if getChr == b'K':
                    maze.move(Move.LEFT)
                elif getChr == b'M':
                    maze.move(Move.RIGHT)
                elif getChr == b'H':
                    maze.move(Move.UP)
                elif getChr == b'P':
                    maze.move(Move.DOWN)
                elif getChr == b'\x1b':
                    break
                if getChr in [b'K', b'M', b'H', b'P']:
                    GameController.reDraw(maze)

if __name__ == "__main__":
    main()