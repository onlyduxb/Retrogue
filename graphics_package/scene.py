"""Scene."""

# -- Imports --

from typing import Any


class Scene:
    """Scene.

    ## Description
    Base class for all scenes, stores all the default attributes and methods for all scenes.
    ## Attributes
    ```
    self.stdscr: str # Screen
    self.bottom_text: str # Text at the bottom of the scene
    ```
    ## Methods
    ```
    on_enter(self) # Runs when entering a scene
    on_exit(self) # Runs when exiting a scene
    draw(self) # Draws the current scene
    extract_obj(self, obj: Any) # Extracts the manager object
    handle_input(self, key) -> Any # Takes a key input from the player and returns an action to the director to be passed to the manager, by default move the player in one of 4 directions
    add_text_bottom(self) # Adds self.bottom_text to the bottom of the screen
    change_text(self, text='') # Changes self.bottom_text to a new piece of text
    get_class_name(self) # Returns the class name
    ```
    """

    def __init__(self, stdscr) -> None:
        """Initialise scene."""
        self.stdscr = stdscr
        self.bottom_text=''

    def on_enter(self):
        """Run when entering a scene."""
        pass

    def on_exit(self):
        """Run when exiting a scene."""
        pass

    def draw(self):
        """Draw the current scene."""
        pass

    def extract_obj(self, obj: Any):
        """Extract the manager object."""
        pass

    def handle_input(self, key) -> Any:
        """Take a key input from the player and returns an action to the director to be passed to the manager."""
        match key:
            case "w" | "KEY_UP":
                return {"action": "move", "vector": (-1, 0)}
            case "s" | "KEY_DOWN": 
                return {"action": "move", "vector":(1, 0)}
            case "a" | "KEY_LEFT": 
                return {"action": "move", "vector":(0, -1)}
            case "d" | "KEY_RIGHT": 
                return {"action": "move", "vector":(0, 1)}
            case "m" | '':
                return {"action": "open_menu"}
            case 'q':
                return {'action': 'use_item', 'slot': 0}
            case 'e':
                return {'action': 'use_item', 'slot': 1}
            case _:
                return {"action": "move", "vector": (0,0)} # No movement
    
    def add_text_bottom(self):
        """Add self.bottom_text to the bottom of the screen."""
        height, width = self.stdscr.getmaxyx()
        y = height - 1
        x = 0
        self.stdscr.move(y, 0)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(y, x, self.bottom_text[: width - 1])
        self.stdscr.refresh()

    def change_text(self, text=''):
        """Change self.bottom_text to a new piece of text."""
        self.bottom_text=str(text)

    def get_class_name(self):
        """Return the class name."""
        return type(self).__name__