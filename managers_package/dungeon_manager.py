"""Dungeon manager."""

# -- Imports --

from typing import Any

from managers_package.room_manager import Exit, RoomManager


class DungeonManager:
    """Dungeon manager.

    ## Description
    Dungeon manager is the room controller for dungeons.
    ## Attributes
    ```
    self.player: Player # Player object
    self.debugger: Debugger # Debugger
    self.dungeon_size: int # How many rooms can stem from the original room
    self.graph: Room_graph # Room graph
    self.current_room: Room_manager | Any # Inital room
    ```
    ## Methods
    ```
    move_player(self, vector: tuple[int, int]) # Moves the player and all the entities in the current room
    start_dungeon(self) # Starts the dungeon by returning a room ready action to the director
    ```
    """

    def __init__(self, player, debugger, weapon_factory, item_factory, size=2) -> None:
        """Initalise dungeon manager."""
        self.player = player  # Player object
        self.debugger = debugger  # Debugger
        self.weapon_factory = weapon_factory  # Weapon factory
        self.item_factory = item_factory  # Item factory
        self.dungeon_size = size  # How many rooms can stem from the original room
        self.graph = RoomGraph(
            dungeon_manager=self,
            weapon_factory=self.weapon_factory,
            item_factory=self.item_factory,
            max_level=self.dungeon_size,
        )  # Room graph
        self.current_room: RoomManager | Any = self.graph.initial_room  # Inital room
        self.current_room.activate_room()  # Activates the inital room

    def move_player(self, vector: tuple[int, int]):
        """Move the player and all the entities in the current room."""
        self.current_room.move_agents()  # Moves all the agents in the current room
        result: dict[str, Any] = self.current_room.move_entity(self.player, vector)  # type: ignore
        match result.get("action"):  # Action to be returned to the director
            case "moved":
                if result.get("vector") != (0, 0):
                    self.current_room.generate_heat_map()
                noise_text = (
                    "You are invisible"
                    if result.get("noise") == False
                    else "You are visible"
                )
                return {"action": "moved", "vector": vector, "notify": noise_text}
            case (
                "room_transition"
            ):  # Adds the next room to the graph and moves the player into said room
                next_vec = result.get("vector")
                room_change = self.current_room.add_next_room(next_vec, result.get("player_pos"))  # type: ignore
                self.current_room = room_change.get("obj")
                self.debugger.write(room_change)
                if type(self.current_room).__name__ == "Exit":
                    return {"action": "exit"}
                return room_change
            case "deal_damage":
                return result
            case "open_chest":
                return result
            case "death":
                return result

    def start_dungeon(self):
        """Start the dungeon by returning a room ready action to the director."""
        return {"action": "room_ready", "map": self.current_room.map}


class RoomGraph:
    """Room graph.

    ## Description
    Controls the room flow for the dungeon.
    ## Attributes
    ```
    self.dungeon_manager: Dungeon_manager # Debugger
    self.initial_room: Room_manager # Initilises original room
    ```
    """

    def __init__(
        self, dungeon_manager: DungeonManager, weapon_factory, item_factory, max_level=2
    ) -> None:
        """Initialise graph."""
        self.dungeon_manager = dungeon_manager  # Debugger
        self.initial_room = RoomManager(
            player=self.dungeon_manager.player,
            dungeon_manager=self.dungeon_manager,
            debugger=self.dungeon_manager.debugger,
            weapon_factory=weapon_factory,
            item_factory=item_factory,
            level=0,
            max_level=max_level,
            doors=4,
        )  # Initilsies a room
        self.initial_room.down = Exit()  # Sets the bottom door to exit to the overworld
