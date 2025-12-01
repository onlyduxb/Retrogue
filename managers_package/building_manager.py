"""Building manager."""

# -- Imports --

from generators_package.overworld_generation import InnGenerator, ShopGenerator


class Inn:
    """Inn.

    ## Description
    Stores the data of the Inn and the player inside
    ## Attributes
    ```
    self.PLAYER: Player # Player object
    self.layout: Inn_generator # Generates the layout of the Inn
    self.PLAYER_coordinates = (len(self.layout) - 2, len(self.layout) // 2) # Stores the cooridnates of the player inside of the Inn, initally set to the bottom middle which is where the door is placed
    ```
    ## Methods
    ```
    move_player(self, vector: tuple[int, int]) # Attempts to move the player
    ```
    """

    def __init__(self, player) -> None:
        """Initalise Inn."""
        self.PLAYER = player  # Player object
        self.layout = InnGenerator(self.PLAYER).layout  # Layout of the Inn
        self.PLAYER_coordinates = (
            len(self.layout) - 2,
            len(self.layout) // 2,
        )  # Stores the cooridnates of the player inside of the Inn, initally set to the bottom middle which is where the door is placed

    def move_player(self, vector: tuple[int, int]):
        """Attempt to move the player."""
        move_attempt = self.layout[self.PLAYER_coordinates[0] + vector[0]][
            self.PLAYER_coordinates[1] + vector[1]
        ]  # Gets the tile where the player is attempting to move to
        if (
            move_attempt == " _ "
        ):  # If the player is attempting to move into an empty space
            self.layout[self.PLAYER_coordinates[0]][self.PLAYER_coordinates[1]] = " _ "
            self.PLAYER_coordinates = (
                self.PLAYER_coordinates[0] + vector[0],
                self.PLAYER_coordinates[1] + vector[1],
            )
            self.layout[self.PLAYER_coordinates[0]][self.PLAYER_coordinates[1]] = " P "
            return {
                "action": "move",
                "player_pos": self.PLAYER_coordinates,
            }  # Action is returned to director
        elif (
            move_attempt == " / "
        ):  # If the player attempts to leave then exit them to the overworld
            return {"action": "exit"}  # Action is returned to director
        return {
            "action": "moved",
            "player_pos": self.PLAYER_coordinates,
        }  # Action is returned to director


class Shop:
    """Shop.

    ## Description
    Stores the data of the Shop and the player inside
    ## Attributes
    ```
    self.PLAYER: Player # Player object
    self.layout: Inn_generator # Generates the layout of the Shop
    self.PLAYER_coordinates = (len(self.layout) - 2, len(self.layout) // 2) # Stores the cooridnates of the player inside of the Shop, initally set to the bottom middle which is where the door is placed
    ```
    ## Methods
    ```
    move_player(self, vector: tuple[int, int]) # Attempts to move the player
    ```
    """

    def __init__(self, player) -> None:
        """Initialise shop."""
        self.PLAYER = player  # Player object
        self.layout = ShopGenerator(self.PLAYER).layout  # Layout of the Shop
        self.PLAYER_coordinates = (
            len(self.layout) - 2,
            len(self.layout) // 2,
        )  # # Stores the cooridnates of the player inside of the Shop, initally set to the bottom middle which is where the door is placed

    def move_player(self, vector: tuple[int, int]):
        """Attempt to move the player."""
        move_attempt = self.layout[self.PLAYER_coordinates[0] + vector[0]][
            self.PLAYER_coordinates[1] + vector[1]
        ]  # Gets the tile where the player is attempting to move to
        if (
            move_attempt == " _ "
        ):  # If the player is attempting to move into an empty space
            self.layout[self.PLAYER_coordinates[0]][self.PLAYER_coordinates[1]] = " _ "
            self.PLAYER_coordinates = (
                self.PLAYER_coordinates[0] + vector[0],
                self.PLAYER_coordinates[1] + vector[1],
            )
            self.layout[self.PLAYER_coordinates[0]][self.PLAYER_coordinates[1]] = " P "
            return {
                "action": "move",
                "player_pos": self.PLAYER_coordinates,
            }  # Action is returned to director
        elif (
            move_attempt == " / "
        ):  # If the player attempts to leave then exit them to the overworld
            return {"action": "exit"}  # Action is returned to director
        return {
            "action": "moved",
            "player_pos": self.PLAYER_coordinates,
        }  # Action is returned to director
