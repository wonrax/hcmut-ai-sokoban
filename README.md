# AI Sokoban
A console-graphical, AI powered Sokoban game written in Python.
For ```Introduction to Artificial Intelligence```'s assignment @hcmut.

## Features
- Parse puzzle from file
- Interactive play. You can control the hero with the arrow keys. **Currently supports only Windows**.
- AI searching. Use Depth first search or A* to search for solution. Replay the solution if found.
## Run the program
Run with Python 3.9 and newer. No dependency is needed.

If the program can't draw the game correctly, try widen your terminal.

**Command:**
```
python main.py –p <path_to_map_file>
	[-i] [-s (dfs|astar)] [-t <time_in_second>]
	[-f <frame_per_second> [--optimal]	[--visual]
	[--no-replay]
```
Where:
```
-p <path_to_map_file>: The path to the map file. e.g. -p maps/nabo1.txt

[-i]: Enable interactive play mode. Use arrow keys to control the hero.

[-s (dfs|astar]: Choose search algorithm. e.g. -s astar

[--visual]: Draw state after each node visit. Will greatly decrease the performance.

[--no-replay]: Do not replay the solution after one is found.

[--optimal]: Continue the search even if a solution is found (seek optimal).

[-t <time_in_second>]: Stop the search after the given time is reached. This option has higher privilege than --optimal.

[-f <frame_per_second>]: The frame rate in which the replay will play after a solution is found.

```
