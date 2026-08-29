
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
        self._color42 = ""

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

    def set_algorithm(self, value: str) -> None:
        self._algorithm = value.lower()

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

    def get_color42(self) -> Optional[str]:
        return self._color42

    def set_color42(self, value: str) -> None:
        self._color42 = value


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
        if algorithm not in ("dfs", "walk", "couple"):
            errors.append("ALGORITHM must be dfs or walk or couple")
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
