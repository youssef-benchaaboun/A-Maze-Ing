
from typing import Any
from abc import ABC, abstractmethod


class MazeRenderer:
    def __init__(
        self,
        config: "MazeConfig",
        generator: "MazeGenerator"
    ) -> None:
        self.config = config
        self.generator = generator
        self.print_maze(self.convert_maze())

    def convert_maze(self) -> list[list[int]]:
        map = []
        for row_number, row in enumerate(self.generator.grid):
            row_top = []
            row_bottom = []
            for cell_number, cell in enumerate(row):
                nw = self.generator.grid[row_number-1][cell_number-1]
                # northwest
                if cell.north or cell.west:
                    row_top.append(1)
                else:
                    if nw and (nw.south or nw.east):
                        row_top.append(1)
                    else:
                        row_top.append(0)
                # north
                if cell.north:
                    row_top.append(1)
                else:
                    row_top.append(0)
                # west
                if cell.west:
                    row_bottom.append(1)
                else:
                    row_bottom.append(0)
                # main
                if str(cell) == "f":
                    row_bottom.append(1)
                else:
                    row_bottom.append(0)
            row_top.append(1)
            row_bottom.append(1)
            map.append(row_top)
            map.append(row_bottom)
        map.append([1] * (self.generator.width * 2 + 1))
        return map

    def print_maze(self, map: list[list[int]]) -> None:
        data = (map, self.config.get_entry(), self.config.get_exit())
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


class ThemeRenderer(ABC):
    def __init__(self, data: Any) -> None:
        self.row_prefix = ""
        self.map = data[0]
        self.entry = data[1]
        self.exit_point = data[2]
        self.row_length = len(self.map[0])
        self.reset = "\x1b[0m"
        self.tile_entry = "\x1b[38;2;30;30;30m" + "██"
        self.tile_exit = "\x1b[48;2;215;215;215m\x1b[38;2;30;30;30m" + "▀▄"

    @abstractmethod
    def render_wall(self, row: int, cell: int) -> str:
        pass

    @abstractmethod
    def render_floor(self, row: int, cell: int) -> str:
        pass

    def render_row(self, row: int) -> str:
        output = self.row_prefix
        for cell, cell_content in enumerate(self.map[row]):
            if cell_content == 1:
                output += self.render_wall(row, cell)
            else:
                output += self.render_floor(row, cell)
        return output

    def print(self) -> None:
        print("\033[H\033[J", end="")
        for row_number, _ in enumerate(self.map):
            print(
                self.render_row(row_number) + self.reset
            )
        print(self.reset, end="")


class HedgeRenderer(ThemeRenderer):
    # Color pallete (aa=basic, aa1=light, aa2=dark, aaF=foreground)
    color_pallete = {
        "gr": "\x1b[48;2;0;195;0m",  # basic green
        "gr1F": "\x1b[38;2;0;255;0m",  # lighter green foreground
        "gr2F": "\x1b[38;2;0;120;0m",  # dark green foreground
        "yl": "\x1b[48;2;255;195;50m",  # basic yellow
    }

    def render_wall(self, row: int, cell: int) -> str:
        map = self.map
        c = self.color_pallete
        row_length = len(map[row])
        if cell >= 0 and map[row][cell-1] != 1:
            wall = c["gr"]+c["gr2F"] + "▏"
        else:
            if row-1 < 0 or map[row-1][cell] != 1:
                wall = c["gr"]+c["gr1F"] + "▔"
            else:
                wall = c["gr"] + " "
        if cell+1 < row_length and map[row][cell+1] != 1:
            wall += c["gr2F"] + "▕"
        else:
            if row-1 < 0 or map[row-1][cell] != 1:
                wall += c["gr1F"]+"▔"
            else:
                wall += " "
        return wall

    def render_floor(self, row: int, cell: int) -> str:
        c = self.color_pallete
        if self.entry == ((cell-1)/2, (row-1)/2):
            return self.tile_entry
        elif self.exit_point == ((cell-1)/2, (row-1)/2):
            return self.tile_exit
        elif self.map[row-1][cell] == 1:
            return c["yl"]+c["gr2F"] + "▀▀"
        else:
            return c["yl"] + "  "


