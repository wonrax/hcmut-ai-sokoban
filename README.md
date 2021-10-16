# AI Sokoban
A console-graphical, AI powered Sokoban game written in Python.
For ```Introduction to Artificial Intelligence```'s assignment @hcmut.

## Features
- Parse puzzle from file
- Interactive play. You can control the hero with the arrow keys. **Currently supports only Windows**.
- AI searching. Use Depth first search or A* to search for solution. Replay the solution if found.
## Run the program
Run with Python 3.9 or newer. No dependency is needed.

If the program can't draw the game correctly, try widening your terminal.

**Command:**
```
python main.py –p <path_to_map_file>
	[-h] [-i] [-s (dfs|astar)] [-t <time_in_second>]
	[-f <frame_per_second>] [--optimal]	[--visual]
	[--no-replay]
```
Where:
```
[-h]: Show this help

-p <path_to_map_file>: The path to the map file. e.g. -p maps/nabo1.txt

[-i]: Enable interactive play mode. Use arrow keys to control the hero.

[-s (dfs|astar)]: Choose search algorithm. e.g. -s astar

[--visual]: Draw state after each node visit. Will greatly decrease the performance.

[--no-replay]: Do not replay the solution after one is found.

[--optimal]: Continue the search even if a solution is found (seek optimal).

[-t <time_in_second>]: Stop the search after the given time is reached. This option has higher privilege than --optimal.

[-f <frame_per_second>]: The frame rate in which the replay will play after a solution is found.

```

### Examples
```
> python main.py -p maps/micro1.txt -s astar

Will run a* algorithm for the puzzle micro1.txt
```

```
> python main.py -p maps/micro1.txt -s astar --visual

Will draw the game state after each node visit.
```

```
> python main.py -p maps/nabo1.txt -s dfs

Will run depth first search algorithm for the puzzle nabo1.txt
```

```
> python main.py -p maps/micro2.txt -s dfs --optimal -t 10

Will run depth first search algorithm for micro2.txt, continue searching for optimal solution even if a solution is found, but do not exceed the time limit which is 10.
```

## Build your custom puzzle
- Create a text file inside ```maps``` or anywhere you like. You just need to specify the correct file path when you run the program.
- Refer to the ```SokobanMap``` class in the code for the character being used to build the map.
