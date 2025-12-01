"""Building Scene."""

# -- Imports --

import curses

from managers_package.building_manager import Inn, Shop

from .scene import Scene


class BuildingScene(Scene):
    """Building scene.

    ## Description
    Scene for buildings, child class of Scene
    ## Attributes
    ```
    self.stdscr: curses.win # Screen
    self.manager_obj # Stores the manager of the building
    self.map # Stores the layout of the building
    ```
    ## Methods
    ```
    extract_obj(self, obj: Shop | Inn) # Extracts the manager object and map
    on_enter(self) # Runs on enter to ge the max size of the screen
    draw(self) # Draws the current scene
    ```
    """

    def __init__(self, stdscr) -> None:
        """Initialise building scene."""
        super().__init__(stdscr) # Screen

    def extract_obj(self, obj: Shop | Inn):
        """Extract the manager object."""
        self.manager_obj = obj
        self.map = self.manager_obj.layout  # Layout of map

    def on_enter(self):
        """Run when entering a scene."""
        h, w = self.stdscr.getmaxyx() # Get screen bounds

    def draw(self):
        """Draw the current scene."""
        self.stdscr.clear() # Clear screen
        for y, row in enumerate(self.map): # Colour tiles
            x_pos = 0
            for tile in row:
                if tile == " . ":
                    color = curses.color_pair(2)
                elif tile == " P ":
                    color = curses.color_pair(4)
                elif tile == " # ":
                    color = curses.color_pair(1)
                else:
                    color = curses.color_pair(3)

                self.stdscr.addstr(y, x_pos, tile, color)
                x_pos += len(tile)
        self.stdscr.refresh() # Refresh screen
