"""New menu manager integrated with MenuFactory."""

# -- Imports --

from generators_package.menu_generator import Menu
from managers_package.debug_manager import Debugger
from factory_package.menu_factory import MenuFactory, WeaponFactory, ItemFactory
from generators_package.entity_generator import Player


class MenuManager:
    """Menu manager with stack-based navigation and dynamic callbacks."""

    def __init__(self, debugger: Debugger, weapon_factory: WeaponFactory, item_factory: ItemFactory, player: Player) -> None:
        """Initialize menu manager."""
        self.debugger = debugger
        self.factory = MenuFactory(debugger, player, weapon_factory, item_factory)
        self.player=player
        self.weapon_factory = weapon_factory
        self.item_factory = item_factory
        root_menu=self.factory.create_main_menu()
        self.current_menu = root_menu
        self.menu_stack: list[Menu] = [root_menu]

    def add_menu(self, menu: Menu) -> Menu:
        """Add a new menu."""
        self.menu_stack.append(menu)
        self.current_menu = menu
        return menu

    def back(self):
        """Go back to the previous menu in the stack."""
        if len(self.menu_stack) > 1:
            self.menu_stack.pop()
            self.current_menu = self.menu_stack[-1]

    def get_breadcrumbs(self) -> str:
        """Return the path of menus to current menu."""
        path = ''
        for menu in self.menu_stack:
            path+=f'{menu.name}/'
        return path

    def run_selected_menu(self, index: int):
        """Run the selected option's callback and handle navigation actions."""
        selected_callback = self.current_menu.get_option(index)
        self.debugger.write(f'Running {selected_callback}')
        result = selected_callback()
        self.debugger.write(f'Returned {result}')

        if isinstance(result, dict):
            action = result.get("action")
            match action:
                case "new_menu":
                    new_menu = result.get("menu_obj")
                    if new_menu:
                        self.menu_stack.append(new_menu)
                        self.current_menu = new_menu
                case "back":
                    self.back()
                case "stay":
                    pass  # do nothing
                case "toggle_debugger":
                    self.debugger.on = not self.debugger.on
                case "resume":
                    return {'action': "resume"}
                case "save_game":
                    return {'action': "save_game"}
                case "give_weapon":
                    weapon_name=result.get('weapon')
                    weapon_rarity=result.get('rarity')
                    params = dict(self.weapon_factory._data[weapon_name]) # type: ignore
                    params["rarity"] = weapon_rarity
                    return {'action': 'give_item', "obj": self.weapon_factory._build(params)}
                case "give_item":
                    item_name=result.get('item')
                    return  {'action': 'give_item', "obj": self.item_factory.create(item_name)} # type: ignore
                case "toggle_keep_inventory":
                    self.player.keep_inventory = not self.player.keep_inventory
                case "toggle_permadeath":
                    self.player.permadeath = not self.player.permadeath
        return result