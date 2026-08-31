
_This project has been created as part of the 42 curriculum by seoliver, yoben-ch._

# A-Maze-ing

## Description

**A-Maze-ing** is a procedurally generated maze application that creates, renders, and solves mazes using multiple algorithms. This project demonstrates understanding of graph algorithms, configuration parsing, object-oriented design patterns, and terminal rendering techniques.

The application generates perfect and non-perfect mazes using two distinct algorithms (Depth-First Search and Random Walk), automatically finds the shortest path from entry to exit using breadth-first search, and renders the maze in the terminal with multiple theme options.

### Key Features
- **Configurable maze generation** with WIDTH, HEIGHT, ENTRY, and EXIT parameters
- **Multiple generation algorithms**: Depth-First Search (DFS) and Random Walk strategies
- **Perfect maze option** that guarantees a unique solution
- **Automatic path solving** using breadth-first search (BFS)
- **Terminal rendering** with multiple themes: Hedge, Pacman, Basic, Silicon
- **Interactive menu system** for real-time customization
- **Visual pattern** with the iconic 42 pattern embedded in the maze
- **Customizable color schemes** for visual enhancement

## Instructions

### Requirements
- Python 3.8 or higher
- Unix-like terminal (tested on Linux and macOS)

### Installation & Execution

Run the maze application with a configuration file (an example one is provided):
```bash
python3 a_maze_ing.py config.txt
```

The application will generate a maze and display an interactive menu where you can:
   - **Replay**: Generate a new maze with a different seed
   - **Style**: Change rendering theme or color of the 42 pattern
   - **Options**: Toggle path display, or change the generation algorithm
   - **Exit**: Close the application

### Configuration File Format

Create a configuration file (e.g., `config.txt`) with the following structure:

```
# Required parameters
WIDTH=19                    # Maze width (number of cells)
HEIGHT=11                   # Maze height (number of cells)
ENTRY=0,0                   # Entry point coordinates (x,y)
EXIT=9,3                    # Exit point coordinates (x,y)
OUTPUT_FILE=maze.txt        # Path to save maze output
PERFECT=True                # True for perfect maze (unique solution), False for braided maze

# Optional parameters
ALGORITHM=walk              # 'dfs' for Depth-First Search, 'walk' for Random Walk, 'couple' for Coupled algorithm
SEED=16                     # Seed for reproducible maze generation (positive integer)
SHOW_PATH=True              # True to display solution path, False to hide
THEME=Hedge                 # Render theme: 'Hedge', 'Pacman', 'Basic', 'Silicon'
```

**Parameter Details:**
- **WIDTH/HEIGHT**: Dimensions of the maze. Recommended: 11-55 cells for clarity
- **ENTRY/EXIT**: Coordinates must be within maze bounds (0 to WIDTH-1, 0 to HEIGHT-1)
- **OUTPUT_FILE**: Generated maze is written in hexadecimal format
- **PERFECT**: When True, generates a perfect maze (tree-like); when False, creates a braided maze (multiple paths possible)
- **SEED**: Controls randomization for reproducible results. Omit or use different values for unique mazes
- **ALGORITHM**: Different algorithms produce different visual characteristics

### Export Output

The generated maze is saved in hexadecimal format where each cell is represented as a 4-bit value:
```
Bit 0 (North): 1 = wall present, 0 = open passage
Bit 1 (East):  1 = wall present, 0 = open passage
Bit 2 (South): 1 = wall present, 0 = open passage
Bit 3 (West):  1 = wall present, 0 = open passage
```

The output file contains:
1. Hexadecimal representation of all maze cells
2. A blank line separator
3. Entry coordinates
4. Exit coordinates
5. Shortest solution path (sequence of directions: N, S, E, W)

This file can be reused to make a Pacman game.

## Architecture & Class Diagram

