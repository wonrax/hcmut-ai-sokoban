import sys
import os
import time


class Move:
    DIR_LEFT = 0
    DIR_RIGHT = 1
    DIR_UP = 2
    DIR_DOWN = 3

    DIR_MOVE_MAPPING: dict[int, tuple] = {
        DIR_LEFT: (-1, 0),
        DIR_RIGHT: (1, 0),
        DIR_UP: (0, -1),
        DIR_DOWN: (0, 1),
    }

    def __init__(self, direction: int) -> None:
        self.dir = direction

    """
    Return the new location after perform the move
    """

    def move(self, old_location: tuple[int]) -> tuple[int]:
        return (
            old_location[0] + Move.DIR_MOVE_MAPPING[self.dir][0],
            old_location[1] + Move.DIR_MOVE_MAPPING[self.dir][1],
        )


LEFT = Move(Move.DIR_LEFT)
RIGHT = Move(Move.DIR_RIGHT)
UP = Move(Move.DIR_UP)
DOWN = Move(Move.DIR_DOWN)


class State:
    def __init__(
        self,
        hero: tuple[int],
        boxes: set[tuple[int]],
        walls: set[tuple[int]],
        shelves: set[tuple[int]],
    ) -> None:
        self.hero = hero
        self.walls = walls
        self.shelves = shelves
        self.boxes = boxes
        self.hash = hash((self.hero, frozenset(self.boxes)))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, State):
            return False
        return self.hash == o.hash

    def next_state(self, direction: Move):
        hero_new_location = direction.move(self.hero)

        if hero_new_location in self.walls:
            return None

        new_boxes_location: set = self.boxes.copy()

        if hero_new_location in self.boxes:
            pushed_box_location = direction.move(hero_new_location)

            if pushed_box_location in self.walls:
                return None

            if pushed_box_location in self.boxes:
                return None

            new_boxes_location.discard(hero_new_location)
            new_boxes_location.add(pushed_box_location)

        return State(hero_new_location, new_boxes_location, self.walls, self.shelves)

    def generate_possible_next_states(self) -> list[object]:
        next_states = []
        for direction in [LEFT, RIGHT, UP, DOWN]:
            new_state = self.next_state(direction)
            if new_state is not None:
                next_states.append(new_state)

        return next_states

    def is_goal_state(self):
        return self.boxes == self.shelves

    def contain_deadend(self):
        CHECK_MAPPINGS = {
            LEFT: (UP, DOWN),
            RIGHT: (UP, DOWN),
            UP: (LEFT, RIGHT),
            DOWN: (LEFT, RIGHT),
        }
        obstacles = self.walls
        for checking_box in self.boxes:
            if checking_box in self.shelves:
                continue

            # Corner check
            for direction in [LEFT, RIGHT, UP, DOWN]:

                new_orthogonal_location = direction.move(checking_box)

                if not new_orthogonal_location in obstacles:
                    continue
                else:
                    for sub_direction in CHECK_MAPPINGS[direction]:
                        if sub_direction.move(checking_box) in obstacles:
                            return True

            # Boundary check
            def check_boundary(dir: Move):
                if dir.move(checking_box) in self.walls:

                    if checking_box[0] in map(lambda x: x[0], self.shelves):
                        return False
                    if checking_box[1] in map(lambda x: x[1], self.shelves):
                        return False

                    bound_1 = None
                    bound_2 = None
                    current_location = checking_box

                    while True:
                        current_location = CHECK_MAPPINGS[dir][0].move(current_location)
                        if current_location in self.walls:
                            bound_1 = current_location[1 if dir in [LEFT, RIGHT] else 0]
                            break

                    current_location = checking_box
                    while True:
                        current_location = CHECK_MAPPINGS[dir][1].move(current_location)
                        if current_location in self.walls:
                            bound_2 = current_location[1 if dir in [LEFT, RIGHT] else 0]
                            break

                    side_wall = dir.move(checking_box)[0 if dir in [LEFT, RIGHT] else 1]

                    for i in range(bound_1 + 1, bound_2):
                        if dir in [LEFT, RIGHT]:
                            if (side_wall, i) not in self.walls:
                                break
                        else:
                            if (i, side_wall) not in self.walls:
                                break
                    else:
                        return True

            for dir in [LEFT, RIGHT, UP, DOWN]:
                if check_boundary(dir):
                    return True

        return False


