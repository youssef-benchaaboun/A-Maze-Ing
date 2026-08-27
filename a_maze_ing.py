import random
import sys
from typing import Optional
from MazeRenderer import MazeRenderer
import termios
import tty


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
        animate: Optional[bool],
        show_path: Optional[bool],
        theme: Optional[str],
    ) -> None:
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_point
        self._output_file = output_file
        self._perfect = perfect
        self._algorithm = algorithm
        self._seed = seed
        self._animate = animate
        self._show_path = show_path
        self._theme = theme

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

    def set_seed(self, value: int) -> None:
        self._seed = value

    def get_animate(self) -> Optional[bool]:
        return self._animate

    def set_animate(self, value: bool) -> None:
        self._animate = value

    def get_show_path(self) -> Optional[bool]:
        return self._show_path

    def set_show_path(self, value: bool) -> None:
        self._show_path = value

    def get_theme(self) -> Optional[str]:
        return self._theme

    def set_theme(self, value: str) -> None:
        self._theme = value


class ConfigLoader:

    REQUIRED_KEYS = (
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
    )
    OPTIONAL_KEYS = ("ALGORITHM", "SEED", "ANIMATE", "SHOW_PATH", "THEME")
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
    
    @staticmethod
    def _parse_theme(value: str) -> tuple[Optional[str], Optional[str]]:
        normalized = value.capitalize()
        if normalized in ["Hedge", "Pacman", "Basic", "Silicon"]:
            return normalized, None
        return None, f"Invalid theme value: {value}"

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
                perfect_error
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
        animate: Optional[bool] = None
        if "ANIMATE" in raw:
            try:
                animate, animate_error = cls._parse_bool(raw["ANIMATE"])
            except ValueError:
                errors.append(f"ANIMATE: Invalid value: {raw['ANIMATE']}")
        show_path: Optional[bool] = None
        if "SHOW_PATH" in raw:
            try:
                show_path, show_path_error = cls._parse_bool(raw["SHOW_PATH"])
            except ValueError:
                errors.append(f"SHOW_PATH: Invalid value: {raw['SHOW_PATH']}")
        theme: Optional[str] = None
        if "THEME" in raw:
            try:
                theme = str(raw["THEME"]).capitalize()
            except ValueError:
                errors.append(f"THEME: Invalid value: {raw['THEME']}")

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
            algorithm, seed, animate, show_path, theme
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
        self, width: int, height: int, entry: tuple[int, int],
        exit_point: tuple[int, int], seed: Optional[int] = None
    ) -> None:
        self.width = width
        self.height = height
        self.grid = [[MazeCell() for _ in range(width)] for _ in range(height)]
        self.random = random.Random(seed)
        self.entry = entry
        self.exit_point = exit_point

    def get_neighbors(self, current: tuple[int, int],allowed:list[tuple]=None) -> list[tuple[int, int]]:
        x, y = current
        neighbors: list[tuple[int, int]] = []
        candidates = ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y))
        for cand in candidates:
            if (0 <= cand[0] < self.width and 0 <= cand[1] < self.height):
                if(allowed is None or cand in allowed):
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

    def place_42_pattern(self, x: int, y: int) -> None:
        for cell in [
            (-2, -3), (-1, -3), (0, -3), (0, -2), (0, -1), (1, -1), (2, -1),
            (-2, 1), (-2, 2), (-2, 3), (-1, 3), (0, 3), (0, 2), (0, 1),
            (2, 1), (2, 2), (2, 3), (1, 1)
        ]:
            self.grid[y + cell[0]][x + cell[1]].visited = True

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
        allowed = [
            (x, y) for x in range(self.width)
            for y in range(self.height)
            if not self.grid[y][x].visited
        ]
        start=random.choice(allowed)
        visited = [start]
        not_visited = [
            bloc for bloc in allowed
            if bloc != start
        ]
        while not_visited:
            start = self.random.choice(visited)
            end = self.random.choice(not_visited)
            while start != end:
                neighbors = self.get_neighbors(start,allowed)
                neighbors_not = [
                    (nx, ny) for (nx, ny) in neighbors
                    if (nx,ny) not in visited
                ]
                if neighbors_not:
                    next_visit = self.random.choice(neighbors_not)
                    nx, ny = next_visit
                    self.open_passage(start, next_visit)
                    visited.append(next_visit)
                    not_visited.remove(next_visit)
                    start = next_visit
                else:
                    start = self.random.choice(visited)

    def generate(self, algorithm: str) -> None:
        if self.width >= 9 and self.height >= 7:
            self.place_42_pattern(self.width//2, self.height//2)
        else:
            print("Map was generated without the 42 pattern.")
        if algorithm == "walk":
            self.generate_walk()
        else:
            self.generate_dfs()

    def find_path(
        self, current: tuple[int, int],
        path: str = "", visited: Optional[set[tuple[int, int]]] = None
    ) -> Optional[str]:
        if visited is None:
            visited = set()
        if current == self.exit_point:
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
                result = self.find_path(cell, next_path, visited)
                if result is not None:
                    return result
        visited.remove(current)
        return None

    def save_output(
        self, output_file: str
    ) -> Optional[str]:
        path = self.find_path(self.entry)
        if path is None:
            return "Cannot save maze: no path exists between ENTRY and EXIT"
        lines = ["".join(str(cell) for cell in row) for row in self.grid]
        lines.extend(("", f"entry :{self.entry[0]},{self.entry[1]}",
                      f"exit:{self.exit_point[0]},{self.exit_point[1]}", path))
        try:
            with open(output_file, "w", encoding="utf-8") as maze_file:
                maze_file.write("\n".join(lines) + "\n")
        except OSError as error:
            return f"Cannot write output file: {error}"
        return None

    def print(
        self, theme: int
    ) -> Optional[str]:
        if theme == 0:
            # Color pallete (aa=basic, aa1=light, aa2=dark, aaF=foreground)
            c = {
                "gr": "\x1b[48;2;0;195;0m",  # basic green
                "gr2F": "\x1b[38;2;0;120;0m",  # dark green foreground
                "yl": "\x1b[48;2;255;195;50m",  # basic yellow
                "rd": "\x1b[48;2;180;0;0m",  # red
                "pr": "\x1b[48;2;180;0;255m",  # purple
                "be": "\x1b[48;2;0;0;255m",  # blue
                "wh": "\x1b[48;2;215;215;215m",  # white
                "blF": "\x1b[38;2;30;30;30m",  # black fg
                "0": "\x1b[0m"  # reset
            }

            class Pallete:
                soil = c["yl"] + "  "
                soil_shaded = c["yl"] + c["gr2F"] + "▀▀"
                hedge = c["gr"] + "  "
                entry_point = c["blF"] + "██"
                exit_point = c["wh"] + c["blF"] + "▀▄"
                closed_cell=c["be"] + "  "
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
                        if cell.north or (nw and (nw.south or nw.east)):
                            row_bottom += p.soil_shaded
                        else:
                            row_bottom += p.soil
                    # main
                    if str(cell) == "f":
                        row_bottom += p.closed_cell
                    else:
                        if (cell_number, row_number) == self.entry:
                            row_bottom += p.entry_point
                        elif (cell_number, row_number) == self.exit_point:
                            row_bottom += p.exit_point
                        elif cell.north:
                            row_bottom += p.soil_shaded
                        else:
                            row_bottom += p.soil
                row_top += p.hedge
                row_bottom += p.hedge
                output += row_top + c["0"] + "\n" + row_bottom + c["0"] + "\n"
            output += p.hedge * (1 + 2 * len(self.grid[0])) + c["0"]
            return output
        else:
            return f"Cannot find theme number: {theme}"

class MazeApplication:
    def __init__(self, config: MazeConfig) -> None:
        self.config = config
        self.generator = MazeGenerator(
            config.get_width(), config.get_height(),
            config.get_entry(), config.get_exit(), config.get_seed()
        )
        self.menu_options = [
            ["Replay", "Style", "Options", "Exit"],
            ["Theme", "Color42", "Back"],
            ["Path", "Animate", "Algorithm", "Back"],
            ["Hedge", "Pacman", "Basic", "Silicon"]
        ]

    @staticmethod
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd) # more powerful than cbreak, but disables Ctrl+C
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def render_menu(self, selected: int, menu: list[str]) -> None:
        options = []
        show_path_checkbox = "✔" if self.config.get_show_path() else " "
        show_animate_checkbox = "✔" if self.config.get_animate() else " "

        c = {
            "oc": "\x1b[48;2;0;0;90m",  # ocean blue
            "oc1": "\x1b[48;2;0;0;190m",  # lighter
            "whF": "\x1b[38;2;215;215;215m",  # white 
            "0": "\x1b[0m",  # reset
        }
        for i, option in enumerate(menu):
            if option == "Path":
                option = f"{show_path_checkbox}{option}"
            elif option == "Animate":
                option = f"{show_animate_checkbox}{option}"
            if i == selected:
                options.append(c["oc1"] + f" {option} " + c["oc"])
            else:
                options.append(f" {option} ")
        print(c["oc"] + c["whF"] + "\n")
        for option in options:
            print(f" {option}", end="")
        print("             ", end="")
        print("\n" + c["0"])

    def print_control(self, maze_output: str, maze_height: int) -> None:
        menu_sel = 0
        menu = self.menu_options[0]
        MazeRenderer(self.config, self.generator)
        self.render_menu(menu_sel, menu)

        while True:
            key = self.get_key()
            if key == "\x1b[D":
                menu_sel = (menu_sel - 1) % len(menu)
            elif key == "\x1b[C":
                menu_sel = (menu_sel + 1) % len(menu)
            elif key in ("\n", "\r"):
                match menu[menu_sel]:
                    case "Replay":
                        lines_up = "\x1b[" + str(maze_height*2 + 5) + "A"
                        print(lines_up, end="")
                        self.config.set_seed(random.randint(0, 999))
                        self.generator.generate(self.config.get_algorithm())
                        MazeRenderer(self.config, self.generator)
                        self.render_menu(menu_sel, menu)
                    case "Path":
                        self.config.set_show_path(
                            not self.config.get_show_path()
                        )
                    case "Animate":
                        self.config.set_animate(not self.config.get_animate())
                    case "Style":
                        menu = self.menu_options[1]
                        menu_sel = 0
                    case "Options":
                        menu = self.menu_options[2]
                        menu_sel = 0
                    case "Theme":
                        menu = self.menu_options[3]
                        menu_sel = 0
                    case "Hedge" | "Pacman" | "Basic" | "Silicon":
                        self.config.set_theme(menu[menu_sel])
                        menu = self.menu_options[1]
                        menu_sel = 0
                        MazeRenderer(self.config, self.generator)
                        self.render_menu(menu_sel, menu)
                    case "Back":
                        menu = self.menu_options[0]
                        menu_sel = 0
                        pass
                    case "Exit":
                        return
            else:
                continue

            print("\x1b[4A", end="")  # 4 lines up (A)
            sys.stdout.flush()
            self.render_menu(menu_sel, menu)

    def run(self) -> int:
        self.generator.generate(self.config.get_algorithm())
        output = self.generator.print(0)
        if output is None:
            print("Render maze error.", file=sys.stderr)
            return 1
        self.print_control(output, self.generator.height)
        error = self.generator.save_output(
            self.config.get_output_file()
        )
        if error:
            print(error, file=sys.stderr)
            return 1
        print(f"Maze saved to {self.config.get_output_file()}")
        return 0


def main(arguments: list[str]) -> int:
    if len(arguments) != 2:
        print(f"Usage: {arguments[0]} config.txt", file=sys.stderr)
        return 1

    config, error = ConfigLoader.load_config(arguments[1])
    if error or config is None:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    application = MazeApplication(config)
    return application.run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