```
classDiagram
direction TB

class MazeConfig {
    +int width
    +int height
    +Coordinate entry
    +Coordinate exit
    +str output_file
    +bool perfect
    +str algorithm
    +OptionalSeed seed
    +bool animate
    +bool show_path
    +str theme
    +str color42
    +get_width() int
    +get_height() int
    +get_entry() tuple
    +get_exit() tuple
    +get_output_file() str
    +get_perfect() bool
    +get_algorithm() str
    +get_seed() int
    +get_animate() bool
    +get_show_path() bool
    +get_theme() str
    +get_color42() str
}

class ConfigLoader {
    +REQUIRED_KEYS: tuple
    +OPTIONAL_KEYS: tuple
    +load_config(path) MazeConfig, Optional[str]
    -_load_lines(file_path) tuple[list, Optional[str]]
    -_split_lines(lines) tuple[dict, Optional[str]]
    -_parse_positive_integer(value, key_name) tuple[int, Optional[str]]
    -_parse_point(value) tuple[tuple[int,int], Optional[str]]
    -_parse_bool(value) tuple[bool, Optional[str]]
    -_parse_algorithm(value) str
    -_validate_bounds(config) Optional[str]
}

class MazeCell {
    +int north
    +int east
    +int south
    +int west
    +bool visited
    +__str__() str
}

class MazeGenerator {
    -int width
    -int height
    -tuple entry
    -tuple exit_point
    -list grid
    -Random random
    +__init__(width, height, entry, exit, seed)
    +get_neighbors(current, allowed) list
    +open_passage(first, second) None
    +place_42_pattern(x, y) None
    +generate_dfs(current) None
    +generate_walk() None
    +generate_couple() None
    +count_walls(current) int
    +find_dead_ends() tuple[list, list]
    +find_path_bfs(start) str
    +save_output(path, solution) None
}

class MazeRenderer {
    -MazeConfig config
    -MazeGenerator generator
    +__init__(config, generator)
    +convert_maze() list[list[int]]
    +convert_path(path, map) list[list[int]]
    +print_maze(map) None
}

class ThemeRenderer {
    <<abstract>>
    -str map
    -tuple entry
    -tuple exit_point
    -str color42
    +render_wall(row, cell) str
    +render_floor(row, cell) str
    +is_cell_42(row, cell) bool
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
    -list menu_options
    +__init__(config)
    +run() int
    +print_control(maze_height) None
    +render_menu(selected, menu) None
    +get_key() str
    -handle_replay() None
    -handle_style() None
    -handle_options() None
    -handle_exit() None
}

ConfigLoader --> MazeConfig : creates
MazeApplication o-- MazeConfig : uses
MazeApplication *-- MazeGenerator : controls
MazeApplication o-- MazeRenderer : uses
MazeRenderer --> MazeGenerator : queries
MazeRenderer --> ThemeRenderer : delegates
ThemeRenderer <|-- BasicRenderer
ThemeRenderer <|-- HedgeRenderer
ThemeRenderer <|-- PacmanRenderer
ThemeRenderer <|-- SiliconRenderer
```

## Maze Generation Algorithms

### 1. Depth-First Search (DFS) - `algorithm=dfs`

**Overview:** Recursive backtracking algorithm that creates mazes with long, continuous passages.

**How it works:**
1. Start at a random cell and mark it as visited
2. From current cell, find unvisited neighbors
3. Randomly select one unvisited neighbor
4. Open passage between current and selected cell
5. Recursively repeat from the selected cell
6. If no unvisited neighbors, backtrack to previous cell

**Advantages:**
- Creates mazes with long, winding paths
- Guaranteed to be perfect (single solution)
- Efficient memory usage with stack-based recursion

**Characteristics:**
- Long, straightforward passages
- Few decision points
- Ideal for challenging puzzles

### 2. Random Walk - `algorithm=walk`

**Overview:** Iterative algorithm that carves passages by randomly walking and connecting visited/unvisited cells.

**How it works:**
1. Maintain list of visited and unvisited cells
2. Select random cell from visited list as starting point
3. Perform random walk toward an unvisited cell
4. Mark walked cells as visited and open passages
5. Repeat until all cells are visited

**Advantages:**
- Different visual characteristics from DFS
- Can create more interconnected passages
- Non-perfect mazes can have multiple solutions

**Characteristics:**
- More branching paths
- Multiple decision points
- Creates varied maze aesthetics

### 3. Coupled Random Walk - `algorithm=couple`

**Overview:** Hybrid approach combining random walk with neighbor connectivity.

**How it works:**
1. Start from origin cell
2. Maintain list of (current, neighbor) couples
3. For each couple, randomly walk to unvisited cells
4. Connect visited and unvisited cells with passages
5. Shuffle couple list for randomization

**Characteristics:**
- Balanced passage distribution
- Medium difficulty
- Unique aesthetic blend

