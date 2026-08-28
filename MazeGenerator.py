import random
from typing import Optional

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

    def generate_couple(self) -> None:
        start=(0,0)
        self.grid[0][0].visited=True
        couple_list=[]
        for near in self.get_neighbors(start):
            couple_list.append((start,near))
        self.random.shuffle(couple_list)

        while(couple_list):
            p1,p2=couple_list[0]
            couple_list.remove((p1,p2))
            x,y=p2
    
            if not self.grid[y][x].visited:
                self.grid[y][x].visited=True
                self.open_passage(p1,p2)
                for near in self.get_neighbors(p2):
                    xn,yn=near
                    if not self.grid[yn][xn].visited:
                        couple_list.append((p2,near))
                self.random.shuffle(couple_list)

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

    def count_walls(self,current:tuple[int,int])->int:
        if current[0] < self.width and current[1]<self.height:
            x,y=current
            return [self.grid[y][x].north,self.grid[y][x].south,self.grid[y][x].west,self.grid[y][x].east].count(1)
        return -1
    
    def find_dead_ends(self)->tuple[list,list]:

        pattern_42=[]
        dead_ends=[]
        for x in range(self.width):
            for y in range(self.height):
                if self.count_walls((x,y))==3:
                    dead_ends.append((x,y))
                elif self.count_walls((x,y))==4:
                    pattern_42.append((x,y))
        return (dead_ends,pattern_42)

    def is_closed(self, p1: tuple[int,int], p2: tuple[int,int]) -> bool:
        x1,y1=p1
        x2,y2=p2
        if x1 + 1 == x2 and self.grid[y1][x1].east == 1:
            return True
        elif x1 - 1 == x2 and self.grid[y1][x1].west == 1:
            return True
        elif y1 + 1 == y2 and self.grid[y1][x1].south == 1:
            return True
        elif y1 - 1 == y2 and self.grid[y1][x1].north == 1:
            return True
        return False
    def open_dead_ends(self)->None:
        dead,pat42=self.find_dead_ends()
        for x in range(self.width):
            for y in range(self.height):
                if(x,y) in dead:
                    neighbors=self.get_neighbors((x,y))
                    allowed_neighbors=[(xn,yn) for (xn,yn) in neighbors if (xn,yn) not in pat42 and self.is_closed((x,y),(xn,yn)) ]

                    if allowed_neighbors:
                        connection=self.random.choice(allowed_neighbors)
                        self.open_passage((x,y),connection)

    def generate(self, algorithm: str,perfect:bool) -> None:
        if self.width >= 9 and self.height >= 7:
            self.place_42_pattern(self.width//2, self.height//2)
        else:
            print("Map was generated without the 42 pattern.")
        if algorithm == "walk":
            self.generate_walk()
        elif algorithm=="couple":
            self.generate_couple()
        else:
            self.generate_dfs()
        if not perfect:
            self.open_dead_ends()

    def find_path_bfs(self, current: tuple) -> str:

        list_point: list[list[tuple]] = []
        result = None

        while(True):
            if result:
                break

            if len(list_point) == 0:
                neighbors = self.get_neighbors(current)
                for next_in in neighbors:
                    if not self.is_closed(current, next_in):
                        list_point.append([current, next_in])
                        if next_in == self.exit_point:
                            result = list_point[-1]
                            break
            else:


                list_copy = []
                for elemnt in list_point:
                    last = elemnt[-1]     
                    neighbors = self.get_neighbors(last)
                    for next_in in neighbors:
                        if not self.is_closed(next_in,last) and (next_in not in elemnt):
                            coppy = elemnt.copy()
                            coppy.append(next_in)
                            list_copy.append(coppy)
                            if next_in == self.exit_point:
                                result = list_copy[-1]
                                break
                    if result:
                        break
                    list_point = list_copy
                    
                


        next_path = ""
        for i in range(len(result) - 1):
            x1, y1 = result[i]
            x2, y2 = result[i + 1]
            
            if x1 + 1 == x2:
                next_path += "E"
            elif x1 - 1 == x2:
                next_path += "W"
            elif y1 + 1 == y2:
                next_path += "S"
            elif y1 - 1 == y2:
                next_path += "N"

        return next_path

    def save_output(
        self, output_file: str
    ) -> Optional[str]:
        path = self.find_path_bfs(self.entry)
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
