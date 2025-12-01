"""Overworld manager."""

# -- Imports --

import random

from generators_package.entity_generator import Player
from generators_package.overworld_generation import OverworldGeneration
from managers_package.building_manager import Inn, Shop
from managers_package.dungeon_manager import DungeonManager


class OverworldManager:
    """Overworld manager.

    ## Description
    Overworld manager applies game logic from director and then returns an action back to the director for the next scene.
    ## Attributes
    ```
    self.player = Player # Player object
    self.debugger: Debugger # Debugger
    self.map_size: int
    self.coordinates: tuple[int, int] # Coordinates for the overworld, used for hashing to generate a seed for the overworld
    self.overworld_generator: Overworld_Generation # Generator for the overworld
    ```
    ## Methods
    ```
    # -- Minimap --
    generate_minimap(grid_divisions: int) -> list[list[str]] # Generates a minimap
    generate_centres(self, grid_divisions=10 # Generates the centres of each one of the grid divisions
    get_square(self, center, size) # Return a list of coordinates covering a square of side 'size' centered on 'center'. 'size' is the full side length (integer >= 1). Works correctly for even or odd sizes.

    # -- Player --
    get_visible_window(self) # Retruns a 5x5 view used to display what the player can see.
    move_player(self, vector) # Moves the player with validation in the overworld by a provided vector

    # -- Building activation --
    activate_building(self, building: Shop | Inn) # Sends activation action to the director

    # -- Save data --
    get_save_data(self) # Returns the save data of the overworld

    ```
    """

    def __init__(
        self,
        player: Player,
        debugger,
        weapon_factory,
        item_factory,
        map_size: int = 50,
        coordinates=(random.randint(100, 1000000), random.randint(100, 1000000)),
        player_pos=None,
    ) -> None:
        """Initilise overworld manager."""
        self.player = player  # Player object
        self.debugger = debugger  # Debugger
        self.weapon_factory=weapon_factory # Weapon factory
        self.item_factory=item_factory # Item factory
        self.map_size = map_size
        self.coordinates = coordinates  # Coordinates for the overworld, used for hashing to generate a seed for the overworld
        self.overworld_generator = OverworldGeneration(
            debugger=self.debugger,
            map_size=self.map_size,
            coordinates=self.coordinates,
        )  # Generator for the overworld

        self.dungeon_char = self.overworld_generator.dungeon_char  # Dungeon char
        self.map: list[list[str]] = (
            self.overworld_generator.generate_map()
        )  # Generates map

        if (
            player_pos == None
        ):  # If there is no passed player position assign the player to a random position
            self.randomise_player_pos()
        else:  # Otherwise set the player to the provided position
            self.player_pos = player_pos

        self.poi_coordinates = (
            self.overworld_generator.get_poi_coordinates()
        )  # Gets the poi cooridnates
        self.poi_dict = (
            self.overworld_generator.get_poi_info()
        )  # Get which pois are at which coordinates

        self.dungeon_manager_dict = {}  # All dungeons with their associated managers

        for poi_coord, poi_type in self.poi_dict:
            if poi_type == " Δ ":
                self.dungeon_manager_dict[poi_coord] = DungeonManager(
                    self.player, self.debugger, self.weapon_factory, self.item_factory
                )  # Assings a new dungeon manager to a point

        while True:
            if self.map[self.player_pos[0]][self.player_pos[1]] in [
                self.dungeon_char,
                " S ",
                " I ",
            ]:
                self.map = self.overworld_generator.generate_map()  # Genrates the map
            else:
                break
        self.player_pos_char = self.map[self.player_pos[0]][self.player_pos[1]]
        self.map[self.player_pos[0]][self.player_pos[1]] = self.player.char

        self.buildings_dungeons = {}  # All buildings and dungeons

        for coord, value in self.poi_dict.items():
            if value != " T ":
                self.buildings_dungeons[coord] = value

        building_info = self.overworld_generator.get_building_info()
        for coord, value in building_info.items():
            self.buildings_dungeons[coord] = value

    def randomise_player_pos(self):
        """Randomise player position."""
        self.player_pos = (
                random.randint(0, len(self.map) - 1),
                random.randint(0, len(self.map) - 1),
            )
    # -- Minimap --

    def generate_minimap(self, grid_divisions=10):
        """Generate the minimap."""
        poi_info = self.overworld_generator.get_poi_info()  # Gets the POI information
        minimap = []  # Initlise the minimap
        centres = self.generate_centres(
            grid_divisions
        )  # Generates the centres of each one of the grid divisions
        cell_h = max(1, self.map_size // grid_divisions)  # Grid height
        for centre_row in centres:
            new_row = []
            for center in centre_row:  # Checks to find out what exists within each grid
                found = False
                square = self.get_square(
                    center, cell_h
                )  # Creates a square from each division
                for coordinate in square:
                    if (
                        coordinate == self.player_pos
                    ):  # If the player is in a square set the minimap at that position to show a 'P'
                        found = True
                        new_row.append("P")
                        break
                if not found:  # Checks to see what poi may exist within this area
                    for coordinate in square:
                        if coordinate in poi_info.keys():
                            new_row.append(poi_info[coordinate].strip())
                            found = True
                            break
                if not found:  # Else just assign it as empty
                    new_row.append(".")
            minimap.append(new_row)
        return minimap  # Returns the minimap

    def generate_centres(self, grid_divisions=10):
        """Generate the centres of each one of the grid divisions."""
        centres = []
        cell_h = self.map_size // grid_divisions
        for row in range(grid_divisions):
            row_centres = []
            for col in range(grid_divisions):
                cy = min(self.map_size - 1, int((row * cell_h) + cell_h // 2))
                cx = min(self.map_size - 1, int((col * cell_h) + cell_h // 2))
                row_centres.append((cy, cx))
            centres.append(row_centres)
        return centres

    def get_square(self, center, size):
        """Return a list of coordinates covering a square of side 'size' centered on 'center'."""
        if size <= 0:
            return []

        cy, cx = int(center[0]), int(center[1])

        half = size // 2
        start_y = cy - half
        start_x = cx - half

        start_y = max(0, start_y)
        start_x = max(0, start_x)
        end_y = min(len(self.map), start_y + size)
        end_x = min(len(self.map[0]), start_x + size)

        square = [(y, x) for y in range(start_y, end_y) for x in range(start_x, end_x)]
        return square

    # -- Player --

    def get_visible_window(self):
        """Retruns a 5x5 view used to display what the player can see."""
        height = len(self.map)
        width = len(self.map[0]) if height > 0 else 0
        desired_view_size = 10
        if desired_view_size < 1:
            desired_view_size = 1
        half = (desired_view_size - 1) // 2
        view_size = half * 2 + 1
        view_window = [[" . " for _ in range(view_size)] for _ in range(view_size)]
        py, px = self.player_pos
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                map_y = py + dy
                map_x = px + dx
                win_y = dy + half
                win_x = dx + half
                if 0 <= map_y < height and 0 <= map_x < width:
                    view_window[win_y][win_x] = self.map[map_y][map_x]
                else:
                    view_window[win_y][win_x] = "   "
        view_window[half][half] = " P "
        return view_window

    def move_player(self, vector):
        """Move the player with validation in the overworld by a provided vector."""
        if (
            vector is None
        ):  # If there is no vector just set the vector to be stationary (0,0)
            vector = (0, 0)
        if 0 <= self.player_pos[0] + vector[0] < len(self.map) and 0 <= self.player_pos[
            1
        ] + vector[1] < len(
            self.map
        ):  # Check that the player is moving within the bounds of the map
            self.generate_minimap()  # Genrates a minimap
            last_pos = self.player_pos  # Stores the current position of the player
            self.map[self.player_pos[0]][
                self.player_pos[1]
            ] = self.player_pos_char  # Sets the old position to be the old character
            self.player_pos = (
                self.player_pos[0] + vector[0],
                self.player_pos[1] + vector[1],
            )  # Sets the player position to be the new position
            self.player_pos_char = self.map[self.player_pos[0]][
                self.player_pos[1]
            ]  # Stores the character below the player character
            self.map[self.player_pos[0]][
                self.player_pos[1]
            ] = self.player.char  # Sets the new position to be the player character

            if (
                self.player_pos in self.buildings_dungeons.keys()
            ):  # Checks to see if the player is attempting to enter a POI
                building_char = self.buildings_dungeons[
                    self.player_pos
                ]  # Gets the character of the building

                self.map[self.player_pos[0]][
                    self.player_pos[1]
                ] = building_char  # To prevent the player from overwriting the building character rewrite it
                self.player_pos = last_pos  # Gets the last position of the player before they entered the building
                self.player_pos_char = self.map[self.player_pos[0]][self.player_pos[1]]

                if building_char == " Δ ":  # Dungeon
                    return {
                        "action": "enter",
                        "next_scene": "dungeon",
                        "obj": DungeonManager(self.player, self.debugger, item_factory=self.item_factory, weapon_factory=self.weapon_factory),
                        "pos": self.player_pos,
                    }  # Returns action to director
                elif building_char == " S ":  # Shop
                    return {
                        "action": "enter",
                        "next_scene": "shop",
                        "obj": Shop(self.player),
                        "pos": self.player_pos,
                    }  # Returns action to director
                elif building_char == " I ":  # Inn
                    return {
                        "action": "enter",
                        "next_scene": "inn",
                        "obj": Inn(self.player),
                        "pos": self.player_pos,
                    }  # Returns action to director
        return {
            "action": "moved",
            "player_pos": self.player_pos,
        }  # Returns action to director

    # -- Building activation --

    def activate_building(self, building: Shop | Inn):
        """Send activation action to the director."""
        return {"action": "enter_building", "building": building}

    # -- Save data --

    def get_save_data(self):
        """Return the save data of the overworld."""
        return {"seed_coordinates": self.coordinates, "player_pos": self.player_pos}
