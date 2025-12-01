"""Room generator."""

# -- Imports --

import random


class RoomGenerator:
    """Room generator.

    ## Description
    Generates Dungeon styled map by method of cellular automaton.
    ## Attributes
    ```
    self.coordinates = coordinates # Room coordinates for seed hash
    self.empty_char: str # Empty char
    self.wall_char: str # Wall char
    self.door_char: str # Door char
    self.grid_size: int # Map siez
    self.doors_num: int # Number of doors
    self.map: list[list[str | None]] # Initilise map
    self.start_door tuple[int, int] # If no start door is specified set it to the bottom middle
    ```
    ## Methods
    ```
    get_wall(self, door_pos) # Get the wall of position.
    set_door_positions(self, ignore: None | str = None) # Set door positions.
    capture_3x3(self, pos: tuple[int, int]) -> int # Return the number of neighbours that have the same character as in map[y][x].
    convert(self, pos: tuple[int, int]) -> None # Apply cellular automaton rules to a given point.
    valid_room(self) -> bool # Check for a valid room.
    add_visited_list(self, local_visited, visited) # Add the local visited list to the visited list.
    count_empty(self) # Count the empty squares in self.map.
    hash_function(self) # Hash function for seed generation.
    generate_dungeon(self) # Generate a dungeon map.
    print_map(self) # Print the map.
    ```
    """

    def __init__(
        self,
        empty_char: str = " _ ",
        wall_char: str = " # ",
        door_char=" / ",
        grid_size: int = 11,
        start_door: None | tuple[int, int] = None,
        doors=1,
    ) -> None:
        """Initialise room generator."""
        self.coordinates = (random.randint(1000,9999), random.randint(1000,9999)) # Room coordinates for seed hash
        self.empty_char = empty_char # Empty char
        self.wall_char = wall_char # Wall char
        self.door_char = door_char # Door char
        self.grid_size = grid_size # Map siez
        self.doors_num = doors # Number of doors
        self.map: list[list[str | None]] = [[]] # Initilise map
        if start_door == None:
            self.start_door = (grid_size - 1, grid_size // 2) # If no start door is specified set it to the bottom middle
        else:
            self.start_door = start_door
        self.doors = self.set_door_positions(ignore=self.get_wall(self.start_door)) # set the door positions except the start door

    def get_wall(self, door_pos):
        """Get the wall of position."""
        if door_pos[0] == 0:
            return "top"
        if door_pos[0] == self.grid_size - 1:
            return "bottom"
        if door_pos[1] == self.grid_size - 1:
            return "right"
        if door_pos[1] == 0:
            return "left"

    def set_door_positions(self, ignore: None | str = None):
        """Set door positions."""
        walls = {
            "top": (0, random.randint(2, self.grid_size - 3)),
            "bottom": (self.grid_size - 1, random.randint(2, self.grid_size - 3)),
            "right": (random.randint(2, self.grid_size - 3), self.grid_size - 1),
            "left": (random.randint(2, self.grid_size - 3), 0),
        }
        labels = ["top", "bottom", "right", "left"]
        doors = []
        if ignore is not None:
            walls.pop(ignore)
            labels.remove(ignore) # Remove ignored door
        for i in range(self.doors_num - 1):
            wall_label = random.choice(labels) # Randomly chooses a door
            labels.remove(wall_label) # Removes this door
            doors.append(walls.pop(wall_label)) # Adds the new door to doors
        return doors

    def capture_3x3(self, pos: tuple[int, int]) -> int:
        """Return the number of neighbours that have the same character as in map[y][x]."""
        y, x = pos
        directions = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ]
        neighbours = []
        for dy, dx in directions: # Chcck in all 8 adjacent directions
            ny, nx = y + dy, x + dx
            if 0 <= ny < len(self.map) and 0 <= nx < len(self.map):
                neighbours.append(self.map[ny][nx])
        return neighbours.count(self.map[y][x])

    def convert(self, pos: tuple[int, int]) -> None:
        """Apply cellular automaton rules to a given point."""
        y, x = pos
        char_count = self.capture_3x3(pos)
        character = self.map[y][x]
        if character == self.wall_char and char_count < 8:
            self.map[y][x] = self.empty_char
        elif character == self.empty_char and char_count >= 6:
            self.map[y][x] = self.wall_char
        else:
            self.map[y][x] = self.empty_char

    def valid_room(self) -> bool:
        """Check for a valid room."""
        visited = [[False for _ in range(len(self.map))] for _ in range(len(self.map))] # Creates a boolean visited map

        def dfs(y: int, x: int, goal: tuple[int, int]) -> bool:
            """Depth First Search sets visited squares to True."""
            if not (0 <= y < len(self.map) and 0 <= x < len(self.map)):
                return False
            if local_visited[y][x]:
                return False
            if self.map[y][x] == self.wall_char:
                return False
            local_visited[y][x] = True
            if (y, x) == (goal[0], goal[1]):
                return True
            if (
                dfs(y, x + 1, goal)
                or dfs(y, x - 1, goal)
                or dfs(y + 1, x, goal)
                or dfs(y - 1, x, goal)
            ): # Checks DFS in all directions reccursively
                return True
            return False

        found = False
        for door in self.doors:
            local_visited = [
                [False for _ in range(len(self.map))] for _ in range(len(self.map))
            ]
            found = dfs(self.start_door[0], self.start_door[1], door)
            if found == False:
                return False
            self.add_visited_list(local_visited, visited) # If a valid route to a door is found add the dfs findings to the visited
        for y in range(len(visited) - 1):
            for x in range(len(visited[y]) - 1):
                if visited[y][x] == False: # Wherever dfs couldnt reach is set to a wall
                    self.map[y][x] = self.wall_char
        return found

    def add_visited_list(self, local_visited, visited):
        """Add the local visited list to the visited list."""
        for y, row in enumerate(local_visited):
            for x, ele in enumerate(row):
                if ele == True:
                    visited[y][x] = True

    def count_empty(self):
        """Count the empty squares in self.map."""
        count = 0
        for row in self.map:
            for element in row:
                if element == self.empty_char:
                    count += 1
        return count

    def hash_function(self):
        """Hash function for seed generation."""
        x = self.coordinates[0]
        y = self.coordinates[1]
        x **= 2
        y **= 2
        x_len = len(str(abs(x)))
        y_len = len(str(abs(y)))
        x_half = str(x)[0 : x_len // 2]
        y_half = str(y)[0 : y_len // 2]
        return int(x_half + y_half)

    def generate_dungeon(self):
        """Generate a dungeon map."""
        if self.doors_num == 1:
            self.map = [
                [self.empty_char for i in range(self.grid_size)]
                for i in range(self.grid_size)
            ] # If the room is at the max level make an empty room
            for y in range(len(self.map)):
                for x in range(len(self.map)):
                    if (
                        y == 0
                        or y == len(self.map) - 1
                        or x == 0
                        or x == len(self.map) - 1
                    ) and self.map[y][x] != self.door_char:
                        self.map[y][x] = self.wall_char

            for door in self.doors + [self.start_door]:
                self.map[door[0]][door[1]] = self.door_char
        else:
            random.seed(self.hash_function()) # Creates the seed
            while True:
                self.map = [
                    [
                        (
                            self.wall_char
                            if random.randint(0, 100) < 30
                            else self.empty_char
                        )
                        for _ in range(self.grid_size)
                    ]
                    for _ in range(self.grid_size)
                ]

                for _ in range(3):
                    for y in range(len(self.map)):
                        for x in range(len(self.map)):
                            self.convert((y, x))

                directions = [
                    (-1, -1),
                    (0, -1),
                    (1, -1),
                    (-1, 0),
                    (1, 0),
                    (-1, 1),
                    (0, 1),
                    (1, 1),
                ]
                for door in self.doors + [self.start_door]:
                    for dy, dx in directions: # Set all the places above each door ot be air, this just makes valid rooms more livkely
                        try:
                            self.map[door[0] + dy][door[1] + dx] = self.empty_char  # type: ignore
                        except:
                            pass

                for y in range(len(self.map)):
                    for x in range(len(self.map)):
                        if (
                            y == 0
                            or y == len(self.map) - 1
                            or x == 0
                            or x == len(self.map) - 1
                        ) and self.map[y][x] != self.door_char: # Set the outside to be walls 
                            self.map[y][x] = self.wall_char

                for door in self.doors + [self.start_door]: # Place the doors
                    self.map[door[0]][door[1]] = self.door_char

                if self.valid_room() and self.count_empty() > 15:
                    break
        return self.map

    def print_map(self):
        """Print the map."""
        for row in self.map:
            print(row)