#### Discarded Algorithms
Other possible expansions that were not added in the project are:
- **Binary Tree Algorithm**: Fast, biased toward corners
- **Sidewinder Algorithm**: Linear, directional passages
- **Prim's Algorithm**: Random spanning tree approach
- **Eller's Algorithm**: Memory-efficient for large mazes

### Why We Chose These Algorithms

- **Simplicity**: Both are easy to understand and implement
- **Efficiency**: Generate mazes quickly even for large grids
- **Determinism**: Seeded randomization ensures reproducibility
- **Perfectness**: Both can generate perfect mazes
- **Flexibility**: Support both perfect and braided modes
- **Visual Variety**: Different algorithms produce distinctly different maze patterns

## Code Reusability

### Modular Design

The project is structured with clear separation of concerns, making components easily reusable:

#### ConfigLoader (`MazeConfig.py`)
**Reusable for:**
- Any application requiring KEY=VALUE configuration file parsing
- Validation of coordinates, boolean flags, integers
- Error handling and reporting
- Type-safe configuration management

**Usage Example:**
```python
config, error = ConfigLoader.load_config("myconfig.txt")
if error:
    print(f"Config Error: {error}")
else:
    width = config.get_width()
    entry = config.get_entry()
```

#### MazeGenerator (`MazeGenerator.py`)
**Reusable for:**
- Graph-based dungeon generation
- Room/corridor generation in game design
- Procedural level creation
- Graph traversal algorithm demonstrations
- Pathfinding algorithm testing

**Key Methods:**
- `get_neighbors(cell)`: Generic neighbor lookup for grid-based systems
- `open_passage(first, second)`: Bidirectional connection between cells
- `find_path_bfs(start)`: Shortest path finding (portable BFS implementation)

#### MazeRenderer (`MazeRenderer.py`)
**Reusable for:**
- Terminal-based UI systems
- Game board rendering
- Data visualization in the terminal
- Theme/style pattern implementation

**Theme System:**
The abstract `ThemeRenderer` base class and concrete implementations (`HedgeRenderer`, `PacmanRenderer`, etc.) demonstrate the Strategy pattern for easy addition of new rendering styles.

#### MazeApplication (`MazeApplication.py`)
**Reusable for:**
- Terminal menu systems
- Interactive configuration tools
- Real-time parameter adjustment interfaces
- Event-driven application architecture

### Example: Extending with New Algorithm

Adding a new maze generation algorithm requires only extending `MazeGenerator`:

```python
def generate_sidewinder(self) -> None:
    """Sidewinder algorithm implementation"""
    for y in range(self.height):
        run = []
        for x in range(self.width):
            run.append((x, y))
            neighbors = [n for n in self.get_neighbors((x, y)) 
                        if not self.grid[n[1]][n[0]].visited]
            if not neighbors or random.random() > 0.5:
                member = random.choice(run)
                # ... carving logic ...
```

Then use it: `config.set_algorithm("sidewinder")`

## Team & Project Management

### Team Project Coordination
This project was developed as a contribution to the 42 curriculum by two students.
Why both have worked globally in all parts of this project, these are the parts in which each member has focused:
* **Sergio Oliver**: Maze application and renderer. Including mapping the user control to what is rendered in screens, and visual design of the maze output.
* **Youssef ben Chaaboun**: Maze config and generator. Including loading and validating provided values, and generating the maze by several algorithms, opening dead-ends and maze export.

### Development Timeline

**Phase 1: Planning & Design**
- Analyzed maze generation algorithms
- Designed class architecture and dependencies
- Planned configuration file format

**Phase 2: Core Implementation**
- Implemented `MazeConfig` and `ConfigLoader` for robust configuration parsing
- Developed `MazeGenerator` with DFS and Random Walk algorithms
- Built `MazeCell` and grid management system

**Phase 3: Pathfinding & Output**
- Implemented BFS for shortest path finding
- Created maze output in hexadecimal format
- Added solution path encoding

**Phase 4: Rendering & UI**
- Developed terminal rendering system
- Implemented multiple theme renderers
- Created interactive menu system
- Added real-time customization

**Phase 5: Testing & Polish**
- Tested with various maze dimensions
- Verified algorithm correctness
- Optimized rendering performance
- Added error handling