class Node:
    def __init__(self, state: State, parent=None) -> None:
        self.state = state
        self.height = 0
        if parent and isinstance(parent, Node):
            self.height = parent.height + 1
        self.parent = parent

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Node):
            return False
        return self.state == o.state

    def is_goal_node(self):
        return self.state.is_goal_state()

    def __hash__(self) -> int:
        return self.state.hash


class Tree:
    def __init__(self, root: Node, print_state=True) -> None:
        self.visited = {root}
        self.current_node = root
        self.pending_nodes: list[Node] = []
        self.pop = self.pending_nodes.pop
        self.insert = self.pending_nodes.append
        self.print_state = print_state
        self.time_init = time.time()

    def search(self):
        while True:

            if self.print_state:
                GraphicController.reDraw(self.current_node.state)
            sys.stdout.write("Total nodes visited: " + str(len(self.visited)) + " | ")
            sys.stdout.write(
                "Node visits per second: "
                + str(len(self.visited) / (time.time() - self.time_init + 0.01))
                + "\r"
            )

            if self.current_node.is_goal_node():
                return self.current_node

            if self.current_node.state.contain_deadend():
                if not self.pending_nodes:
                    break
                self.current_node = self.pending_nodes.pop()
                continue

            next_states = self.current_node.state.generate_possible_next_states()

            for state in next_states:
                new_node = Node(state, self.current_node)
                if new_node in self.visited:
                    continue
                self.insert(new_node)

            if not self.pending_nodes:
                break

            self.current_node = self.pop()
            self.visited.add(self.current_node)

        return False


class Maze:
    # Map symbol constants used in parsing maze from file
    MAZE_HERO = "X"
    MAZE_SPACE = " "
    MAZE_WALL = "#"
    MAZE_BOX = "U"
    MAZE_SHELF = "*"
    MAZE_SHELF_BOX = "O"  # the shelf with box

    def __init__(self, mapFilePath) -> None:
        # Hero location
        self.hero: tuple(int)

        # Shelves location
        self.shelves: set[tuple[int]] = set()

        # Boxes location
        self.boxes: set[tuple[int]] = set()

        # Walls location
        self.walls: set[tuple[int]] = set()

        with open(mapFilePath, "r") as txt_file:
            lines = txt_file.readlines()
            str_maze = []
            for line in lines:
                line = line.rstrip()
                if not line:
                    continue
                str_maze.append(line)

        for i in range(len(str_maze)):
            row = str_maze[i]
            for x in range(len(row)):
                c = row[x]
                if c == Maze.MAZE_WALL:
                    self.walls.add((x, i))
                elif c == Maze.MAZE_HERO:
                    self.hero = (x, i)
                elif c == Maze.MAZE_SHELF:
                    self.shelves.add((x, i))
                elif c == Maze.MAZE_BOX:
                    self.boxes.add((x, i))
                elif c == Maze.MAZE_SHELF_BOX:
                    self.boxes.add((x, i))
                    self.shelves.add((x, i))

    def build_state(self) -> State:
        return State(self.hero, self.boxes, self.walls, self.shelves)


