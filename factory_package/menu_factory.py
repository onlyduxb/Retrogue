"""Menu factory."""

# -- Imports --

from typing import Callable, Dict

from generators_package.menu_generator import Menu
from managers_package.debug_manager import Debugger
from generators_package.entity_generator import Player
from .item_factory import WeaponFactory, ItemFactory

current_rarity=0

class MenuFactory:
    """Menu factory.

    ## Description
    ## Attributes
    ## Methods
    """

    def __init__(self, debugger, player, weapon_factory, item_factory) -> None:
        """Initilise menu factory."""
        self.weapon_factory: WeaponFactory = weapon_factory
        self.item_factory: ItemFactory = item_factory
        self.player: Player = player
        self.debugger: Debugger = debugger

    def create_menu(self, options: Dict[Callable[[], str], Callable], name=''):
        """Create a menu."""
        menu = Menu(options=options, name=name)
        return menu
    
    def create_death_menu(self):
        """Create death menu."""
        def generate_options():
            if self.player.permadeath:
                options[lambda: 'Quit game'] = quit_game
                return
            options[lambda: 'Respawn'] = respawn

        def respawn():
            return {'action': 'respawn'}
        def quit_game():
            return {'action': 'quit'}
        
        options = {}
        generate_options()
        return self.create_menu(options, 'You died')

    def create_give_weapon_menu(self):
        """Create the menu to give player weapons."""
        rarities=['Common', 'Rare', 'Epic', 'Legendary']
        def go_back():
            return {"action": "back"}
        def change_rarity():
            global current_rarity
            current_rarity=(current_rarity+1)%(len(rarities))
            return {"action": 'change_rarity', 'rarity': rarities[current_rarity]}


        options = {
        }

        for internal_name, params in  self.weapon_factory.get_registry().items():
            weapon_obj = self.weapon_factory.create(internal_name)

            def action(w=weapon_obj):
                return {"action": "give_weapon", "weapon": w.name, 'rarity': rarities[current_rarity]}

            options[lambda wname=params["name"]: f"Give {wname}"] = action

        options[lambda: f"Change rarity ({rarities[current_rarity]})"] = change_rarity
        options[lambda: "Back"] = go_back

        return self.create_menu(options, 'give_weapon')
    
    def create_give_item_menu(self):
        """Create give item menu."""
        def go_back():
            return {'action': 'back'}

        options={}

        for internal_name, params in  self.item_factory.get_registry().items():
            item_obj = self.item_factory.create(internal_name)

            def action(i=item_obj):
                return {"action": "give_item", "item": i.name}

            options[lambda iname=params["name"]: f"Give {iname}"] = action
        options[lambda: "Back"] = go_back

        return self.create_menu(options, 'give_item')

    def create_admin_menu(self):
        """Create admin menu."""
        def go_back():
            return {"action": "back"}
        def open_give_weapon_menu():
            return {"action": "new_menu", "menu_obj": self.create_give_weapon_menu()}
        def open_give_item_menu():
            return {"action": "new_menu", "menu_obj": self.create_give_item_menu()}
        def toggle_debugger():
            return {"action": "toggle_debugger"}
        
        options = {
            lambda: f"Toggle debugger ({self.debugger.on})": toggle_debugger,
            lambda: "Give weapon": open_give_weapon_menu,
            lambda: "Give item": open_give_item_menu,
            lambda: "Back": go_back
        }
        return self.create_menu(options, 'admin_menu')
    
    def create_settings_menu(self):
        """Create game settings menu."""
        def go_back():
            return {'action': 'back'}
        def toggle_keep_inventory():
            return {'action': "toggle_keep_inventory"}
        def toggle_permadeath():
            return {'action': "toggle_permadeath"}
        
        options = {
            lambda: f'Toggle keep inventory ({self.player.keep_inventory})': toggle_keep_inventory,
            lambda: f'Toggle permadeath ({self.player.permadeath})': toggle_permadeath,
            lambda: 'Back': go_back
        }
        return self.create_menu(options, 'game_settings')

    def create_options_menu(self):
        """Create options menu."""
        def go_back():
            return {"action": "back"}
        def open_settings_menu():
            return {"action": "new_menu", "menu_obj": self.create_settings_menu()}
        
        def open_admin_menu():
            return {"action": "new_menu", "menu_obj": self.create_admin_menu()}

        options = {
            lambda: "Open settings menu": open_settings_menu,
            lambda: "Open admin menu": open_admin_menu,
            lambda: "Back": go_back
        }

        return self.create_menu(options, 'options')

    def create_main_menu(self):
        """Create Main menu."""

        def resume_game():
            return {'action': "resume"}

        def open_options():
            return {"action": "new_menu", "menu_obj": self.create_options_menu()}

        def save_exit_game():
            return {"action": "save_game"}

        options = {
            lambda: "Resume Game": resume_game,
            lambda: "Options": open_options,
            lambda: "Save and exit": save_exit_game
        }

        return self.create_menu(options, 'main_menu')