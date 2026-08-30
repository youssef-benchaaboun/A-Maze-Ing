from abc import ABC, abstractmethod

from MazeConfig import MazeConfig
from mazegen import MazeGenerator


Coordinate = tuple[int, int]
RendererData = tuple[
    list[list[int]],
    Coordinate,
    Coordinate,
    str,
]


class MazeRenderer:
    """Convert generated cells to display tiles and select a theme."""

    def __init__(
        self,
        config: MazeConfig,
        generator: MazeGenerator,
    ) -> None:
        """Initialize the renderer and immediately print the maze."""
        self.config = config
        self.generator = generator
        self.print_maze(self.convert_maze())

    def convert_path(
        self,
        path: str,
        maze_map: list[list[int]],
    ) -> list[list[int]]:
        """Mark the solution path on a display-ready maze map."""
        current = self.config.get_entry()
        current = (current[0] * 2 + 1, current[1] * 2 + 1)

        for direction in path:
            if direction == "N":
                maze_map[current[1] - 1][current[0]] = 3
                maze_map[current[1] - 2][current[0]] = 3
                current = (current[0], current[1] - 2)

            elif direction == "S":
                maze_map[current[1] + 1][current[0]] = 3
                maze_map[current[1] + 2][current[0]] = 3
                current = (current[0], current[1] + 2)

            elif direction == "E":
                maze_map[current[1]][current[0] + 1] = 3
                maze_map[current[1]][current[0] + 2] = 3
                current = (current[0] + 2, current[1])

            elif direction == "W":
                maze_map[current[1]][current[0] - 1] = 3
                maze_map[current[1]][current[0] - 2] = 3
                current = (current[0] - 2, current[1])

        return maze_map

    def convert_maze(self) -> list[list[int]]:
        """Convert the cell grid into a wall-and-floor tile map."""
        maze_map: list[list[int]] = []
        grid = self.generator.get_grid()

        for row_number, row in enumerate(grid):
            row_top: list[int] = []
            row_bottom: list[int] = []

            for cell_number, cell in enumerate(row):
                nw = grid[row_number - 1][cell_number - 1]

                row_top.append(
                    int(
                        cell.north
                        or cell.west
                        or (nw.south or nw.east)
                    )
                )
                row_top.append(int(cell.north))
                row_bottom.append(int(cell.west))
                row_bottom.append(int(str(cell) == "f"))

            maze_map.append(row_top + [1])
            maze_map.append(row_bottom + [1])

        width = self.config.get_width()
        maze_map.append([1] * (width * 2 + 1))

        if self.config.get_show_path():
            path = self.generator.get_solution()

            if path is not None:
                maze_map = self.convert_path(path, maze_map)

        return maze_map

    def print_maze(self, maze_map: list[list[int]]) -> None:
        """Print a tile map with the configured visual theme."""
        data: RendererData = (
            maze_map,
            self.config.get_entry(),
            self.config.get_exit(),
            self.config.get_color42(),
        )

        maze: ThemeRenderer
        match self.config.get_theme():
            case "Basic":
                maze = BasicRenderer(data)
            case "Pacman":
                maze = PacmanRenderer(data)
            case "Silicon":
                maze = SiliconRenderer(data)
            case _:
                maze = HedgeRenderer(data)

        maze.print()

        if self.config.get_width() < 9 and self.config.get_height() < 7:
            print("Small maze was generated without the 42 pattern.")


