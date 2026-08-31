import random
import sys
import termios
import tty
from MazeConfig import MazeConfig
from mazegen import MazeGenerator
from MazeRenderer import MazeRenderer


class MazeApplication:
    """Coordinate maze generation, rendering, and terminal interaction."""

    def __init__(self, config: MazeConfig) -> None:
        """Initialize the application from a validated configuration."""
        self.config = config
        self.generator = self._create_generator()
        self.menu_options = [
            ["Replay", "Style", "Options", "Exit"],
            ["Theme", "Color42", "Back"],
            ["Path", "Algorithm", "Animate", "Back"],
            ["Hedge", "Pacman", "Basic", "Silicon"],
            [
                "255;255;255", "255;0;0", "255;128;0",
                "255;255;0", "128;255;0", "0;255;0",
                "0;255;128", "0;255;255", "0;128;255",
                "0;0;255", "128;0;255", "255;90;255",
                "255;0;128", "Back",
            ],
            ["Perfect", "Walk", "DFS", "Couple", "Back"],
        ]

    def _create_generator(self) -> MazeGenerator:
        """Create a generator that reflects the current configuration."""

        return MazeGenerator(
            self.config.get_width(),
            self.config.get_height(),
            self.config.get_entry(),
            self.config.get_exit(),
            self.config.get_seed(),
            self.config.get_algorithm(),
            self.config.get_perfect(),
            self.render_maze if self.config.get_animate() else None,
        )

    @staticmethod
    def get_key() -> str:
        """Read one keypress from the terminal, including arrow sequences."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            if ch == "\x1b":
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(
                fd,
                termios.TCSADRAIN,
                old_settings,
            )

        return ch

    def render_maze(self, maze: MazeGenerator) -> None:
        MazeRenderer(self.config, maze)

    def render_menu(
        self,
        selected: int,
        menu: list[str],
    ) -> None:
        """Render a horizontal menu and highlight its selected option."""
        options: list[str] = []

        path_box = "✔" if self.config.get_show_path() else " "
        perfect_box = "✔" if self.config.get_perfect() else " "
        animate_box = "✔" if self.config.get_animate() else " "

        colors = {
            "oc": "\x1b[48;2;0;0;90m",
            "oc1": "\x1b[48;2;0;0;190m",
            "whF": "\x1b[38;2;215;215;215m",
            "0": "\x1b[0m",
        }

        for i, option in enumerate(menu):
            if option == "Path":
                option = f"{path_box}{option}"
            elif option == "Perfect":
                option = f"{perfect_box}{option}"
            elif option == "Animate":
                option = f"{animate_box}{option}"

            if menu[0] == "255;255;255" and option != "Back":
                color = "\x1b[48;2;" + option + "m"

                if i == selected:
                    options.append(color + "•")
                else:
                    options.append(color + " ")

            elif i == selected:
                options.append(
                    colors["oc1"] + f" {option} " + colors["oc"]
                )
            else:
                options.append(colors["oc"] + f" {option} ")

        print(colors["oc"] + colors["whF"] + "\n")
        print(" ", end="")

        for option in options:
            print(option, end="")

        print("             ", end="")
        print("\n" + colors["0"])

    def print_control(self) -> None:
        """Display the maze and process interactive menu controls."""
        menu_sel = 0
        menu = self.menu_options[0]

        self.render_maze(self.generator)
        self.render_menu(menu_sel, menu)

        while True:
            key = self.get_key()

            if key == "\x1b[D":
                menu_sel = (menu_sel - 1) % len(menu)

            elif key == "\x1b[C":
                menu_sel = (menu_sel + 1) % len(menu)

            elif key == "\x1b\x1b\x1b":
                return

            elif key in ["w", "a", "s", "d"]:
                entry = self.config.get_entry()
                current = self.generator.grid[entry[1]][entry[0]]

                if key == "w" and current.north == 0:
                    entry = (entry[0], entry[1] - 1)
                elif key == "a" and current.west == 0:
                    entry = (entry[0] - 1, entry[1])
                elif key == "s" and current.south == 0:
                    entry = (entry[0], entry[1] + 1)
                elif key == "d" and current.east == 0:
                    entry = (entry[0] + 1, entry[1])

                self.config.set_entry(entry)
                self.generator.entry = entry

                self.render_maze(self.generator)
                self.render_menu(menu_sel, menu)

            elif key in ("\n", "\r"):
                if (
                    menu[0] == "255;255;255"
                    and menu[menu_sel] != "Back"
                ):
                    if menu[menu_sel] == "255;255;255":
                        self.config.set_color42("")
                    else:
                        self.config.set_color42(menu[menu_sel])

                    self.render_maze(self.generator)
                    self.render_menu(menu_sel, menu)

                else:
                    option = menu[menu_sel]

                    match option:
                        case "Replay":
                            lines_up = (
                                "\x1b["
                                + str(self.config.get_height() * 2 + 5)
                                + "A"
                            )
                            print(lines_up, end="")

                            self.config.set_seed(
                                random.randint(0, 999)
                            )

                            self.generator = self._create_generator()
                            self.generator.generate()

                            self.render_maze(self.generator)
                            self.render_menu(menu_sel, menu)

                        case "Path":
                            self.config.set_show_path(
                                not self.config.get_show_path()
                            )

                            self.render_maze(self.generator)
                            self.render_menu(menu_sel, menu)

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
                            self.config.set_theme(option)
                            menu = self.menu_options[1]
                            menu_sel = 0

                            self.render_maze(self.generator)
                            self.render_menu(menu_sel, menu)

                        case "Color42":
                            menu = self.menu_options[4]
                            menu_sel = 0

                        case "Algorithm":
                            menu = self.menu_options[5]
                            menu_sel = 0

                        case "Perfect":
                            self.config.set_perfect(
                                not self.config.get_perfect()
                            )

                            self.generator = self._create_generator()
                            self.generator.generate()

                            self.render_maze(self.generator)
                            self.render_menu(menu_sel, menu)

                        case "Walk" | "DFS" | "Couple":
                            self.config.set_algorithm(option)

                            self.generator = self._create_generator()
                            self.generator.generate()

                            self.render_maze(self.generator)
                            self.render_menu(menu_sel, menu)

                        case "Animate":
                            self.config.set_animate(
                                not self.config.get_animate()
                            )
                            if self.config.get_animate():
                                menu = self.menu_options[0]
                                menu_sel = 0

                        case "Back":
                            menu = self.menu_options[0]
                            menu_sel = 0

                        case "Exit":
                            return

            else:
                continue

            print("\x1b[4A", end="")
            sys.stdout.flush()
            self.render_menu(menu_sel, menu)

    def run(self) -> int:
        """Generate, display, and save a maze, returning a status code."""
        self.generator.generate()
        self.print_control()

        error = self.generator.save_output(
            self.config.get_output_file()
        )

        if error:
            print(error, file=sys.stderr)
            return 1

        print(
            f"Maze saved to "
            f"{self.config.get_output_file()}"
        )
        return 0
