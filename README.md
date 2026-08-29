

*This project has been created as part of the 42 curriculum by seoliver, yoben-ch.*

**# A-Maze-ing**

**## Description**

**\*\*A-Maze-ing\*\*** is a procedurally generated maze application that creates, renders, and solves mazes using multiple algorithms. This project demonstrates understanding of graph algorithms, configuration parsing, object-oriented design patterns, and terminal rendering techniques.

The application generates perfect and non-perfect mazes using three generation algorithms (Depth-First Search, Random Walk, and Coupled generation), automatically finds the shortest path from entry to exit using breadth-first search, and renders the maze in the terminal with multiple theme options.

**### Key Features**

\- **\*\*Configurable maze generation\*\*** with WIDTH, HEIGHT, ENTRY, and EXIT parameters

\- **\*\*Multiple generation algorithms\*\***: Depth-First Search (DFS) and Random Walk strategies

\- **\*\*Perfect maze option\*\*** that guarantees a unique solution

\- **\*\*Automatic path solving\*\*** using breadth-first search (BFS)

\- **\*\*Terminal rendering\*\*** with multiple themes: Hedge, Pacman, Basic, Silicon

\- **\*\*Interactive menu system\*\*** for real-time customization

\- **\*\*Visual pattern\*\*** with the iconic 42 pattern embedded in the maze

\- **\*\*Customizable color schemes\*\*** for visual enhancement

**## Instructions**

**### Requirements**

\- Python 3.10 or higher

\- Unix-like terminal (tested on Linux and macOS)

**### Installation & Execution**

Run the maze application with a configuration file (an example one is provided):

