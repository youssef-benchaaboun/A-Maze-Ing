import random
import sys
from typing import Optional


class MazeConfig:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_point: tuple[int, int],
        output_file: str,
        perfect: bool,
        algorithm: str,
        seed: Optional[int],
    ) -> None:
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_point
        self._output_file = output_file
        self._perfect = perfect
        self._algorithm = algorithm
        self._seed = seed

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def get_entry(self) -> tuple[int, int]:
        return self._entry

    def get_exit(self) -> tuple[int, int]:
        return self._exit

    def get_output_file(self) -> str:
        return self._output_file

    def get_perfect(self) -> bool:
        return self._perfect

    def get_algorithm(self) -> str:
        return self._algorithm

    def get_seed(self) -> Optional[int]:
        return self._seed


class ConfigLoader:

    REQUIRED_KEYS = (
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
    )
    OPTIONAL_KEYS = ("ALGORITHM", "SEED")
    VALID_KEYS = REQUIRED_KEYS + OPTIONAL_KEYS

    @staticmethod
    def _load_lines(
        file_path: str,
    ) -> tuple[Optional[list[str]], Optional[str]]:
        try:
            with open(file_path, encoding="utf-8") as config_file:
                return config_file.read().splitlines(), None
        except OSError as error:
            return None, f"Cannot read configuration file: {error}"

    @classmethod
    def _split_lines(
        cls, lines: list[str]
    ) -> tuple[Optional[dict[str, str]], Optional[str]]:
        config: dict[str, str] = {}
        errors: list[str] = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                errors.append(f"Bad KEY=VALUE syntax: {line}")
                continue
            key, value = (part.strip() for part in line.split("=", 1))
            if key not in cls.VALID_KEYS:
                errors.append(f"{key} is not a valid configuration")
            elif key in config:
                errors.append(f"{key} is repeated")
            else:
                config[key] = value
        for key in cls.REQUIRED_KEYS:
            if key not in config:
                errors.append(f"Missing required configuration: {key}")
        return (None, "\n".join(errors)) if errors else (config, None)

    @staticmethod
    def _parse_positive_integer(
        value: str,
    ) -> tuple[Optional[int], Optional[str]]:
        try:
            result = int(value)
        except ValueError:
            return None, f"Invalid integer value: {value}"
        if result < 1:
            return None, f"{result} must be greater than 0"
        return result, None

    @staticmethod
    def _parse_point(
        value: str,
    ) -> tuple[Optional[tuple[int, int]], Optional[str]]:
        try:
            x_value, y_value = value.split(",", 1)
            point = (int(x_value.strip()), int(y_value.strip()))
        except ValueError:
            return None, f"Invalid point format: {value}"
        if point[0] < 0 or point[1] < 0:
            return None, f"Point {point} cannot contain negative coordinates"
        return point, None

    @staticmethod
    def _parse_bool(value: str) -> tuple[Optional[bool], Optional[str]]:
        normalized = value.lower()
        if normalized == "true":
            return True, None
        if normalized == "false":
            return False, None
        return None, f"Invalid boolean value: {value}"

    @classmethod
    def load_config(
        cls, file_path: str
    ) -> tuple[Optional[MazeConfig], Optional[str]]:
        lines, error = cls._load_lines(file_path)
        if error or lines is None:
            return None, error
        raw, error = cls._split_lines(lines)
        if error or raw is None:
            return None, error
        width, width_error = cls._parse_positive_integer(raw["WIDTH"])
        height, height_error = cls._parse_positive_integer(raw["HEIGHT"])
        entry, entry_error = cls._parse_point(raw["ENTRY"])
        exit_point, exit_error = cls._parse_point(raw["EXIT"])
        perfect, perfect_error = cls._parse_bool(raw["PERFECT"])
        errors = [
            item for item in (
                width_error, height_error, entry_error, exit_error,
                perfect_error,
            ) if item
        ]
        output_file = raw["OUTPUT_FILE"].strip()
        if not output_file:
            errors.append("OUTPUT_FILE: Value cannot be empty")
        algorithm = raw.get("ALGORITHM", "dfs").lower()
        if algorithm not in ("dfs", "walk"):
            errors.append("ALGORITHM must be dfs or walk")
        seed: Optional[int] = None
        if "SEED" in raw:
            try:
                seed = int(raw["SEED"])
            except ValueError:
                errors.append(f"SEED: Invalid integer value: {raw['SEED']}")

        for name, point in (("ENTRY", entry), ("EXIT", exit_point)):
            if point[0] >= width or point[1] >= height:
                errors.append(
                    f"{name} {point} is outside maze boundaries "
                    + f"({width}x{height})"
                )
        if entry == exit_point:
            errors.append(
                f"ENTRY {entry} cannot be the same as EXIT {exit_point}"
            )
        if errors:
            return None, "\n".join(errors)
        return MazeConfig(
            width, height, entry, exit_point, output_file, perfect,
            algorithm, seed,
        ), None


