"""Dungeon Scene."""

#  -- Imports --

import curses
import time

from managers_package import DungeonManager
from managers_package.chest_manager import Chest

from .scene import Scene

last_draw=0


class DungeonScene(Scene):
    """A Dungeon Scene.

    ## Description
    Dungeon scene, child class of scene.
    ## Attributes
    ```
    self.stdscr: curses.win # Screen
    self.manager_obj # Manager object
    self.stat_win: curses.win # Stats window
    ```
    ## Methods
    ```
    extract_obj(self, obj: DungeonManager) # Extract the manager object.
    on_enter(self) # Run when entering a scene.
    draw(self) # Draw the current scene.
    draw_side_win(self) # Draw the side window.
    damage_colour(self, coordinates: tuple[int, int]) # Set the colour of a tile to red.
    on_exit(self) # Run when exiting a scene.
    ```
    """

    def __init__(self, stdscr):
        """Initialise dungeon scene."""
        super().__init__(stdscr)
        self.stat_win = None  # Stats window
        self.bottom_text: str = ""

    def extract_obj(self, obj: DungeonManager):
        """Extract the manager object."""
        self.manager_obj = obj

    def on_enter(self):
        """Run when entering a scene."""
        h, w = self.stdscr.getmaxyx()
        self.stat_win = curses.newwin(1, 1, 0, w - 1)
        self.stdscr.nodelay(True)  # Makes curses 'non-blocking'

    def draw(self):
        """Draw the current scene."""
        global last_draw
        now = time.time()
        if now - last_draw < 1/30:   # 30 FPS cap
            return
        last_draw = now
        self.stdscr.clear()  # clears screen
        room_map = self.manager_obj.current_room.map  # current map
        entity_map = self.manager_obj.current_room.entity_map  # entity map
        colour = curses.color_pair(3)
        for y, row in enumerate(room_map):  # Applies colouring
            x_pos = 0
            for tile in row:
                coloured = False
                if not isinstance(entity_map[y][int(x_pos / len(tile))], Chest):  # type: ignore
                    if entity_map[y][int(x_pos / len(tile))].is_hit:  # type: ignore
                        colour = curses.color_pair(6)
                        coloured = True
                if tile == " _ ":
                    colour = curses.color_pair(2)
                    coloured = True
                if tile == " P ":
                    if self.manager_obj.player.is_hit:
                        colour = curses.color_pair(6)
                        coloured = True
                    else:
                        colour = curses.color_pair(4)
                        coloured = True
                    if not self.manager_obj.player.is_making_noise: # When the player is not making noise make the character dimmer
                        colour |= curses.A_DIM
                if tile == " # ":
                    colour = curses.color_pair(1)
                    coloured = True
                if tile == " / ":
                    colour = curses.color_pair(5)
                    coloured = True
                if not coloured:
                    colour = curses.color_pair(3)

                try:
                    self.stdscr.addstr(y, x_pos, str(tile), colour)
                except curses.error:
                    pass
                x_pos += len(tile)  # type: ignore

        self.add_text_bottom()  # Adds text to bottom
        self.draw_side_win()  # Draws side screen
        self.stdscr.noutrefresh()  # Queue screen refresh
        curses.doupdate()

    def draw_side_win(self):
        """Draw the side window."""
        assert self.stat_win is not None
        player = self.manager_obj.player  # gets player object
        weapon = self.manager_obj.player.weapon
        inventory_names = [item.name for item in player.inventory]

        # Auto-scale side window
        lines = [
            f"Health: {player.health} / {player.max_health}",
            f"{weapon.name}",
            f". Weapon Damage: {weapon.damage * weapon.get_rarity_boost() *  player.base_strength}",
            f". Crit chance: {weapon.crit_chance}",
            f". Crit damage {int(weapon.damage * weapon.get_rarity_boost() * weapon.crit_mult * player.base_strength)}",
            f". Rarity: {weapon.rarity}",
            f". Durability: {weapon.durability} / {weapon.max_durability}",
            f". Inventory: {inventory_names}",
        ]

        max_width = max(len(line) for line in lines) + 2
        height = len(lines) + 2

        h, w = self.stdscr.getmaxyx()
        self.stat_win.resize(height, max_width)
        self.stat_win.mvwin(0, w - max_width)

        if self.stat_win:  # Display player stats and held weapon stats
            self.stat_win.clear()
            self.stat_win.box()
            for idx, line in enumerate(lines, start=1):
                self.stat_win.addstr(idx, 1, line)
            self.stat_win.noutrefresh()

    def damage_colour(self, coordinates: tuple[int, int]):
        """Set the colour of a tile to red."""
        tile = self.manager_obj.current_room.map[coordinates[0]][coordinates[1]]
        self.stdscr.addstr(
            coordinates[0], coordinates[1] * 3, tile, curses.color_pair(6)
        )

    def on_exit(self):
        """Run when exiting a scene."""
        self.stdscr.nodelay(False)  # Reblock curses