class GraphicController:
    SYMBOLS_MAPPINGS = {
        Maze.MAZE_HERO: "☻",
        Maze.MAZE_BOX: "U",
        Maze.MAZE_WALL: "█",
        Maze.MAZE_SPACE: " ",
        Maze.MAZE_SHELF: "*",
        Maze.MAZE_SHELF_BOX: "O",
    }
    drawnRows = 0

    def print(string):
        print(string)
        GraphicController.drawnRows += 1

    def reDraw(state: State):

        if state is None:
            return

        # Move the cursor to the beginning
        # prepare for the next draw
        rows_full = GraphicController.drawnRows + 1
        print("\033[F" * rows_full)

        GraphicController.drawnRows = 0

        # Find the maze bound
        max_wall_x = 0
        max_wall_y = 0

        for wall in state.walls:
            wall_location = wall[0]
            y = wall[1]
            max_wall_x = wall_location if wall_location > max_wall_x else max_wall_x
            max_wall_y = y if y > max_wall_y else max_wall_y

        maze = [
            [
                GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_SPACE]
                for x in range(max_wall_x + 1)
            ]
            for y in range(max_wall_y + 1)
        ]
        for wall_location in state.walls:
            maze[wall_location[1]][
                wall_location[0]
            ] = GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_WALL]
        for shelf_location in state.shelves:
            if shelf_location in state.boxes:
                maze[shelf_location[1]][
                    shelf_location[0]
                ] = GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_SHELF_BOX]
            else:
                maze[shelf_location[1]][
                    shelf_location[0]
                ] = GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_SHELF]
        for box_location in state.boxes:
            if not box_location in state.shelves:
                maze[box_location[1]][
                    box_location[0]
                ] = GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_BOX]

        maze[state.hero[1]][state.hero[0]] = GraphicController.SYMBOLS_MAPPINGS[
            Maze.MAZE_HERO
        ]

        print_string = ""
        for row in maze:
            for col in row:
                print_string += col
            print_string += "\n"
            GraphicController.drawnRows += 1

        print(print_string)
        GraphicController.drawnRows += 1

        print(
            "Hero:",
            GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_HERO],
            "Wall:",
            GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_WALL],
            "Box:",
            GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_BOX],
            "Shelf:",
            GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_SHELF],
            "Filled shelf:",
            GraphicController.SYMBOLS_MAPPINGS[Maze.MAZE_SHELF_BOX],
        )
        GraphicController.drawnRows += 1

        sys.stdout.write("\033[2K\033[1G")
        if state.is_goal_state():
            print("You won the game!")
        else:
            print("")
        GraphicController.drawnRows += 1


def main():
    os.system("cls||clear")
    maze = None
    maze_file_path = "src/maps/micro1.txt"
    try:
        maze_file_path = "src/maps/" + sys.argv[sys.argv.index("-p") + 1]
        maze = Maze(maze_file_path)
    except ValueError:
        maze = Maze(maze_file_path)
    except OSError:
        print("Map file not found")
        return

    if maze:
        initial_state = maze.build_state()
    else:
        print("Something went wrong")
        return

    if "-i" in sys.argv:
        GraphicController.reDraw(initial_state)
        import msvcrt

        state = initial_state
        steps = 0
        while True:
            if msvcrt.kbhit():
                getChr = msvcrt.getch()
                new_state = None
                if getChr == b"K":
                    new_state = state.next_state(LEFT)
                elif getChr == b"M":
                    new_state = state.next_state(RIGHT)
                elif getChr == b"H":
                    new_state = state.next_state(UP)
                elif getChr == b"P":
                    new_state = state.next_state(DOWN)
                elif getChr == b"\x1b":
                    break
                if new_state is not None:
                    state = new_state
                    steps += 1
                if getChr in [b"K", b"M", b"H", b"P"]:
                    GraphicController.reDraw(state)
                    GraphicController.print("Steps: " + str(steps))

    else:
        ### Default Options ###
        # Print the state after each node visit
        print_game_state = True
        # Replay the solution after the search completes
        replay = True
        # Number of states that are printed per second when replay the solution
        frame_rate = 30

        if "--no-visual" in sys.argv:
            print_game_state = False
        if "--no-replay" in sys.argv:
            replay = False
        try:
            frame_rate = int(sys.argv[sys.argv.index("-f") + 1])
        except ValueError:
            pass

        t1 = time.time()
        tree = Tree(Node(initial_state), print_game_state)
        if not print_game_state:
            print("Searching...\n")
        GraphicController.reDraw(initial_state)
        result = tree.search()
        if result:
            time_taken = time.time() - t1
            os.system("cls||clear")
            GraphicController.reDraw(result.state)
            GraphicController.print(
                "time-taken: "
                + str(int(time_taken / 60))
                + "m "
                + str(time_taken % 60)
                + "s"
            )
            GraphicController.print("Steps to solution: " + str(result.height + 1))
            GraphicController.print("Total node visited: " + str(len(tree.visited)))
            if replay:
                GraphicController.print(
                    "Solution found, press enter to replay the solution..."
                )
                input()
                os.system("cls||clear")
                moves = []
                node_travel = result
                while True:
                    moves.append(node_travel.state)
                    node_travel = node_travel.parent
                    if not node_travel:
                        break
                moves.reverse()
                for index, move in enumerate(moves):
                    GraphicController.reDraw(move)
                    GraphicController.print(
                        "Replaying solution: "
                        + str(index + 1)
                        + "/"
                        + str(result.height + 1)
                        + " steps"
                    )
                    time.sleep(1 / frame_rate)
        else:
            GraphicController.print("Couldn't find solution")


if __name__ == "__main__":
    main()