### What Worked Well
- **Modular architecture**: Clear separation between parsing, generation, rendering, and UI
- **Configuration-driven design**: Flexible without code changes
- **Theme abstraction**: Easy to add new rendering styles
- **BFS pathfinding**: Reliable and efficient path finding

### Challenges & Solutions
| Challenge | Solution |
|-----------|----------|
| Dead-end detection in perfect vs. braided mazes | Implemented `count_walls()` and `find_dead_ends()` for validation |
| Complex terminal rendering | Used abstract base class pattern for theme flexibility |
| Menu navigation in raw terminal mode | Implemented `get_key()` with proper termios handling |
| Coordinate mapping in 2D render | Created `convert_maze()` to map logical grid to terminal cells |

### Tools Used
- **Python 3**: Core language (type hints, dataclasses)
- **Git and Github**: Version control
- **Terminal/Shell**: Testing and execution
- **VS Code**: Primary IDE with Pylance integration

### Lessons Learned
1. **Algorithm visualization** is powerful for understanding graph theory
2. **Configuration files** enable flexible, reusable applications
3. **Design patterns** (Strategy, Abstract Factory) improve extensibility
4. **Terminal manipulation** with `termios` enables rich CLI experiences
5. **BFS guarantees shortest path** — important for maze solving

## Resources

### Maze Generation & Algorithms
- [Maze Generation Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-First Search Maze Generation](https://en.wikipedia.org/wiki/Recursive_backtracker)
- [Random Walk Maze Generation](https://en.wikipedia.org/wiki/Random_walk_maze)
- [Breadth-First Search Pathfinding](https://en.wikipedia.org/wiki/Breadth-first_search)

### Python Documentation
- [Python Typing Module](https://docs.python.org/3/library/typing.html)
- [Python Random Module](https://docs.python.org/3/library/random.html)
- [Terminal Control with termios](https://docs.python.org/3/library/termios.html)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)

### Design Patterns
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Abstract Factory Pattern](https://refactoring.guru/design-patterns/abstract-factory)
- [Builder Pattern](https://refactoring.guru/design-patterns/builder)

### Graph Theory & Data Structures
- [Introduction to Algorithms (CLRS)](https://en.wikipedia.org/wiki/Introduction_to_Algorithms)
- [Graph Traversal Algorithms](https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/)

### AI Usage

It was used to assist in:

1. **Documentation**: Helping structure and format this README.md file
2. **Code review and refactoring**: Suggestions for improving code structure and readability

**AI was NOT used for:**
- Application flow
- Algorithm implementation
- Logic development
- Configuration logic

## Bonus part

We have prepared some interesting features to spice up the project: 

#### 1. Playable Maze without Dead-Ends 
The application supports both perfect mazes (unique solution path) and non-perfect mazes (multiple possible paths), which can be used as a base for a Pacman game. Set `PERFECT=False` for this playable maze with no dead-ends.

#### 2. Multiple Maze Generation Algorithms
Three distinct algorithms are implemented:
- **DFS (Depth-First Search)**: `ALGORITHM=dfs`
- **Random Walk**: `ALGORITHM=walk`
- **Coupled Random Walk**: `ALGORITHM=couple`

Each produces unique maze characteristics.

#### 3. Theme System with Multiple Renderers
Four rendering themes included:
- **Hedge** 🌿: Vegetation-based theme (default) `THEME=Hedge`
- **Pacman** 👾: Retro arcade aesthetic `THEME=Pacman`
- **Basic** ⬜: classic ASCII art representation `THEME=Basic`
- **Silicon** 💻: Digital/tech theme of a motherboard `THEME=Silicon`

Interactive menu allows runtime theme switching or edit the config file.

#### 4. Interactive Menu System
Interactive and real-time input menu that allows instant maze customization:
- **Replay**: Generate with new random seed
- **Style**: Change theme or pattern 42 color
- **Options**: Toggle path display or change algorithm
- **Exit**: Clean application termination

#### 5. Automatic Pathfinding with Visualization
Breadth-first search automatically finds shortest path from entry to exit. Solution can be toggled on/off: `SHOW_PATH=True/False`

#### 6. choose Color of the 42 Pattern
The patter accepts 14 preset color options. Configurable via menu.

#### 7. Move in the maze
Users can move around the maze using the keys:
- `w` Up
- `a` Left
- `s` Down
- `d` Right

#### 8. Animate passage openings 
Optional flag to have the maze generated as an animation. 

