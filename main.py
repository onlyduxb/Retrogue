"""Retrogue."""

# -- Imports --

from time import sleep, ctime
from typing import Any
import random
import curses
import os
from art import text2art
from factory_package.item_factory import WeaponFactory, ItemFactory
from managers_package.overworld_manager import OverworldManager
from managers_package.menu_manager import MenuManager
from managers_package.debug_manager import Debugger
from managers_package import load_game
from managers_package.director import Director
from generators_package.entity_generator import Player


def clear():
    """Use an escape character sequence to clear screen."""
    print("\033c")


def get_last_edited_times(path_to_file: str, file_name: str):
    """Return the last edited time of a file."""
    return ctime(os.path.getmtime(f"{path_to_file}/{file_name}"))


def launcher(stdscr, player, overworld_coordinates, player_position, file_name):
    """Launch the director which starts the game loop."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_YELLOW, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, -1, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)
    curses.init_pair(5, curses.COLOR_CYAN, -1)
    curses.init_pair(6, curses.COLOR_RED, -1)
    curses.curs_set(0)

    overworld = OverworldManager(
        player=player,
        weapon_factory=weapon_factory,
        item_factory=item_factory,
        coordinates=overworld_coordinates,
        player_pos=player_position,
        debugger=debug_manager,
    )
    menu = MenuManager(
        debugger=debug_manager,
        weapon_factory=weapon_factory,
        item_factory=item_factory,
        player=player,
    )

    director = Director(
        stdscr,
        overworld_manager=overworld,
        menu_manager=menu,
        player=player,
        weapon_factory=weapon_factory,
        item_factory=item_factory,
        save_name=file_name,
        debugger=debug_manager,
    )

    director.run()


if __name__ == "__main__":
    debug_manager = Debugger("debug")
    CURRENT_PATH = os.path.curdir  # Gets the current directory to load game save

    SAVE_PATH = f"{CURRENT_PATH}/game_data"  # Path to game saves

    art = text2art("retrogue", font="Chiseled")  # Title screen
    for row in art:
        for letter in row:  # type: ignore
            print(letter, end="")
            sleep(0.001)

    load_save = input("\n Would you like to load a save (y/n) \n-> ")
    clear()
    weapon_factory = WeaponFactory()  # Weapon factory
    item_factory = ItemFactory()  # Item factory

    if load_save == "y":
        saves = os.listdir(SAVE_PATH)
        print("Current saves: ")
        for save in saves:
            print(
                f"[{get_last_edited_times(SAVE_PATH, save)}] {save.removesuffix('.json')}"
            )
        save_name = input("Enter save name: ")
        save_data = load_game(save_name, debug_manager)  # Loads the game save data
        item_factory.load_registry(save_data["item_registry"])
        weapon_factory.load_registry(save_data["weapon_registry"])
        overworld_data = save_data["overworld_data"]
        coordinates = overworld_data["seed_coordinates"]
        player_pos = overworld_data["player_pos"]
        player_data = save_data["player_data"]
        weapon = player_data["weapon"]
        inventory = [item_factory.create(item["name"]) for item in player_data["inventory"]]  # type: ignore

        player_object = Player(
            debugger=debug_manager,
            health=player_data["health"],
            level=player_data["level"],
            weapon=weapon_factory._build(weapon),  # type: ignore
            inventory=inventory,
        )

    else:
        save_name = input("Enter a name to save the game under: ")
        weapon_factory.initilise_registry()
        item_factory.initilise_registry()
        player_object = Player(
            debugger=debug_manager,
            weapon=weapon_factory.create("fists"),
            inventory=[item_factory.create("None"), item_factory.create("None")],
        )  # Creates player obj
        coordinates = (
            random.randint(0, 10000),
            random.randint(0, 10000),
        )  # Randomly generates coordinates
        player_pos = None
    os.environ.setdefault("ESCDELAY", "25")
    curses.wrapper(launcher, player_object, coordinates, player_pos, save_name)
