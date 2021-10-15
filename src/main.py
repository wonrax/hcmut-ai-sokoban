import sys
import os
import time
import heapq


class Move:
    """
    Move class generating object that performs a move to Left/Right/Up/Down direction.
    """

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
    Take current position and return the new location after performing the move.
    """

    def move(self, current_position: tuple[int]) -> tuple[int]:
        return (
            current_position[0] + Move.DIR_MOVE_MAPPING[self.dir][0],
            current_position[1] + Move.DIR_MOVE_MAPPING[self.dir][1],
        )


LEFT = Move(Move.DIR_LEFT)
RIGHT = Move(Move.DIR_RIGHT)
UP = Move(Move.DIR_UP)
DOWN = Move(Move.DIR_DOWN)


class State:
    """
    A State object represents a certain game state.
    """

    def __init__(
        self,
        hero: tuple[int],
        boxes: set[tuple[int]],
        walls: set[tuple[int]],
        shelves: set[tuple[int]],
    ) -> None:

        """
        A tuple that stores the current position of the hero. E.g. (1, 2)
        """
        self.hero = hero

        """
        A set of tuples that stores the current position of the walls. E.g. {(1, 2), (1,5)}
        """
        self.walls = walls

        """
        A set of tuples that stores the current position of the shelves. E.g. {(1, 2), (1,5)}
        """
        self.shelves = shelves

        """
        A set of tuples that stores the current position of the boxes. E.g. {(1, 2), (1,5)}
        """
        self.boxes = boxes

        """
        Hash value of the state. Different states should have different hash values.
        """
        self.hash = hash((self.hero, frozenset(self.boxes)))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, State):
            return False
        return self.hash == o.hash

    def next_state(self, direction: Move):
        """
        Find the next state given the move direction.
        """

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
        """
        Generate the next possible states from the current state by trying to perform all the move
        directions.
        """
        next_states = []
        for direction in [LEFT, RIGHT, UP, DOWN]:
            new_state = self.next_state(direction)
            if new_state is not None:
                next_states.append(new_state)

        return next_states

    def is_goal_state(self):
        return self.boxes == self.shelves

    def check_dead_end(self, deadends) -> bool:
        """
        Check if any box in the current state is at the blocked position.
        """

        for box in self.boxes:
            if box in deadends:
                return True
        return False


class Node:
    """
    Represents a node on a tree. Contains a State object associated with this node. No 2 nodes
    have the same identical state.
    """

    def __init__(self, state: State, parent=None, h_function=None) -> None:
        self.state = state

        """
        g(n) = cost of the cheapest path from the initial node to this node.
        Also equals to the height of the current node.
        """
        self.g = 0

        """
        h(n) = cost of the cheapest path from this node to the goal node.
        """
        self.h = h_function(state) if callable(h_function) else None

        if parent and isinstance(parent, Node):
            self.g = parent.g + 1
        self.parent = parent

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Node):
            return False
        return self.state == o.state

    def __lt__(self, o: object) -> bool:

        if not isinstance(o, Node):
            raise Exception(
                "Wrong comparing type: " + str(type(self)) + " and " + str(type(o))
            )

        if self.h is None:
            raise Exception("H value is None")

        if self.g + self.h == o.g + o.h:
            return self.g > o.g

        return self.g + self.h < o.g + o.h

    def is_goal_node(self):
        return self.state.is_goal_state()

    def __hash__(self) -> int:
        return self.state.hash


DFS = 0
A_STAR = 1


class Tree:
    """
    The state space tree. Store and manage closed and open Nodes.
    Use this object to start search process.
    """

    def __init__(
        self,
        root: Node,
        deadends=set(),
        print_state=True,
        search_type=DFS,
        heuristic_function=None,
    ) -> None:

        """
        Nodes that have already been examined.
        """
        self.closed = {root}

        """
        Box positions that are blocked and there exists no way to solution.
        """
        self.deadends: set[tuple[int]] = deadends

        """
        Current node being examined in the tree. Initialized with the root node.
        """
        self.current_node = root

        """
        Nodes that have been generated, but have not examined.
        """
        self.open: list[Node] = []

        if search_type == DFS:

            """
            Use stack-like operations on the list.
            """
            self.pop = self.open.pop
            self.insert = self.open.append

        elif search_type == A_STAR:

            """
            Use priority-queue-like operations on the list.
            heapq uses the Node class' __lt__ function to compare priority.
            """
            self.pop = lambda: heapq.heappop(self.open)
            self.insert = lambda node: heapq.heappush(self.open, node)

        else:
            raise Exception("Illegal search type.")

        """
        Function that calculate h(n).
        """
        self.heuristic_function = heuristic_function

        self.print_state = print_state
        self.time_init = time.time()

        self.total_visited = 0
        self.time_limit = None
        self.best_solution: Node = None

    def search(
        self,
        # Continue finding the best solution by traversing through all nodes of the tree
        seek_optimal=False,
        # Stop searching after time limit is reached, even if seek_optimal is True
        time_limit=None,
    ):
        """
        Function that starts and keeps track of the search. Search algorithm is determined by
        self.search_type. Generate next nodes, check deadend, insert and pop the open queue to
        travel the tree. Terminate if reach the time limit. Continue searching for optimal solution
        if demanded.
        """

        while True:
            # Print state to console
            if self.print_state:
                GraphicController.reDraw(self.current_node.state)
            sys.stdout.write("Total nodes visited: " + str(self.total_visited) + " | ")
            sys.stdout.write(
                "Average speed: "
                + str(
                    round(self.total_visited / (time.time() - self.time_init + 0.01), 2)
                )
                + "\r"
            )

            # Stop search if time limit is reached
            if time_limit and time.time() - self.time_init > time_limit:
                return self.best_solution

            if self.current_node.is_goal_node():
                # Update with the best solution so far
                if not self.best_solution or self.current_node.g < self.best_solution.g:
                    self.best_solution = self.current_node

                if seek_optimal:
                    self.current_node = self.pop()
                    continue

                return self.current_node

            # If any of the box is at the blocked position, remove the current state from
            # the open queue
            if self.current_node.state.check_dead_end(self.deadends):
                if not self.open:
                    break
                self.current_node = self.open.pop()
                continue

            next_states = self.current_node.state.generate_possible_next_states()

            for state in next_states:
                new_node = Node(
                    state=state,
                    parent=self.current_node,
                    h_function=self.heuristic_function,
                )
                if new_node in self.closed:
                    continue
                self.insert(new_node)

            if not self.open:
                break

            self.closed.add(self.current_node)
            self.current_node = self.pop()
            self.total_visited += 1

        return self.best_solution


class SokobanMap:
    """
    This class handle map file parsing and converting them to the initial game state.
    """

    """
    Characters used in map building and parsing
    """
    HERO_CHAR = "X"
    SPACE_CHAR = " "
    WALL_CHAR = "#"
    BOX_CHAR = "U"
    SHELF_CHAR = "*"
    SHELF_BOX_CHAR = "O"  # the shelf which is currently filled with a box

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

        # Parse map to game state
        for i in range(len(str_maze)):
            row = str_maze[i]
            for x in range(len(row)):
                c = row[x]
                if c == SokobanMap.WALL_CHAR:
                    self.walls.add((x, i))
                elif c == SokobanMap.HERO_CHAR:
                    self.hero = (x, i)
                elif c == SokobanMap.SHELF_CHAR:
                    self.shelves.add((x, i))
                elif c == SokobanMap.BOX_CHAR:
                    self.boxes.add((x, i))
                elif c == SokobanMap.SHELF_BOX_CHAR:
                    self.boxes.add((x, i))
                    self.shelves.add((x, i))

    def build_state(self) -> State:
        return State(self.hero, self.boxes, self.walls, self.shelves)

    def get_map_bound(self) -> tuple[int]:
        # Find the maze bound
        max_wall_x = 0
        max_wall_y = 0

        for wall in self.walls:
            wall_location = wall[0]
            y = wall[1]
            max_wall_x = wall_location if wall_location > max_wall_x else max_wall_x
            max_wall_y = y if y > max_wall_y else max_wall_y

        return max_wall_x, max_wall_y

    def search_dead_ends(self):
        """
        Search box positions that are blocked and there exists no way to solution.
        """

        CHECK_MAPPINGS = {
            LEFT: (UP, DOWN),
            RIGHT: (UP, DOWN),
            UP: (LEFT, RIGHT),
            DOWN: (LEFT, RIGHT),
        }

        wall_bound_x, wall_bound_y = self.get_map_bound()
        check_spaces = set()
        for i in range(wall_bound_x + 1):
            for j in range(wall_bound_y + 1):
                if (i, j) not in self.walls:
                    check_spaces.add((i, j))

        def check_deadend(check_space):
            """
            Find and return a set of deadends. A deadend is a position where once the box gets
            in its place, it can not be moved further to achieve the goal state.
            """
            if check_space in self.shelves:
                return False

            # Corner check
            for direction in [LEFT, RIGHT, UP, DOWN]:

                new_orthogonal_location = direction.move(check_space)

                if not new_orthogonal_location in self.walls:
                    continue
                else:
                    for sub_direction in CHECK_MAPPINGS[direction]:
                        if sub_direction.move(check_space) in self.walls:
                            return True

            # Boundary check
            def check_boundary(dir: Move):
                """
                This function checks if a box is stuck beside a wall. Meaning it can only move
                along the wall, but not freely move anywhere else. Return True if it is stuck,
                otherwise False.

                E.g.:

                ###
                  #
                 U#
                  #
                ###

                In this state, the box U cannot escape.
                """

                if dir.move(check_space) in self.walls:

                    # If the position being checked is a shelve, don't mark it as a deadend
                    if check_space[0] in map(lambda x: x[0], self.shelves):
                        return False
                    if check_space[1] in map(lambda x: x[1], self.shelves):
                        return False

                    bound_1 = None
                    bound_2 = None
                    current_location = check_space

                    # Try moving along the wall to see if it's stuck, THIS direction
                    while True:
                        current_location = CHECK_MAPPINGS[dir][0].move(current_location)
                        if current_location in self.walls:
                            bound_1 = current_location[1 if dir in [LEFT, RIGHT] else 0]
                            break
                        if (
                            current_location[0] > wall_bound_x
                            or current_location[1] > wall_bound_y
                            or current_location[0] < 0
                            or current_location[1] < 0
                        ):
                            break

                    current_location = check_space
                    # Try moving along the wall to see if it's stuck, THE OTHER direction
                    while True:
                        current_location = CHECK_MAPPINGS[dir][1].move(current_location)
                        if current_location in self.walls:
                            bound_2 = current_location[1 if dir in [LEFT, RIGHT] else 0]
                            break
                        if (
                            current_location[0] > wall_bound_x
                            or current_location[1] > wall_bound_y
                            or current_location[0] < 0
                            or current_location[1] < 0
                        ):
                            break

                    side_wall = dir.move(check_space)[0 if dir in [LEFT, RIGHT] else 1]

                    if bound_1 and bound_2:
                        for i in range(bound_1 + 1, bound_2):
                            if dir in [LEFT, RIGHT]:
                                if (side_wall, i) not in self.walls:
                                    break
                            else:
                                if (i, side_wall) not in self.walls:
                                    break
                        else:
                            return True
                    else:
                        return False

            for dir in [LEFT, RIGHT, UP, DOWN]:
                if check_boundary(dir):
                    return True

            return False

        deadends = set()
        for check_space in check_spaces:
            if check_deadend(check_space):
                deadends.add(check_space)

        return deadends


class GraphicController:
    """
    Graphic control class. Used to draw the game to the console.
    """

    SYMBOLS_MAPPINGS = {
        SokobanMap.HERO_CHAR: "☻",
        SokobanMap.BOX_CHAR: "U",
        SokobanMap.WALL_CHAR: "█",
        SokobanMap.SPACE_CHAR: " ",
        SokobanMap.SHELF_CHAR: "*",
        SokobanMap.SHELF_BOX_CHAR: "O",
    }
    drawnRows = 0

    def print(string):
        """
        Custom print function that keeps track of the printed lines.
        """
        print(string)
        GraphicController.drawnRows += 1

    def reDraw(state: State):
        """
        Redraw the given game state to the console.
        """

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
                GraphicController.SYMBOLS_MAPPINGS[SokobanMap.SPACE_CHAR]
                for x in range(max_wall_x + 1)
            ]
            for y in range(max_wall_y + 1)
        ]
        for wall_location in state.walls:
            maze[wall_location[1]][
                wall_location[0]
            ] = GraphicController.SYMBOLS_MAPPINGS[SokobanMap.WALL_CHAR]
        for shelf_location in state.shelves:
            if shelf_location in state.boxes:
                maze[shelf_location[1]][
                    shelf_location[0]
                ] = GraphicController.SYMBOLS_MAPPINGS[SokobanMap.SHELF_BOX_CHAR]
            else:
                maze[shelf_location[1]][
                    shelf_location[0]
                ] = GraphicController.SYMBOLS_MAPPINGS[SokobanMap.SHELF_CHAR]
        for box_location in state.boxes:
            if not box_location in state.shelves:
                maze[box_location[1]][
                    box_location[0]
                ] = GraphicController.SYMBOLS_MAPPINGS[SokobanMap.BOX_CHAR]

        maze[state.hero[1]][state.hero[0]] = GraphicController.SYMBOLS_MAPPINGS[
            SokobanMap.HERO_CHAR
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
            GraphicController.SYMBOLS_MAPPINGS[SokobanMap.HERO_CHAR],
            "Wall:",
            GraphicController.SYMBOLS_MAPPINGS[SokobanMap.WALL_CHAR],
            "Box:",
            GraphicController.SYMBOLS_MAPPINGS[SokobanMap.BOX_CHAR],
            "Shelf:",
            GraphicController.SYMBOLS_MAPPINGS[SokobanMap.SHELF_CHAR],
            "Filled shelf:",
            GraphicController.SYMBOLS_MAPPINGS[SokobanMap.SHELF_BOX_CHAR],
        )
        GraphicController.drawnRows += 1

        sys.stdout.write("\033[2K\033[1G")
        if state.is_goal_state():
            print("You won the game!")
        else:
            print("")
        GraphicController.drawnRows += 1


def heuristic_distance_box_shelf(state: State) -> float:
    """
    A heuristic h(n) function that calculate the distance from the given state to the goal state.
    Return the sum of the minimum distance from a box to any shelve.
    """

    h = 0
    for box in state.boxes:
        min_distance = float("inf")
        for shelf in state.shelves:
            distance = abs(shelf[0] - box[0]) + abs(shelf[1] - box[1])
            if distance < min_distance:
                min_distance = distance
        h += min_distance
    return h


def heuristic_distance_combined(state: State) -> float:
    """
    A heuristic h(n) function that calculate the distance from the given state to the goal state.
    Return the sum of the minimum distance from a box to any shelve and the sum of the distance
    from the hero to the unfilled boxes.
    """

    h = 0

    for box in state.boxes:
        if box in state.shelves:
            continue
        distance = abs(state.hero[0] - box[0]) + abs(state.hero[1] - box[1])

        h += distance

    return h + heuristic_distance_box_shelf(state)


def run_interactive(initial_state: State):
    """
    Run program in interactive mode. User can use arrow keys to control the hero.
    """

    GraphicController.reDraw(initial_state)
    GraphicController.print("Interactive mode. Use arrow keys to move.")
    try:
        import msvcrt
    except Exception:
        print(
            "Can not import msvcrt module. Please note that interactive mode is only available "
            + "on Windows."
        )
        return
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
                GraphicController.print("Interactive mode. Use arrow keys to move.")
                GraphicController.print("Steps: " + str(steps))


def main():
    os.system("cls||clear")

    map: SokobanMap = None
    initial_state: State = None

    # Get map path from command argument and create SokobanMap instance
    try:
        maze_file_path = sys.argv[sys.argv.index("-p") + 1]
        map = SokobanMap(maze_file_path)
    except ValueError:
        print(
            'Please provide a path to a map with the "-p" option. For example: -p maps/micro1.txt'
        )
        return
    except OSError:
        print(
            "Map file not found. Please specify the relative path from your currently working "
            + "directory.\nFor example: python src/main.py -p src/maps/micro1.txt"
        )
        return

    if map:
        initial_state = map.build_state()
    else:
        print("Something went wrong")
        return

    # Interactive mode, control with arrow keys
    if "-i" in sys.argv:
        run_interactive(initial_state)
    # AI mode
    else:
        """Default Options"""
        # Search type
        search_type = DFS
        # h(n) function for a star search
        h_function = None
        # Print the state after each node visit
        print_game_state = False
        # Replay the solution after the search completes
        replay = True
        # Number of states that are printed per second while replaying the solution
        frame_rate = 10
        # Keep finding optimal solution
        seek_optimal = False
        # Time limit when seek_optimal in seconds
        time_limit = None

        if "--visual" in sys.argv:
            print_game_state = True
        if "--no-replay" in sys.argv:
            replay = False
        if "--optimal" in sys.argv:
            seek_optimal = True
        try:
            frame_rate = int(sys.argv[sys.argv.index("-f") + 1])
        except ValueError:
            pass
        try:
            time_limit = int(sys.argv[sys.argv.index("-t") + 1])
        except ValueError:
            pass
        try:
            st = sys.argv[sys.argv.index("-s") + 1]
            if st == "astar":
                search_type = A_STAR
                h_function = heuristic_distance_combined
            elif st != "dfs":
                raise Exception('Illegal search type. Accept only "dfs" or "astar"')
        except ValueError:
            pass

        t1 = time.time()
        GraphicController.reDraw(initial_state)

        # Init the space tree
        tree = Tree(
            root=Node(initial_state),
            deadends=map.search_dead_ends(),
            print_state=print_game_state,
            search_type=search_type,
            heuristic_function=h_function,
        )

        # Start searching for solution
        result = tree.search(seek_optimal, time_limit)

        # If solution is found
        if result:
            time_taken = time.time() - t1

            # Draw the final state (goal state) and statistics
            os.system("cls||clear")
            GraphicController.reDraw(result.state)
            GraphicController.print(
                "Time taken: "
                + str(int(time_taken / 60))
                + "m "
                + str(round(time_taken % 60, 2))
                + "s"
            )
            GraphicController.print("Solution path length: " + str(result.g + 1))
            GraphicController.print("Total node visited: " + str(tree.total_visited))

            # Replay the found solution
            if replay:
                GraphicController.print(
                    "Solution found, press enter to replay the solution..."
                )
                input()
                os.system("cls||clear")
                moves = []
                node_travel = result

                # Traverse back from the goal node to the root in order to find the moves
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
                        + str(result.g + 1)
                        + " steps"
                    )
                    time.sleep(1 / frame_rate)
        # No solution found
        else:
            GraphicController.print("Couldn't find solution")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