class ThemeRenderer(ABC):
    """Define shared behavior for terminal maze themes."""

    def __init__(self, data: RendererData) -> None:
        """Initialize shared map, coordinate, and color data."""
        self.row_prefix: str = ""
        self.map = data[0]
        self.entry = data[1]
        self.exit_point = data[2]
        self.color42 = data[3]
        self.row_length = len(self.map[0])
        self.reset = "\x1b[0m"
        self.tile_entry = "\x1b[38;2;30;30;30m██"
        self.tile_exit = (
            "\x1b[48;2;215;215;215m"
            "\x1b[38;2;30;30;30m▀▄"
        )

    @abstractmethod
    def render_wall(self, row: int, cell: int) -> str:
        """Render one wall tile."""
        pass

    @abstractmethod
    def render_floor(self, row: int, cell: int) -> str:
        """Render one floor tile."""
        pass

    def is_cell_42(self, row: int, cell: int) -> bool:
        """Return whether a tile belongs to a fully enclosed pattern cell."""
        return bool(
            cell % 2
            and row % 2
            and cell - 1 > 0
            and self.map[row][cell - 1]
            and row - 1 > 0
            and self.map[row - 1][cell]
            and cell + 1 < self.row_length
            and self.map[row][cell + 1]
            and row + 1 < len(self.map)
            and self.map[row + 1][cell]
        )

    def render_row(self, row: int) -> str:
        """Render one complete tile-map row."""
        output = self.row_prefix

        for cell, cell_content in enumerate(self.map[row]):
            if cell_content == 1:
                output += self.render_wall(row, cell)
            else:
                output += self.render_floor(row, cell)

        return output

    def print(self) -> None:
        """Clear the terminal and print all rendered rows."""
        print("\033[H\033[J", end="")

        for row_number, _ in enumerate(self.map):
            print(self.render_row(row_number) + self.reset)

        print(self.reset, end="")


class HedgeRenderer(ThemeRenderer):
    """Render the maze with hedge walls and earth-colored paths."""

    color_pallete = {
        "gr": "\x1b[48;2;0;195;0m",
        "gr1F": "\x1b[38;2;0;255;0m",
        "gr2F": "\x1b[38;2;0;120;0m",
        "yl": "\x1b[48;2;255;195;50m",
        "yl2": "\x1b[48;2;220;125;30m",
    }

    def render_wall(self, row: int, cell: int) -> str:
        """Render one hedge wall tile."""
        maze_map = self.map
        colors = self.color_pallete
        row_length = len(maze_map[row])

        colors["42"] = (
            f"\x1b[48;2;{self.color42}m"
            if self.color42
            else colors["gr"]
        )

        if cell >= 0 and maze_map[row][cell - 1] != 1:
            wall = colors["gr"] + colors["gr2F"] + "▏"
        elif row - 1 < 0 or maze_map[row - 1][cell] != 1:
            wall = colors["gr"] + colors["gr1F"] + "▔"
        else:
            wall = colors["gr"] + " "

        if (
            cell + 1 < row_length
            and maze_map[row][cell + 1] != 1
        ):
            wall += colors["gr2F"] + "▕"
        elif row - 1 < 0 or maze_map[row - 1][cell] != 1:
            wall += colors["gr1F"] + "▔"
        else:
            wall += " "

        if self.is_cell_42(row, cell):

            if self.color42 == "255;0;0":
                wall = "🌹"
            elif self.color42 == "255;128;0":
                wall = "🏵️ "
            elif self.color42 == "255;255;0":
                wall = "🌼"
            elif self.color42 == "0;255;255":
                wall = "💠"
            elif self.color42 == "128;0;255":
                wall = "🪻 "
            elif self.color42 == "255;90;255":
                wall = "🌸"
            elif self.color42 == "255;0;128":
                wall = "🌺"
            else:
                wall = colors["42"] + "  "

        return wall

    def render_floor(self, row: int, cell: int) -> str:
        """Render one hedge-theme floor tile."""
        colors = self.color_pallete

        if self.entry == ((cell - 1) / 2, (row - 1) / 2):
            return self.tile_entry

        if self.exit_point == ((cell - 1) / 2, (row - 1) / 2):
            return self.tile_exit

        floor = colors["yl2"] if self.map[row][cell] == 3 else colors["yl"]

        if self.map[row - 1][cell] == 1:
            return floor + colors["gr2F"] + "▀▀"

        return floor + "  "


