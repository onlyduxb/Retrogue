"""Chest."""

# -- Imports --

from factory_package.item_factory import WeaponFactory, ItemFactory

import random

class Chest:
    """Chest.

    ## Description
    ## Attributes
    ## Methods
    """

    def __init__(self, weapon_factory: WeaponFactory, item_factory: ItemFactory, debugger) -> None:
        """Initalise chest."""
        self.debugger=debugger
        self.initilsed = False
        self.weapon_factory=weapon_factory
        self.item_factory=item_factory
        self.loot=self.generate_loot()

    def generate_loot(self):
        """Generate loot for the chest."""
        if not self.initilsed:
            self.initilsed=True
            loot_factory_probabilies=[0.75, 0.25]
            loot_factory=[self.weapon_factory, self.item_factory]
            selected_factory=random.choices(loot_factory, weights=loot_factory_probabilies, k=1)[0]
            self.debugger.write(f'Factory chest loot {selected_factory}')
            loot = selected_factory.create_random()
            self.debugger.write(f'Generated chest loot {loot.name}')
            return loot
        
    def loot_chest(self):
        """Return weapon obj and set loot to None."""
        weapon_obj=self.loot
        self.loot=self.item_factory.create('None')
        return weapon_obj