class PacmanRenderer(ThemeRenderer):
    def __init__(self, data: Any) -> None:
        super().__init__(data)
        self.row_prefix = "\x1b[48;2;0;0;0m" + "\x1b[38;2;0;0;255m"

    def c(self, row, cell): # return value 1/0 of a map's cell
        if row < 0 or row >= len(self.map) or cell < 0 or cell >= self.row_length:
            return 0
        else:
            return self.map[row][cell]

    def render_wall(self, row: int, cell: int) -> str:
        # vertical wall
        if self.c(row-1, cell) and self.c(row+1, cell):
            if self.c(row, cell+1):
                if self.c(row, cell-1):
                    wall = "╣╠" # ╬╬
                else:
                    wall = "║╠"
            elif self.c(row, cell-1):
                wall = "╣║"
            else:
                wall = "║║"
        # horizontal wall
        elif self.c(row, cell-1) and self.c(row, cell+1):
            if self.c(row+1, cell):
                wall = "╦╦"
            elif self.c(row-1, cell):
                wall = "╩╩"
            else:
                wall = "══"
        # corners 
        elif self.c(row, cell+1) and self.c(row+1, cell):
            wall = "╔╦"
        elif self.c(row, cell-1) and self.c(row+1, cell):
            wall = "╦╗"
        elif self.c(row, cell+1) and self.c(row-1, cell):
            wall = "╚╩"
        elif self.c(row, cell-1) and self.c(row-1, cell):
            wall = "╩╝"
        # single ends
        elif self.c(row-1, cell):
            wall = "╚╝"
        elif self.c(row+1, cell):
            wall = "╔╗"
        elif self.c(row, cell+1):
            wall = " ◉"
        else:
            wall = "◆ "
        return wall

    def render_floor(self, row: int, cell: int) -> str:
        if self.entry == ((cell-1)/2, (row-1)/2):
            return "🟡"
        elif self.exit_point == ((cell-1)/2, (row-1)/2):
            return self.tile_exit + self.row_prefix
        else:
            return "  "


class SiliconRenderer(ThemeRenderer):
    def __init__(self, data: Any) -> None:
        super().__init__(data)
        self.row_prefix = "\x1b[48;2;0;120;0m" + "\x1b[38;2;255;195;50m"

    def c(self, row, cell): # return value 1/0 of a map's cell
        if row < 0 or row >= len(self.map) or cell < 0 or cell >= self.row_length:
            return 0
        else:
            return self.map[row][cell]

    def render_wall(self, row: int, cell: int) -> str:
        # vertical wall
        if self.c(row-1, cell) and self.c(row+1, cell):
            return "║║"
        # horizontal wall
        elif self.c(row, cell-1) and self.c(row, cell+1):
            if self.c(row+1, cell):
                return "╦╦"
            elif self.c(row-1, cell):
                return "╩╩"
            else:
                return "══"
        else:
            return "▒▒"

    def render_floor(self, row: int, cell: int) -> str:
        if self.entry == ((cell-1)/2, (row-1)/2):
            return "⚡"
        elif self.exit_point == ((cell-1)/2, (row-1)/2):
            return self.tile_exit + self.row_prefix
        else:
            return "  "


class BasicRenderer(ThemeRenderer):
    def render_wall(self, row: int, cell: int) -> str:
        map = self.map
        if (cell % 2 and row % 2
            and cell-1 >= 0 and map[row][cell-1]
            and row - 1 >= 0 and map[row-1][cell]
            and cell + 1 < self.row_length and map[row][cell+1]
            and row + 1 < len(map) and map[row+1][cell]
            ):
            return "\x1b[38;2;255;255;255m" + "██" + self.reset
        else:
            return "▒▒"

    def render_floor(self, row: int, cell: int) -> str:
        if self.entry == ((cell-1)/2, (row-1)/2):
            return self.tile_entry + self.reset
        elif self.exit_point == ((cell-1)/2, (row-1)/2):
            return self.tile_exit + self.reset
        else:
            return "  "
