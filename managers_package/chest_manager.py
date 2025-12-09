"""Chest."""

# -- Imports --

import random

from factory_package.item_factory import ItemFactory, WeaponFactory
from managers_package.debug_manager import Debugger
from generators_package.item_generator import Weapon, Item


class Chest:
    """Chest.

    ## Description
    Chest object generates a random item to store loot that the player can pick up.
    ## Attributes
    ```
    self.debugger: Debugger # Debugger object
    self.initilised: Bool # True when the loot has been initilised
    self.weapon_factory: WeaponFactory # Weapon factory object
    self.item_factory: ItemFactory # Item factory object
    ```
    ## Methods
    ```
    generate_loot(self) -> Weapon | Item | None # Generate loot for the chest.
    loot_chest(self) -> Weapon | Item | None # Return weapon obj and set loot to None.
    ```
    """

    def __init__(
        self,
        weapon_factory: WeaponFactory,
        item_factory: ItemFactory,
        debugger: Debugger,
    ) -> None:
        """Initalise chest."""
        self.debugger = debugger  # Debugger object
        self.initilsed = False  # True when the loot has been initilised
        self.weapon_factory = weapon_factory  # Weapon factory object
        self.item_factory = item_factory  # Item factory object
        self.loot = self.generate_loot()

    def generate_loot(self) -> Weapon | Item | None:
        """Generate loot for the chest."""
        if not self.initilsed:
            self.initilsed = True
            loot_factory_probabilies = [0.75, 0.25]
            loot_factory = [self.weapon_factory, self.item_factory]
            selected_factory = random.choices(
                loot_factory, weights=loot_factory_probabilies, k=1
            )[0]
            self.debugger.write(f"Factory chest loot {selected_factory}")
            loot = selected_factory.create_random()
            self.debugger.write(f"Generated chest loot {loot.name}")
            return loot
        else:
            return self.loot

    def loot_chest(self) -> Weapon | Item | None:
        """Return weapon obj and set loot to None."""
        item_obj = self.loot
        self.loot = self.item_factory.create("None")
        return item_obj
