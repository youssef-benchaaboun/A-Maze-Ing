import random
import sys
from typing import Optional


class MazeCell:
    """Represent one maze cell and its four walls."""

    def __init__(self) -> None:
        """Initialize a closed, unvisited cell."""
        self.north: int = 1
        self.east: int = 1
        self.south: int = 1
        self.west: int = 1
        self.visited: bool = False

    def __str__(self) -> str:
        """Return the cell's hexadecimal wall encoding."""
        value = (
            self.north | (self.east << 1) | (self.south << 2)
            | (self.west << 3)
        )
        return f"{value:x}"


class MazeGenerator:
    """Generate, solve, inspect, and export configurable mazes."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_point: tuple[int, int],
        seed: Optional[int] = None,
        algorithm: str = "dfs",
        perfect: bool = True,
    ) -> None:
        """Initialize a reusable maze generator."""
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit_point: tuple[int, int] = exit_point
        self.algorithm: str = algorithm
        self.perfect: bool = perfect
        self.random: random.Random = random.Random(seed)
        self.grid: list[list[MazeCell]] = []
        self._initialize_grid()

    def _initialize_grid(self) -> None:
        """Reset the grid to closed, unvisited cells."""
        self.grid = [
            [MazeCell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _get_neighbors(
        self,
        current: tuple[int, int],
        allowed: Optional[list[tuple[int, int]]] = None,
    ) -> list[tuple[int, int]]:
        """Return in-bounds neighbors, optionally limited to allowed cells."""
        x, y = current
        neighbors: list[tuple[int, int]] = []
        candidates = ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y))

        for candidate in candidates:
            x_next, y_next = candidate
            if 0 <= x_next < self.width and 0 <= y_next < self.height:
                if allowed is None or candidate in allowed:
                    neighbors.append(candidate)

        return neighbors

    def _open_passage(
        self,
        first: tuple[int, int],
        second: tuple[int, int],
    ) -> None:
        """Open the shared wall between two adjacent cells."""
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

    def _place_42_pattern(self, x: int, y: int) -> None:
        """Reserve fully closed cells forming the centered 42 pattern."""
        pattern = [
            (-2, -3), (-1, -3), (0, -3), (0, -2), (0, -1), (1, -1),
            (2, -1), (-2, 1), (-2, 2), (-2, 3), (-1, 3), (0, 3),
            (0, 2), (0, 1), (2, 1), (2, 2), (2, 3), (1, 1),
        ]

        for row, column in pattern:
            if (x + column, y + row) in [self.entry, self.exit_point]:
                print(
                    "Cannot create maze: ENTRY and EXIT in 42 pattern",
                    file=sys.stderr
                )
                sys.exit(1)
            self.grid[y + row][x + column].visited = True

    def _generate_dfs(self, current: tuple[int, int] = (0, 0)) -> None:
        """Carve passages using recursive depth-first search."""
        x, y = current
        self.grid[y][x].visited = True
        neighbors = self._get_neighbors(current)
        self.random.shuffle(neighbors)

        for next_cell in neighbors:
            nx, ny = next_cell
            if not self.grid[ny][nx].visited:
                self._open_passage(current, next_cell)
                self._generate_dfs(next_cell)

    def _generate_couple(self) -> None:
        """Carve passages using randomized neighboring cell pairs."""
        start: tuple[int, int] = (0, 0)
        self.grid[0][0].visited = True
        couple_list: list[tuple[tuple[int, int], tuple[int, int]]] = []

        for neighbor in self._get_neighbors(start):
            couple_list.append((start, neighbor))

        self.random.shuffle(couple_list)

        while couple_list:
            p1, p2 = couple_list[-1]
            couple_list.remove((p1, p2))
            x, y = p2

            if not self.grid[y][x].visited:
                self.grid[y][x].visited = True
                self._open_passage(p1, p2)

                list_copy:list[tuple]=[]
                for neighbor in self._get_neighbors(p2):
                    xn, yn = neighbor
                    if not self.grid[yn][xn].visited:
                        list_copy.append((p2, neighbor))
                        self.random.shuffle(list_copy)
                couple_list.extend(list_copy)

    def _generate_walk(self) -> None:
        """Carve passages by connecting random visited and unvisited cells."""
        allowed = [
            (x, y) for x in range(self.width) for y in range(self.height)
            if not self.grid[y][x].visited
        ]
        start = self.random.choice(allowed)
        visited: list[tuple[int, int]] = [start]
        not_visited = [cell for cell in allowed if cell != start]

        while not_visited:
            start = self.random.choice(visited)
            end = self.random.choice(not_visited)

            while start != end:
                neighbors = self._get_neighbors(start, allowed)
                neighbors_not = [
                    cell for cell in neighbors if cell not in visited
                ]

                if neighbors_not:
                    next_visit = self.random.choice(neighbors_not)
                    self._open_passage(start, next_visit)
                    visited.append(next_visit)
                    not_visited.remove(next_visit)
                    start = next_visit
                else:
                    start = self.random.choice(visited)

    def _count_walls(self, current: tuple[int, int]) -> int:
        """Count closed walls for a cell, or return -1 outside the grid."""
        x, y = current

        if not (0 <= x < self.width and 0 <= y < self.height):
            return -1

        cell = self.grid[y][x]

        return [
            cell.north,
            cell.south,
            cell.west,
            cell.east,
        ].count(1)

    def _find_dead_ends(
        self,
    ) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """Return dead-end cells and fully closed pattern cells."""
        pattern_42: list[tuple[int, int]] = []
        dead_ends: list[tuple[int, int]] = []

        for x in range(self.width):
            for y in range(self.height):
                walls = self._count_walls((x, y))

                if walls == 3:
                    dead_ends.append((x, y))
                elif walls == 4:
                    pattern_42.append((x, y))

        return dead_ends, pattern_42

    def _is_closed(self, p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        """Return whether the passage from one adjacent cell is closed."""
        x1, y1 = p1
        x2, y2 = p2

        if x1 + 1 == x2:
            return self.grid[y1][x1].east == 1
        if x1 - 1 == x2:
            return self.grid[y1][x1].west == 1
        if y1 + 1 == y2:
            return self.grid[y1][x1].south == 1
        if y1 - 1 == y2:
            return self.grid[y1][x1].north == 1

        return False

    def _open_dead_ends(self) -> None:
        """Open eligible dead ends when generating a non-perfect maze."""
        dead_ends, pattern_42 = self._find_dead_ends()

        for x, y in dead_ends:
            neighbors = self._get_neighbors((x, y))
            allowed_neighbors = [
                neighbor for neighbor in neighbors
                if neighbor not in pattern_42
                and self._is_closed((x, y), neighbor)
            ]

            if allowed_neighbors:
                connection = self.random.choice(allowed_neighbors)
                self._open_passage((x, y), connection)

    def generate(self) -> None:
        """Generate a fresh maze with the configured algorithm and mode."""
        self._initialize_grid()

        if self.width >= 9 and self.height >= 7:
            self._place_42_pattern(self.width // 2, self.height // 2)

        if self.algorithm == "walk":
            self._generate_walk()
        elif self.algorithm == "couple":
            self._generate_couple()
        else:
            cell_count = self.width * self.height
            sys.setrecursionlimit(max(sys.getrecursionlimit(), cell_count + 100))
            self._generate_dfs()

        if not self.perfect:
            self._open_dead_ends()

    def get_grid(self) -> list[list[MazeCell]]:
        """Return a shallow row copy of the generated cell grid."""
        return [row.copy() for row in self.grid]

    def get_solution(self) -> Optional[str]:
        """Return a shortest entry-to-exit path as cardinal directions."""
        if self.entry == self.exit_point:
            return ""

        list_point: list[list[tuple[int, int]]] = [[self.entry]]

        while list_point:
            list_copy: list[list[tuple[int, int]]] = []

            for element in list_point:
                last = element[-1]

                for next_cell in self._get_neighbors(last):
                    if self._is_closed(last, next_cell):
                        continue

                    if next_cell in element:
                        continue

                    path = element.copy()
                    path.append(next_cell)

                    if next_cell == self.exit_point:
                        return self._path_to_string(path)

                    list_copy.append(path)

            list_point = list_copy

        return None

    @staticmethod
    def _path_to_string(path: list[tuple[int, int]]) -> str:
        """Convert a coordinate path to cardinal direction letters."""
        result = ""

        for index in range(len(path) - 1):
            x1, y1 = path[index]
            x2, y2 = path[index + 1]

            if x1 + 1 == x2:
                result += "E"
            elif x1 - 1 == x2:
                result += "W"
            elif y1 + 1 == y2:
                result += "S"
            elif y1 - 1 == y2:
                result += "N"

        return result

    def save_output(self, output_file: str = "maz.txt") -> Optional[str]:
        """Save the encoded maze and solution, returning any write error."""
        path = self.get_solution()

        if self.entry==self.exit_point:
            return "Cannot save maze: same ENTRY and EXIT"
        
        if path is None:
            return "Cannot save maze: no path exists between ENTRY and EXIT"

        lines = ["".join(str(cell) for cell in row) for row in self.grid]
        lines.extend(
            (
                "",
                f"{self.entry[0]},{self.entry[1]} #entry",
                f"{self.exit_point[0]},{self.exit_point[1]} #exit",
                path,
            )
        )

        try:
            with open(output_file, "w", encoding="utf-8") as maze_file:
                maze_file.write("\n".join(lines) + "\n")
        except OSError as error:
            return f"Cannot write output file: {error}"

        return None