class MazeCell:

    def __init__(self) -> None:
        self.north = 1
        self.east = 1
        self.south = 1
        self.west = 1
        self.visited = False

    def __str__(self) -> str:
        value = (
            self.north | (self.east << 1) | (self.south << 2)
            | (self.west << 3)
        )
        return f"{value:x}"


class MazeGenerator:
    def __init__(
        self, width: int, height: int, seed: Optional[int] = None
    ) -> None:
        self.width = width
        self.height = height
        self.grid = [[MazeCell() for _ in range(width)] for _ in range(height)]
        self.random = random.Random(seed)

    def get_neighbors(self, current: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = current
        neighbors: list[tuple[int, int]] = []
        candidates = ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y))
        for cand in candidates:
            if (0 <= cand[0] < self.width and 0 <= cand[1] < self.height):
                neighbors.append(cand)
        return neighbors

    def open_passage(
        self, first: tuple[int, int], second: tuple[int, int]
    ) -> None:
        x1, y1 = first
        x2, y2 = second
        if x1 + 1 == x2:
            self.grid[y1][x1].east = 0
            self.grid[y2][x2].west = 0
        elif x1 - 1 == x2:
            self.grid[y1][x1].west = 0
            self.grid[y2][x2].east = 0
        elif y1 + 1 == y2:
            self.grid[y1][x1].south = 0
            self.grid[y2][x2].north = 0
        elif y1 - 1 == y2:
            self.grid[y1][x1].north = 0
            self.grid[y2][x2].south = 0

    def generate_dfs(self, current: tuple[int, int] = (0, 0)) -> None:
        x, y = current
        self.grid[y][x].visited = True
        neighbors = self.get_neighbors(current)
        self.random.shuffle(neighbors)
        for next_cell in neighbors:
            nx, ny = next_cell
            if not self.grid[ny][nx].visited:
                self.open_passage(current, next_cell)
                self.generate_dfs(next_cell)

    def generate_walk(self) -> None:
        start = (random.randrange(self.width), random.randrange(self.height))
        self.grid[start[1]][start[0]].visited = True
        visited = [start]
        not_visited = [
            (x, y) for x in range(self.width)
            for y in range(self.height)
            if (x, y) != start
        ]
        # TODO: place_42_pattern() as visited cells
        while not_visited:
            start = random.choice(visited)
            end = random.choice(not_visited)
            while start != end:
                neighbors = self.get_neighbors(start)
                neighbors_not = [
                    (nx, ny) for (nx, ny) in neighbors
                    if not self.grid[ny][nx].visited
                ]
                if neighbors_not:
                    next_visit = random.choice(neighbors_not)
                    nx, ny = next_visit
                    self.grid[ny][nx].visited = True
                    self.open_passage(start, next_visit)
                    visited.append(next_visit)
                    not_visited.remove(next_visit)
                    start = next_visit
                    break
                else:
                    if neighbors:
                        start = random.choice(neighbors)

    def generate(self, algorithm: str) -> None:
        if algorithm == "walk":
            self.generate_walk()
        else:
            self.generate_dfs()

    def find_path(
        self, current: tuple[int, int], exit_point: tuple[int, int],
        path: str = "", visited: Optional[set[tuple[int, int]]] = None
    ) -> Optional[str]:
        if visited is None:
            visited = set()
        if current == exit_point:
            return path
        x1, y1 = current
        visited.add(current)
        for cell in self.get_neighbors(current):
            if cell in visited:
                continue
            x2, y2 = cell
            next_path: Optional[str] = None
            if x1 + 1 == x2 and self.grid[y1][x1].east == 0:
                next_path = path + "E"
            elif x1 - 1 == x2 and self.grid[y1][x1].west == 0:
                next_path = path + "W"
            elif y1 + 1 == y2 and self.grid[y1][x1].south == 0:
                next_path = path + "S"
            elif y1 - 1 == y2 and self.grid[y1][x1].north == 0:
                next_path = path + "N"
            if next_path is not None:
                result = self.find_path(cell, exit_point, next_path, visited)
                if result is not None:
                    return result
        visited.remove(current)
        return None

    def save_output(
        self, output_file: str, entry: tuple[int, int],
        exit_point: tuple[int, int]
    ) -> Optional[str]:
        path = self.find_path(entry, exit_point)
        if path is None:
            return "Cannot save maze: no path exists between ENTRY and EXIT"
        lines = ["".join(str(cell) for cell in row) for row in self.grid]
        lines.extend(("", f"entry :{entry[0]},{entry[1]}",
                      f"exit:{exit_point[0]},{exit_point[1]}", path))
        try:
            with open(output_file, "w", encoding="utf-8") as maze_file:
                maze_file.write("\n".join(lines) + "\n")
        except OSError as error:
            return f"Cannot write output file: {error}"
        return None

    def print(
        self, theme: int
    ) -> Optional[str]:
        print("Maze print theme:", theme)
        print("Maze print grid:", self.grid[9][2])
        # Color pallete (aa=basic color, aa1=light, aa2=dark, aaF=foreground)

        class Color:
            gr = "\x1b[48;2;0;195;0m"  # basic green background
            gr2F = "\x1b[38;2;0;120;0m"  # dark green background
            yl = "\x1b[48;2;255;195;50m"  # basic yellow background
            reset = "\x1b[0m"
        c = Color()

        class Pallete:
            soil = c.yl + "  "
            soil_shaded = c.yl + c.gr2F + "▀▀"
            hedge = c.gr + "  "
        p = Pallete()
        output = ""
        for row_number, row in enumerate(self.grid):
            row_top = ""
            row_bottom = ""
            for cell_number, cell in enumerate(row):
                nw = self.grid[row_number-1][cell_number-1]
                # northwest
                if cell.north or cell.west:
                    row_top += p.hedge
                else:
                    if nw and (nw.south or nw.east):
                        row_top += p.hedge
                    else:
                        row_top += p.soil
                # north
                if cell.north:
                    row_top += p.hedge
                else:
                    row_top += p.soil
                # west
                if cell.west:
                    row_bottom += p.hedge
                else:
                    if nw and (nw.south or nw.east):
                        row_bottom += p.soil_shaded
                    else:
                        row_bottom += p.soil
                # main
                if str(cell) == "f":
                    row_bottom += p.hedge
                else:
                    if cell.north:
                        row_bottom += p.soil_shaded
                    else:
                        row_bottom += p.soil
            row_top += p.hedge
            row_bottom += p.hedge
            output += row_top + c.reset + "\n" + row_bottom + c.reset + "\n"
        output += p.hedge * (1 + 2 * len(self.grid[0])) + c.reset
        print(output)


def main(arguments: list[str]) -> int:
    if len(arguments) != 2:
        print(f"Usage: {arguments[0]} config.txt", file=sys.stderr)
        return 1
    config, error = ConfigLoader.load_config(arguments[1])
    if error or config is None:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1
    generator = MazeGenerator(
        config.get_width(), config.get_height(), config.get_seed()
    )
    generator.generate(config.get_algorithm())
    generator.print(0)
    error = generator.save_output(
        config.get_output_file(), config.get_entry(), config.get_exit()
    )
    if error:
        print(error, file=sys.stderr)
        return 1
    print(f"Maze saved to {config.get_output_file()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
