"""Menu scene."""

# -- Imports --

import curses

from graphics_package.scene import Scene
from managers_package.menu_manager import MenuManager


class MenuScene(Scene):
    """Menu scene.

    ## Description
    Menu scene takes the input from the user to display the menu options.
    ## Attributes
    ```
    self.stdscr: curses.win # Screen
    self.options: list[str] # List of options
    self.manager_obj.current_menu.current_selection: int # Index of current option
    ```
    ## Methods
    ```
    on_enter(self) # Runs when entering a scene
    draw(self) # Draws the current scene
    handle_input(self, key) # Different to other scenes as this scene only deals with selecting the new option it does not take in inputs such as 'A' or 'D'
    ```
    """

    def __init__(self, stdscr) -> None:
        """Initialise menu scene."""
        super().__init__(stdscr)  # Screen
        self.options = []  # List of options
        self.last_options = [None]

    def on_enter(self):
        """Run when entering a scene."""
        self.draw()

    def draw(self):
        """Draw the current scene."""
        self.options = self.manager_obj.current_menu.get_labels()
        # if self.last_options[0] != self.options[0]:
        #     self.manager_obj.current_menu.current_selection
        self.last_options=self.options
        self.stdscr.clear()
        # Correct breadcrumb placement centered safely
        h, w = self.stdscr.getmaxyx()
        for idx, option in enumerate(self.options):
            x = w // 2 - len(self.options) // 2
            y = h // 2 - len(self.options) // 2 + idx + 1
            if idx == self.manager_obj.current_menu.current_selection:
                self.stdscr.attron(curses.color_pair(4))  # highlight
                self.stdscr.addstr(y, x, option)
                self.stdscr.attroff(curses.color_pair(4))
            else:
                self.stdscr.addstr(y, x, option)
        self.stdscr.refresh()

    def handle_input(self, key):
        """Different to other scenes as this scene only deals with selecting the new option it does not take in inputs such as 'A' or 'D'."""
        match key:
            case 'w' | 'KEY_UP':
                self.manager_obj.current_menu.current_selection = (self.manager_obj.current_menu.current_selection - 1) % len(
                self.options
                )  # Selects the option above
                self.draw()
            case "s" | 'KEY_DOWN':
                self.manager_obj.current_menu.current_selection = (self.manager_obj.current_menu.current_selection + 1) % len(
                    self.options
                )  # Selects the option below
                self.draw()
            case "\n" | 'KEY_RIGHT':
                return {"action": "select_menu", "menu_index": self.manager_obj.current_menu.current_selection}
            case "m" | "":
                return {"action": "exit_menu"}
        
    def extract_obj(self, obj: MenuManager):
        """Extract manager."""
        self.manager_obj = obj