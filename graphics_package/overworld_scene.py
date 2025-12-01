"""Overworld scene."""

# -- Imports --

import curses

from managers_package.overworld_manager import OverworldManager

from .scene import Scene


class OverworldScene(Scene):
    """Overworld scene.

    ## Description
    Scene for overworld, child class of Scene.
    TEST
    ## Attributes
    ```
    self.stdscr: curses.win # Inherrited from Scene class
    self.bottom_text: str # Text to be displayed at the bottom of the screen
    self.minimap_win: curses.win # Minimap to be displayed on the right hand side of the screen
    ```
    ## Methods
    ```
    on_enter(self) # Runs when entering a scene
    on_exit(self) # Runs when exiting a scene
    draw(self) # Draws the current scene
    draw_side_win(self) # Draws the minimap
    extract_obj(self, obj: Any) # Extracts the manager object
    handle_input(self, key) -> Any # Returns action to director based on keypress
    add_text_bottom(self) # Adds self.bottom_text to the bottom of the screen
    change_text(self, text='') # Changes self.bottom_text to a new piece of text
    get_class_name(self) # Returns the class name
    update_map(self, new_map) # Updates the map
    ```
    """

    def __init__(self, stdscr) -> None:
        """Initialise overworld scene."""
        super().__init__(stdscr)
        self.manager_obj = None
        self.minimap_win = None  # Minimap window

    def extract_obj(self, obj: OverworldManager):
        """Extract the manager object."""
        self.manager_obj = obj  # Manager obj

    def on_enter(self):
        """Run when entering a scene."""
        h, w = self.stdscr.getmaxyx()  # Gets the window size
        self.minimap_win = curses.newwin(12, 20, 0, w - 20)  # Creates minimap window

    def draw(self):
        """Draw the current scene."""
        self.stdscr.clear()  # Clears the screen
        if self.manager_obj is not None:
            for y, row in enumerate(
                self.manager_obj.get_visible_window()
            ):  # Gets the visible window
                x_pos = 0
                for tile in row:  # Itterates through the map applying colours
                    if tile == " . ":
                        color = curses.color_pair(2)
                    elif tile == " P ":
                        color = curses.color_pair(4)
                    elif tile == " = ":
                        color = curses.color_pair(1)
                    else:
                        color = curses.color_pair(3)

                    self.stdscr.addstr(y, x_pos, tile, color)
                    x_pos += len(tile)
        self.stdscr.refresh()  # Refreshes the screen
        self.draw_side_win()  # Draws the minimap

    def draw_side_win(self):
        """Autoscale the side window to fit the provided minimap and draw it."""
        if self.manager_obj is not None:
            minimap = self.manager_obj.generate_minimap()  # Generates the minimap
            inner_h = len(minimap)
            inner_w = 0
            for row in minimap:
                row_width = sum(len(str(col)) for col in row)
                if row_width > inner_w:
                    inner_w = row_width

            inner_h = max(0, inner_h)
            inner_w = max(1, inner_w)

            win_h = inner_h + 2
            win_w = inner_w + 2

            max_h, max_w = self.stdscr.getmaxyx()
            if win_h > max_h:
                win_h = max_h
                inner_h = max(0, win_h - 2)
            if win_w > max_w:
                win_w = max_w
                inner_w = max(1, win_w - 2)

            side_y = 0
            side_x = max(0, max_w - win_w)

            try:
                self.minimap_win = curses.newwin(
                    win_h, win_w, side_y, side_x
                )  # Creates the minimap window
                self.minimap_win.box()  # Draws a box around the minimap
            except curses.error:
                return

            for iy in range(1, win_h - 1):
                try:
                    self.minimap_win.move(iy, 1)
                    self.minimap_win.clrtoeol()
                except curses.error:
                    pass

            for y, row in enumerate(minimap):
                if y >= inner_h:
                    break
                cur_x = 1
                for col in row:
                    cell_str = str(col)
                    remaining = inner_w - (
                        cur_x - 1
                    )  # How many characters left in the row of the minimap
                    if remaining <= 0:  # Preventing a curses error
                        break
                    if len(cell_str) > remaining:
                        cell_str = cell_str[:remaining]
                    try:
                        self.minimap_win.addstr(
                            1 + y, cur_x, cell_str
                        )  # If there is available space then add the minimap char into the window
                    except curses.error:
                        pass
                    cur_x += len(cell_str)

            try:
                self.minimap_win.box()
                self.minimap_win.refresh()
            except curses.error:
                pass

    def update_map(self, new_map):
        """Update the map."""
        self.map = new_map
        self.draw()