class PacmanRenderer(ThemeRenderer):
    """Render the maze with a Pac-Man-inspired terminal theme."""

    def __init__(self, data: RendererData) -> None:
        """Initialize the Pac-Man color palette."""
        super().__init__(data)
        self.row_prefix = (
            "\x1b[48;2;0;0;0m"
            "\x1b[38;2;0;0;255m"
        )

    def c(self, y: int, x: int) -> bool:
        """Return whether an in-bounds tile is a wall."""
        if (
            y < 0
            or y >= len(self.map)
            or x < 0
            or x >= self.row_length
        ):
            return False

        return self.map[y][x] == 1

    def render_wall(self, row: int, cell: int) -> str:
        """Render one connected Pac-Man wall tile."""
        if self.c(row - 1, cell) and self.c(row + 1, cell):
            if self.c(row, cell + 1):
                if self.c(row, cell - 1):
                    wall = "╣╠"
                else:
                    wall = "║╠"
            elif self.c(row, cell - 1):
                wall = "╣║"
            else:
                wall = "║║"

        elif self.c(row, cell - 1) and self.c(row, cell + 1):
            if self.c(row + 1, cell):
                wall = "╦╦"
            elif self.c(row - 1, cell):
                wall = "╩╩"
            else:
                wall = "══"

        elif self.c(row, cell + 1) and self.c(row + 1, cell):
            wall = "╔╦"

        elif self.c(row, cell - 1) and self.c(row + 1, cell):
            wall = "╦╗"

        elif self.c(row, cell + 1) and self.c(row - 1, cell):
            wall = "╚╩"

        elif self.c(row, cell - 1) and self.c(row - 1, cell):
            wall = "╩╝"

        elif self.c(row - 1, cell):
            wall = "╚╝"

        elif self.c(row + 1, cell):
            wall = "╔╗"

        elif self.c(row, cell + 1):
            wall = " ◉"

        else:
            wall = "◆ "

        if self.color42 and self.is_cell_42(row, cell):
            wall = (
                f"\x1b[38;2;{self.color42}m"
                + "╬╬"
                + self.row_prefix
            )

        return wall

    def render_floor(self, row: int, cell: int) -> str:
        """Render one Pac-Man floor tile."""
        if self.entry == ((cell - 1) / 2, (row - 1) / 2):
            return "🟡"

        if self.exit_point == ((cell - 1) / 2, (row - 1) / 2):
            return self.tile_exit + self.row_prefix

        if self.map[row][cell] == 3:
            return "▫️ "

        return "  "


class SiliconRenderer(ThemeRenderer):
    """Render the maze with a green silicon-style theme."""

    def __init__(self, data: RendererData) -> None:
        """Initialize the silicon color palette."""
        super().__init__(data)
        self.row_prefix = (
            "\x1b[48;2;0;120;0m"
            "\x1b[38;2;255;195;50m"
        )

    def c(self, y: int, x: int) -> bool:
        """Return whether an in-bounds tile is a wall."""
        if (
            y < 0
            or y >= len(self.map)
            or x < 0
            or x >= self.row_length
        ):
            return False

        return self.map[y][x] == 1

    def render_wall(self, row: int, cell: int) -> str:
        """Render one silicon wall tile."""
        if self.color42 and self.is_cell_42(row, cell):
            return (
                f"\x1b[38;2;{self.color42}m"
                + "╬╬"
                + self.row_prefix
            )

        if self.c(row - 1, cell) and self.c(row + 1, cell):
            return "║║"

        if self.c(row, cell - 1) and self.c(row, cell + 1):
            if self.c(row + 1, cell):
                return "╦╦"

            if self.c(row - 1, cell):
                return "╩╩"

            return "══"

        return "▒▒"

    def render_floor(self, row: int, cell: int) -> str:
        """Render one silicon floor tile."""
        if self.entry == ((cell - 1) / 2, (row - 1) / 2):
            return "✨"

        if self.exit_point == ((cell - 1) / 2, (row - 1) / 2):
            return self.tile_exit + self.row_prefix

        if self.map[row][cell] == 3:
            return "▪️ "

        return "  "


class BasicRenderer(ThemeRenderer):
    """Render the maze with a minimal monochrome theme."""

    color_pallete = {
        "whF": "\x1b[38;2;255;255;255m",
        "rdF": "\x1b[38;2;255;30;30m",
    }

    def render_wall(self, row: int, cell: int) -> str:
        """Render one basic wall tile."""
        if self.is_cell_42(row, cell):
            color = (
                self.color42
                if self.color42
                else "255;255;255"
            )

            return (
                "\x1b[38;2;"
                + color
                + "m██"
                + self.reset
            )

        return "▒▒"

    def render_floor(self, row: int, cell: int) -> str:
        """Render one basic floor tile."""
        if self.entry == ((cell - 1) / 2, (row - 1) / 2):
            return (
                self.color_pallete["rdF"]
                + "▓▓"
                + self.reset
            )

        if self.exit_point == ((cell - 1) / 2, (row - 1) / 2):
            return self.tile_exit + self.reset

        if self.map[row][cell] == 3:
            return "░░"

        return "  "
