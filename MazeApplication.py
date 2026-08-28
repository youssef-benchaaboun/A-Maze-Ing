import sys
import random
import termios
import tty
from MazeConfig import MazeConfig
from MazeGenerator import MazeGenerator
from MazeRenderer import MazeRenderer

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
            ["Hedge", "Pacman", "Basic", "Silicon"],
            ["255;255;255", "255;0;0", "255;128;0", "255;255;0", "128;255;0",
                "0;255;0", "0;255;128", "0;255;255", "0;128;255", "0;0;255",
                "128;0;255", "255;90;255", "255;0;128", "Back"],
            ["Walk", "DS", "Couple", "Back"]
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
            if menu[0] == "255;255;255" and option != "Back":
                color = "\x1b[48;2;" + option + "m"
                if i == selected:
                    options.append(color+"•")
                else:
                    options.append(color+" ")
            elif i == selected:
                options.append(c["oc1"] + f" {option} " + c["oc"])
            else:
                options.append(c["oc"] + f" {option} ")
        print(c["oc"] + c["whF"] + "\n")
        print(f" ", end="")
        for option in options:
            print(f"{option}", end="")
        print("             ", end="")
        print("\n" + c["0"])

    def print_control(self, maze_height: int) -> None:
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
                if menu[0] == "255;255;255" and menu[menu_sel] != "Back":
                    if menu[menu_sel] == "255;255;255":
                        self.config.set_color42("")
                    else:
                        self.config.set_color42(menu[menu_sel])
                    MazeRenderer(self.config, self.generator)
                    self.render_menu(menu_sel, menu)
                else:
                    match menu[menu_sel]:
                        case "Replay":
                            lines_up = "\x1b[" + str(maze_height*2 + 5) + "A"
                            print(lines_up, end="")
                            self.config.set_seed(random.randint(0, 999))
                            self.generator = MazeGenerator(
                                self.config.get_width(), self.config.get_height(),
                                self.config.get_entry(), self.config.get_exit(), self.config.get_seed()
                            )
                            self.generator.generate(
                                self.config.get_algorithm(), self.config.get_perfect())
                            MazeRenderer(self.config, self.generator)
                            self.render_menu(menu_sel, menu)
                        case "Path":
                            self.config.set_show_path(
                                not self.config.get_show_path()
                            )
                            MazeRenderer(self.config, self.generator)
                            self.render_menu(menu_sel, menu)
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
                        case "Color42":
                            menu = self.menu_options[4]
                            menu_sel = 0
                        case "Algorithm":
                            menu = self.menu_options[5]
                            menu_sel = 0
                        case "Walk" | "DS" | "Couple":
                            self.config.set_algorithm(menu[menu_sel])
                            self.generator = MazeGenerator(
                                self.config.get_width(), self.config.get_height(),
                                self.config.get_entry(), self.config.get_exit(), self.config.get_seed()
                            )
                            self.generator.generate(
                                self.config.get_algorithm(), self.config.get_perfect())
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
        self.generator.generate(self.config.get_algorithm(),self.config.get_perfect())
        self.print_control(self.generator.height)
        error = self.generator.save_output(
            self.config.get_output_file()
        )
        if error:
            print(error, file=sys.stderr)
            return 1
        print(f"Maze saved to {self.config.get_output_file()}")
        return 0