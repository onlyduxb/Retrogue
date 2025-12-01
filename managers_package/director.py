"""Director."""

# -- Imports --

from graphics_package.building_scene import BuildingScene
from graphics_package.dungeon_scene import DungeonScene
from graphics_package.menu_scene import MenuScene
from graphics_package.overworld_scene import OverworldScene
from managers_package.save_manager import save_game
from managers_package.menu_manager import MenuManager
from managers_package.overworld_manager import OverworldManager
from factory_package.item_factory import ItemFactory, WeaponFactory
from managers_package.debug_manager import Debugger
from managers_package.entity_manager import Player


class Director:
    """Director.

    ## Description
    The director is the highest level in the hierarchy as it communicates the scenes with their related manager through 'actions'.
    Actions are dictionaries that are returned in response to an input from a user.
    The director first sends the key pressed to a scene which handles the input using the handle_input method.
    This returns an action which is passed to the related manager.
    ### Scene action example
    `{'action': 'move', 'vector': (-1, 0)}`
    The manager then applies game logic e.g moving the player on the map which then returns another action.
    ### Manager action example
    `{'action': 'enter', 'next_scene': [building_name], 'obj': [object], 'pos': (int, int)}`
    The director then selects the appropriate scene and extracts the object from the action above.
    ## Attributes
    ```
    self.stdscr = stdscr # Curses screen
    self.game_name: str # Save name to save data
    self.PLAYER: Player  # Player object
    self.debugger: Debugger  # Debugger (find in debugger_output/director.txt)
    self.overworld_manager: Overworld manager  # Overworld manager
    self.menu_manager: menu_manager  # Menu manager
    self.scene_managers: dict[str, scene_obj]  # Stores the manager objects
    self.scenes: dict[str, maanger_obj]  # Stores all the scenes
    self.previous_scene = None  # Stores the previous scene for the Menu
    ```
    ## Methods
    ```
    run() # Run the scene.
    new_scene(scene_name: str, new_scene_obj: manager, run_scene: bool = True) # Switch the scene.
    ```
    """

    def __init__(
        self,
        stdscr,
        overworld_manager,
        menu_manager,
        player,
        save_name,
        debugger,
        weapon_factory,
        item_factory,
    ) -> None:
        """Initialise director."""
        self.stdscr = stdscr  # Curses screen
        self.game_name: str = save_name  # Save name to save data
        self.PLAYER: Player = player  # Player object
        self.debugger: Debugger = (
            debugger  # Debugger (find in debugger_output/director.txt)
        )
        self.weapon_factory: WeaponFactory = weapon_factory  # Weapon factory
        self.item_factory: ItemFactory = item_factory  # Item factory
        self.overworld_manager: OverworldManager = (
            overworld_manager  # Overworld manager is permanent
        )
        self.menu_manager: MenuManager = menu_manager  # Menu manager is permanent
        self.scene_holders = {
            "building": BuildingScene,
            "dungeon": DungeonScene,
            "overworld": OverworldScene,
            "menu": MenuScene,
        }  # Holds all of the scene objects
        self.scene_managers = {
            "overworld": overworld_manager,
            "menu": menu_manager,
        }  # Stores the manager objects
        self.scenes = {}  # Stores all the scenes
        self.new_scene(
            scene_name="menu", new_scene_obj=self.menu_manager, run_scene=False
        )  # Adds the Menu scene
        self.new_scene(
            scene_name="overworld", new_scene_obj=self.overworld_manager
        )  # Adds and runs the Overworld scene
        self.previous_scene = None  # Stores the previous scene for the Menu

    def run(self):
        """Run the scene."""
        self.scenes[
            self.current_scene
        ].on_enter()  # Runs on enter to initilise the scene
        while True:  # Selects the current scene manager and scene
            scene = self.scenes[self.current_scene]
            scene_manager = self.scene_managers[self.current_scene]  # type: ignore
            scene.draw()  # Draws the scene
            key = self.stdscr.getch()  # Fetches player input
            next_scene = scene.handle_input(
                key
            )  # Scene recieves the player input and returns an action
            if not next_scene:  # If no key is pressed just continue
                continue
            action = next_scene.get("action")
            if next_scene.get("vector", None) is None:
                self.debugger.write(next_scene)

            match action:
                case "move":  # If the player attempts to move
                    scene_action = scene_manager.move_player(
                        next_scene["vector"]
                    )  # Manager recieves the movement vector
                    scene.change_text(
                        scene_action.get("notify", "")
                    )  # Types a notification in the bottom of the screen
                    if not scene_action.get("action") == "moved":  # Debugging
                        self.debugger.write(scene_action)
                    match scene_action.get("action"):
                        case "enter":  # Runs if the player attempts to enter a building
                            new_scene_obj = scene_action.get("obj")  # Building object
                            scene.on_exit()  # Exits the current scene
                            if scene_action.get("next_scene") in [
                                "shop",
                                "inn",
                            ]:  # Checks if the player is attempting to enter a building
                                scene_name = "building"
                            else:
                                scene_name = "dungeon"
                            self.new_scene(
                                scene_name=scene_name, new_scene_obj=new_scene_obj
                            )  # Changes the scene
                        case "room_transition":  # Dungeon room changes
                            room_activation = scene.manager_obj.current_room.activate_room(
                                scene_action.get("player_pos")
                            )  # Passes the vector into dungeon manager to activate the next room
                            self.debugger.write(room_activation)
                        case (
                            "exit"
                        ):  # Leaving any building returns you to the overworld
                            scene.on_exit()
                            self.current_scene = "overworld"
                        case "death":
                            self.scenes[self.current_scene].on_exit()
                            self.previous_scene = (
                                "overworld"  # Records the previous scene
                            )
                            self.menu_manager.current_menu = (
                                self.menu_manager.factory.create_death_menu()
                            )
                            self.current_scene = "menu"

                case "open_menu":  # Opens the menu
                    self.previous_scene = (
                        self.current_scene
                    )  # Records the previous scene
                    self.menu_manager.current_menu = (
                        self.menu_manager.factory.create_main_menu()
                    )
                    self.current_scene = "menu"
                case "exit_menu":
                    self.current_scene = (
                        self.previous_scene
                    )  # Retuns to the previous scene
                    self.previous_scene = None
                case "use_item":
                    item_index = next_scene.get("slot")
                    self.PLAYER.use_item(item_index)
                    self.PLAYER.inventory[item_index] = self.item_factory.create("None")

                case _:
                    menu_index = next_scene.get("menu_index")
                    if menu_index is not None:
                        result = scene.manager_obj.run_selected_menu(menu_index)
                        menu_action = result.get("action")
                        match menu_action:
                            case "resume":
                                self.current_scene = self.previous_scene
                                self.previous_scene = None
                            case "save_game":
                                save_game(
                                    save_name=self.game_name,
                                    player_data=self.PLAYER.get_save_data(),
                                    overworld_data=self.overworld_manager.get_save_data(),
                                    weapon_registry=self.weapon_factory.get_registry(),
                                    item_registry=self.item_factory.get_registry(),
                                    debugger=self.debugger,
                                )
                            case "give_item":
                                self.PLAYER.pickup(result.get("obj"))
                            case "respawn":
                                self.PLAYER.health = self.PLAYER.max_health
                                if (
                                    self.PLAYER.death_action().get("keep_inventory")
                                    == False
                                ):
                                    self.PLAYER.weapon = self.weapon_factory.create(
                                        "fists"
                                    )
                                    for slot_index in range(
                                        len(self.PLAYER.inventory) - 1
                                    ):
                                        self.PLAYER.inventory[slot_index] = (
                                            self.item_factory.create("None")
                                        )
                                self.new_scene("overworld", self.overworld_manager)
                                self.overworld_manager.randomise_player_pos()
                            case "quit":
                                quit()

    def new_scene(self, scene_name, new_scene_obj, run_scene=True):
        """Switch the scene."""
        new_scene = self.scene_holders[scene_name](
            self.stdscr
        )  # Runs the scene with the same screen (self.stdscr)
        new_scene.extract_obj(new_scene_obj)  # Loads the manager object
        if run_scene:
            new_scene.on_enter()  # If you dont want the scene to run set run_scene to False
        self.scene_managers[scene_name] = new_scene_obj
        self.scenes[scene_name] = new_scene
        self.current_scene = scene_name
        self.debugger.write(f"Set scene to {scene_name}")  # Debugging