\`\`\`bash

python3 a\_maze\_ing.py config.txt

\`\`\`

**### Reusable `mazegen` Package**

The maze-generation logic is also distributed as an installable Python package.
The package is independent from the terminal application, configuration parser,
and renderer, so it can be reused by another Python project.

Install the generated wheel:

\`\`\`bash
python3 -m pip install ./mazegen-1.0.0-py3-none-any.whl
\`\`\`

Then import the generator directly:

\`\`\`python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_point=(19, 14),
    seed=42,
    algorithm="dfs",
    perfect=True,
)

generator.generate()
grid = generator.get_grid()
solution = generator.get_solution()
\`\`\`

The package can be rebuilt from the repository sources with:

\`\`\`bash
python3 -m pip install build
python3 -m build
\`\`\`

The build creates a wheel (`.whl`) and a source distribution (`.tar.gz`) in
the `dist/` directory. The submitted `mazegen-*` distribution can then be
installed with `pip` in another project or in a clean virtual environment.

The application will generate a maze and display an interactive menu where you can:

   \- **\*\*Replay\*\***: Generate a new maze with a different seed

   \- **\*\*Style\*\***: Change rendering theme or color of the 42 pattern

   \- **\*\*Options\*\***: Toggle path display, or change the generation algorithm

   \- **\*\*Exit\*\***: Close the application

**### Configuration File Format**

Create a configuration file (e.g., \`config.txt\`) with the following structure:

\`\`\`

\# Required parameters

WIDTH=19                    # Maze width (number of cells)

HEIGHT=11                   # Maze height (number of cells)

ENTRY=0,0                   # Entry point coordinates (x,y)

EXIT=9,3                    # Exit point coordinates (x,y)

OUTPUT\_FILE=maze.txt        # Path to save maze output

PERFECT=True                # True for perfect maze (unique solution), False for braided maze

\# Optional parameters

ALGORITHM=walk              # 'dfs' for Depth-First Search, 'walk' for Random Walk, 'couple' for Coupled algorithm

SEED=16                     # Seed for reproducible maze generation (positive integer)

SHOW\_PATH=True              # True to display solution path, False to hide

THEME=Hedge                 # Render theme: 'Hedge', 'Pacman', 'Basic', 'Silicon'

\`\`\`

**\*\*Parameter Details:\*\***

\- **\*\*WIDTH/HEIGHT\*\***: Dimensions of the maze. Recommended: 11-55 cells for clarity

\- **\*\*ENTRY/EXIT\*\***: Coordinates must be within maze bounds (0 to WIDTH-1, 0 to HEIGHT-1)

\- **\*\*OUTPUT\_FILE\*\***: Generated maze is written in hexadecimal format

\- **\*\*PERFECT\*\***: When True, generates a perfect maze (tree-like); when False, creates a braided maze (multiple paths possible)

\- **\*\*SEED\*\***: Controls randomization for reproducible results. Omit or use different values for unique mazes

\- **\*\*ALGORITHM\*\***: Different algorithms produce different visual characteristics

**### Export Output**

The generated maze is saved in hexadecimal format where each cell is represented as a 4-bit value:

\`\`\`

Bit 0 (North): 1 = wall present, 0 = open passage

Bit 1 (East):  1 = wall present, 0 = open passage

Bit 2 (South): 1 = wall present, 0 = open passage

Bit 3 (West):  1 = wall present, 0 = open passage

\`\`\`

The output file contains:

1\. Hexadecimal representation of all maze cells

2\. A blank line separator

3\. Entry coordinates

4\. Exit coordinates

5\. Shortest solution path (sequence of directions: N, S, E, W)

This file can be reused to make a Pacman game.

**## Architecture & Class Diagram**

\`\`\`

classDiagram

direction TB

class MazeConfig {

    +int width

    +int height

    +Coordinate entry

    +Coordinate exit

    +str output\_file

    +bool perfect

    +str algorithm

    +OptionalSeed seed

    +bool animate

    +bool show\_path

    +str theme

    +str color42

    +get\_width() int

    +get\_height() int

    +get\_entry() tuple

    +get\_exit() tuple

    +get\_output\_file() str

    +get\_perfect() bool

    +get\_algorithm() str

    +get\_seed() int

    +get\_animate() bool

    +get\_show\_path() bool

    +get\_theme() str

    +get\_color42() str

}

class ConfigLoader {

    +REQUIRED\_KEYS: tuple

    +OPTIONAL\_KEYS: tuple

    +load\_config(path) MazeConfig, Optional[str]

    -\_load\_lines(file\_path) tuple[list, Optional[str]]

    -\_split\_lines(lines) tuple[dict, Optional[str]]

    -\_parse\_positive\_integer(value, key\_name) tuple[int, Optional[str]]

    -\_parse\_point(value) tuple[tuple[int,int], Optional[str]]

    -\_parse\_bool(value) tuple[bool, Optional[str]]

    -\_parse\_algorithm(value) str

    -\_validate\_bounds(config) Optional[str]

}

class MazeCell {

    +int north

    +int east

    +int south

    +int west

    +bool visited

    +\_\_str\_\_() str

}

class MazeGenerator {

    -int width

    -int height

    -tuple entry

    -tuple exit\_point

    -list grid

    -Random random

    -str algorithm

    -bool perfect

    +\_\_init\_\_(width, height, entry, exit, seed, algorithm, perfect)

    +generate() None

    +get\_grid() list

    +get\_solution() str

    +save\_output(output\_file) Optional[str]

    -\_initialize\_grid() None

    -\_get\_neighbors(current, allowed) list

    -\_open\_passage(first, second) None

    -\_place\_42\_pattern(x, y) None

    -\_generate\_dfs(current) None

    -\_generate\_walk() None

    -\_generate\_couple() None

    -\_count\_walls(current) int

    -\_find\_dead\_ends() tuple[list, list]

    -\_open\_dead\_ends() None

}

class MazeRenderer {

    -MazeConfig config

    -MazeGenerator generator

    +\_\_init\_\_(config, generator)

    +convert\_maze() list[list[int]]

    +convert\_path(path, map) list[list[int]]

    +print\_maze(map) None

}

class ThemeRenderer {

    <\<abstract>>

    -str map

    -tuple entry

    -tuple exit\_point

    -str color42

    +render\_wall(row, cell) str

    +render\_floor(row, cell) str

    +is\_cell\_42(row, cell) bool

    +print() None

}

class BasicRenderer {

    ◇ ThemeRenderer

}

class HedgeRenderer {

    ◇ ThemeRenderer

}

class PacmanRenderer {

    ◇ ThemeRenderer

}

class SiliconRenderer {

    ◇ ThemeRenderer

}

class MazeApplication {

    -MazeConfig config

    -MazeGenerator generator

    -list menu\_options

    +\_\_init\_\_(config)

    +run() int

    +print\_control(maze\_height) None

    +render\_menu(selected, menu) None

    +get\_key() str

    -handle\_replay() None

    -handle\_style() None

    -handle\_options() None

    -handle\_exit() None

}

ConfigLoader --> MazeConfig : creates

MazeApplication o-- MazeConfig : uses

MazeApplication \*-- MazeGenerator : controls

MazeApplication o-- MazeRenderer : uses

MazeRenderer --> MazeGenerator : queries

MazeRenderer --> ThemeRenderer : delegates

ThemeRenderer <|-- BasicRenderer

ThemeRenderer <|-- HedgeRenderer

ThemeRenderer <|-- PacmanRenderer

ThemeRenderer <|-- SiliconRenderer

\`\`\`

**## Maze Generation Algorithms**

**### 1. Depth-First Search (DFS) -** \`algorithm=dfs\`

**\*\*Overview:\*\*** Recursive backtracking algorithm that creates mazes with long, continuous passages.

**\*\*How it works:\*\***

1\. Start at a random cell and mark it as visited

2\. From current cell, find unvisited neighbors

3\. Randomly select one unvisited neighbor

4\. Open passage between current and selected cell

5\. Recursively repeat from the selected cell

6\. If no unvisited neighbors, backtrack to previous cell

**\*\*Advantages:\*\***

\- Creates mazes with long, winding paths

\- Guaranteed to be perfect (single solution)

\- Efficient memory usage with stack-based recursion

**\*\*Characteristics:\*\***

\- Long, straightforward passages

\- Few decision points

\- Ideal for challenging puzzles

**### 2. Random Walk -** \`algorithm=walk\`

**\*\*Overview:\*\*** Iterative algorithm that carves passages by randomly walking and connecting visited/unvisited cells.

**\*\*How it works:\*\***

1\. Maintain list of visited and unvisited cells

2\. Select random cell from visited list as starting point

3\. Perform random walk toward an unvisited cell

4\. Mark walked cells as visited and open passages

5\. Repeat until all cells are visited

**\*\*Advantages:\*\***

\- Different visual characteristics from DFS

\- Can create more interconnected passages

\- Non-perfect mazes can have multiple solutions

**\*\*Characteristics:\*\***

\- More branching paths

\- Multiple decision points

\- Creates varied maze aesthetics

**### 3. Coupled Random Walk -** \`algorithm=couple\`

**\*\*Overview:\*\*** Hybrid approach combining random walk with neighbor connectivity.

**\*\*How it works:\*\***

1\. Start from origin cell

2\. Maintain list of (current, neighbor) couples

3\. For each couple, randomly walk to unvisited cells

4\. Connect visited and unvisited cells with passages

5\. Shuffle couple list for randomization

**\*\*Characteristics:\*\***

\- Balanced passage distribution

\- Medium difficulty

\- Unique aesthetic blend

**#### Discarded Algorithms**

Other possible expansions that were not added in the project are:

\- **\*\*Binary Tree Algorithm\*\***: Fast, biased toward corners

\- **\*\*Sidewinder Algorithm\*\***: Linear, directional passages

\- **\*\*Prim's Algorithm\*\***: Random spanning tree approach

\- **\*\*Eller's Algorithm\*\***: Memory-efficient for large mazes

**### Why We Chose These Algorithms**

\- **\*\*Simplicity\*\***: Both are easy to understand and implement

\- **\*\*Efficiency\*\***: Generate mazes quickly even for large grids

\- **\*\*Determinism\*\***: Seeded randomization ensures reproducibility

\- **\*\*Perfectness\*\***: Both can generate perfect mazes

\- **\*\*Flexibility\*\***: Support both perfect and braided modes

\- **\*\*Visual Variety\*\***: Different algorithms produce distinctly different maze patterns

**## Code Reusability**

The reusable part of this project is the maze-generation library distributed
as the `mazegen` Python package.

The application-specific components remain outside the package:

- `MazeConfig` / `ConfigLoader`: reads and validates the A-Maze-ing config file
- `MazeApplication`: handles the terminal application and user interaction
- `MazeRenderer`: converts and displays the generated maze
- `mazegen`: contains the reusable maze-generation logic

This separation means another project can generate mazes without depending on
our config-file format, terminal menu, or rendering system.

**### Package Structure**

\`\`\`text
mazegen/
├── __init__.py
└── generator.py
\`\`\`

`generator.py` contains the reusable `MazeGenerator` implementation and its
internal maze-cell representation.

`__init__.py` exposes the public generator class, allowing users to write:

\`\`\`python
from mazegen import MazeGenerator
\`\`\`

instead of depending on the package's internal file layout.

**### Public API**

The package intentionally exposes a small public API:

- `MazeGenerator(...)`: configure a generator
- `generate()`: generate or regenerate the maze
- `get_grid()`: access the generated maze structure
- `get_solution()`: access a shortest entry-to-exit solution
- `save_output(...)`: serialize a generated maze to the project output format

Generation helpers such as neighbor lookup, passage opening, DFS, dead-end
handling, and `42` placement are internal implementation details and are not
part of the supported public API.

**### Constructor Parameters**

\`\`\`python
MazeGenerator(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_point: tuple[int, int],
    seed: int | None = None,
    algorithm: str = "dfs",
    perfect: bool = True,
)
\`\`\`

- `width`, `height`: maze dimensions
- `entry`, `exit_point`: maze coordinates in `(x, y)` form
- `seed`: optional seed for reproducible pseudo-random generation
- `algorithm`: generation algorithm (`dfs`, `walk`, or `couple`)
- `perfect`: selects perfect or non-perfect generation behavior

**### Basic Reuse Example**

\`\`\`python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_point=(19, 14),
    seed=42,
    algorithm="dfs",
    perfect=True,
)

generator.generate()

grid = generator.get_grid()
solution = generator.get_solution()

print(solution)
\`\`\`

A later project does not need to create a `MazeConfig` object or read a
`config.txt` file. It can provide the values directly.

**### Re-generating a Maze**

`generate()` initializes a fresh closed grid before each generation. This
prevents wall and visited-state data from a previous generation from leaking
into the next one.

\`\`\`python
generator.generate()
first_grid = generator.get_grid()

generator.generate()
second_grid = generator.get_grid()
\`\`\`

With the same deterministic seed and the same generation options, generation
can be reproduced. A different seed can be used to obtain a different maze.

**### Accessing the Generated Structure**

\`\`\`python
grid = generator.get_grid()
\`\`\`

The reusable API exposes the maze's in-memory structure. It does not require a
consumer to parse the hexadecimal output file first.

The package's internal maze representation and the A-Maze-ing output-file
representation are separate concerns.

**### Accessing a Solution**

\`\`\`python
solution = generator.get_solution()
\`\`\`

The solution is returned as cardinal directions such as:

\`\`\`text
EESSWN
\`\`\`

where each character represents `N`, `E`, `S`, or `W`.

**### Saving the Maze**

\`\`\`python
error = generator.save_output("maze.txt")

if error:
    print(error)
\`\`\`

The output contains the hexadecimal wall representation, entry coordinates,
exit coordinates, and the solution path.

**### Building the Distribution**

Package metadata and build configuration are defined in `pyproject.toml`.

Build the package with:

\`\`\`bash
python3 -m pip install build
python3 -m build
\`\`\`

This creates files similar to:

\`\`\`text
dist/
├── mazegen-1.0.0-py3-none-any.whl
└── mazegen-1.0.0.tar.gz
\`\`\`

The wheel is an installable built distribution. The `.tar.gz` file is a source
distribution.

**### Testing Reuse in a Clean Environment**

A clean virtual environment can be used to prove that the library does not
depend on files accidentally available in the development environment:

\`\`\`bash
python3 -m venv test_env
source test_env/bin/activate
python -m pip install ./dist/mazegen-1.0.0-py3-none-any.whl
\`\`\`

Then test the installed package from Python:

\`\`\`python
from mazegen import MazeGenerator
\`\`\`

Exit the environment with:

\`\`\`bash
deactivate
\`\`\`

**### Licensing**

The reusable maze generator is distributed under the MIT License. The full
license is provided in `LICENSE.md` at the repository root. This license allows
reuse, modification, and redistribution of the generator, including by later
projects.

**## Team & Project Management**

**### Team Project Coordination**

This project was developed as a contribution to the 42 curriculum by two students.

Why both have worked globally in all parts of this project, these are the parts in which each member has focused:

\* **\*\*Sergio Oliver\*\***: Maze application and renderer. Including mapping the user control to what is rendered in screens, and visual design of the maze output.

\* **\*\*Youssef ben Chaaboun\*\***: Maze config and generator. Including loading and validating provided values, and generating the maze by several algorithms, opening dead-ends and maze export.

**### Development Timeline**

**\*\*Phase 1: Planning & Design\*\***

\- Analyzed maze generation algorithms

\- Designed class architecture and dependencies

\- Planned configuration file format

**\*\*Phase 2: Core Implementation\*\***

\- Implemented \`MazeConfig\` and \`ConfigLoader\` for robust configuration parsing

\- Developed \`MazeGenerator\` with DFS and Random Walk algorithms

\- Built \`MazeCell\` and grid management system

**\*\*Phase 3: Pathfinding & Output\*\***

\- Implemented BFS for shortest path finding

\- Created maze output in hexadecimal format

\- Added solution path encoding

**\*\*Phase 4: Rendering & UI\*\***

\- Developed terminal rendering system

\- Implemented multiple theme renderers

\- Created interactive menu system

\- Added real-time customization

**\*\*Phase 5: Testing & Polish\*\***

\- Tested with various maze dimensions

\- Verified algorithm correctness

\- Optimized rendering performance

\- Added error handling

**### What Worked Well**

\- **\*\*Modular architecture\*\***: Clear separation between parsing, generation, rendering, and UI

\- **\*\*Configuration-driven design\*\***: Flexible without code changes

\- **\*\*Theme abstraction\*\***: Easy to add new rendering styles

\- **\*\*BFS pathfinding\*\***: Reliable and efficient path finding

**### Challenges & Solutions**

\| Challenge | Solution |

\|-----------|----------|

\| Dead-end detection in perfect vs. braided mazes | Implemented \`count\_walls()\` and \`find\_dead\_ends()\` for validation |

\| Complex terminal rendering | Used abstract base class pattern for theme flexibility |

\| Menu navigation in raw terminal mode | Implemented \`get\_key()\` with proper termios handling |

\| Coordinate mapping in 2D render | Created \`convert\_maze()\` to map logical grid to terminal cells |

**### Tools Used**

\- **\*\*Python 3\*\***: Core language (type hints, dataclasses)

\- **\*\*Git and Github\*\***: Version control

\- **\*\*Terminal/Shell\*\***: Testing and execution

\- **\*\*VS Code\*\***: Primary IDE with Pylance integration

**### Lessons Learned**

1\. **\*\*Algorithm visualization\*\*** is powerful for understanding graph theory

2\. **\*\*Configuration files\*\*** enable flexible, reusable applications

3\. **\*\*Design patterns\*\*** (Strategy, Abstract Factory) improve extensibility

4\. **\*\*Terminal manipulation\*\*** with \`termios\` enables rich CLI experiences

5\. **\*\*BFS guarantees shortest path\*\*** — important for maze solving

**## Resources**

**### Maze Generation & Algorithms**

\- [Maze Generation Algorithm - Wikipedia]\(https\://en.wikipedia.org/wiki/Maze\_generation\_algorithm)

\- [Depth-First Search Maze Generation]\(https\://en.wikipedia.org/wiki/Recursive\_backtracker)

\- [Random Walk Maze Generation]\(https\://en.wikipedia.org/wiki/Random\_walk\_maze)

\- [Breadth-First Search Pathfinding]\(https\://en.wikipedia.org/wiki/Breadth-first\_search)

**### Python Documentation**

\- [Python Typing Module]\(https\://docs.python.org/3/library/typing.html)

\- [Python Random Module]\(https\://docs.python.org/3/library/random.html)

\- [Terminal Control with termios]\(https\://docs.python.org/3/library/termios.html)

\- [ANSI Escape Codes]\(https\://en.wikipedia.org/wiki/ANSI\_escape\_code)

**### Design Patterns**

\- [Strategy Pattern]\(https\://refactoring.guru/design-patterns/strategy)

\- [Abstract Factory Pattern]\(https\://refactoring.guru/design-patterns/abstract-factory)

\- [Builder Pattern]\(https\://refactoring.guru/design-patterns/builder)

**### Graph Theory & Data Structures**

\- [Introduction to Algorithms (CLRS)]\(https\://en.wikipedia.org/wiki/Introduction\_to\_Algorithms)

\- [Graph Traversal Algorithms]\(https\://www\.geeksforgeeks.org/graph-data-structure-and-algorithms/)

**### AI Usage**

It was used to assist in:

1\. **\*\*Documentation\*\***: Helping structure and format this README.md file

2\. **\*\*Code review and refactoring\*\***: Suggestions for improving code structure and readability

**\*\*AI was NOT used for:\*\***

\- Application flow

\- Algorithm implementation

\- Logic development

\- Configuration logic

**## Bonus part**

We have prepared some interesting features to spice up the project: 

**#### 1. Playable Maze without Dead-Ends** 

The application supports both perfect mazes (unique solution path) and non-perfect mazes (multiple possible paths), which can be used as a base for a Pacman game. Set \`PERFECT=False\` for this playable maze with no dead-ends.

**#### 2. Multiple Maze Generation Algorithms**

Three distinct algorithms are implemented:

\- **\*\*DFS (Depth-First Search)\*\***: \`ALGORITHM=dfs\`

\- **\*\*Random Walk\*\***: \`ALGORITHM=walk\`

\- **\*\*Coupled Random Walk\*\***: \`ALGORITHM=couple\`

Each produces unique maze characteristics.

**#### 3. Theme System with Multiple Renderers**

Four rendering themes included:

\- **\*\*Hedge\*\*** 🌿: Vegetation-based theme (default) \`THEME=Hedge\`

\- **\*\*Pacman\*\*** 👾: Retro arcade aesthetic \`THEME=Pacman\`

\- **\*\*Basic\*\*** ⬜: classic ASCII art representation \`THEME=Basic\`

\- **\*\*Silicon\*\*** 💻: Digital/tech theme of a motherboard \`THEME=Silicon\`

Interactive menu allows runtime theme switching or edit the config file.

**#### 4. Interactive Menu System**

Interactive and real-time input menu that allows instant maze customization:

\- **\*\*Replay\*\***: Generate with new random seed

\- **\*\*Style\*\***: Change theme or pattern 42 color

\- **\*\*Options\*\***: Toggle path display or change algorithm

\- **\*\*Exit\*\***: Clean application termination

**#### 5. Automatic Pathfinding with Visualization**

Breadth-first search automatically finds shortest path from entry to exit. Solution can be toggled on/off: \`SHOW\_PATH=True/False\`

**#### 6. Patter 42 Color**

The patter accepts 14 preset color options. Configurable via menu.