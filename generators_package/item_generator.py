"""Weapons manager."""

# -- Imports --

import random


class Weapon:
    """Weapons.

    ## Description
    Base class for weapons.
    ## Attributes
    ```
    self.name: str # Weapon name
    self.damage: int # Weapon damage
    self.crit_chance # Probability to do a critical hit
    self.crit_mult # Crit multiplier
    self.rarity: str # Weapon rarity
    ```
    ## Methods
    ```
    get_damage(self) -> float # Return the damage a weapon deals.
    get_rarity_boost(self) # Return rarity multiplier.
    to_dict(self) # Return a dictionary of the weapon information.
    ```
    """

    def __init__(
        self,
        name: str,
        damage: int = 10,
        rarity: str = "Common",
        durability: int = 100,
        max_durability: int = 100,
    ) -> None:
        """Initilises weapon."""
        self.name: str = name  # Weapon name
        self.damage: int = damage  # Weapon damage
        self.crit_chance = 0.15  # Probability to do a critical hit
        self.crit_mult = 1.45  # Crit multiplier
        self.rarity: str = rarity  # Weapon rarity
        if durability > max_durability:
            raise ValueError('Durability can not be greater than maximum durability')
        self.durability: int = durability
        self.max_durability: int = max_durability

    def get_damage(self) -> float:
        """Return the damage a weapon deals."""
        damage_mult = [1, self.crit_mult]
        probabilities = [1 - self.crit_chance, self.crit_chance]
        multiplier = (
            random.choices(damage_mult, weights=probabilities, k=1)[0]
            * self.get_rarity_boost()
        )
        return self.damage * multiplier

    def get_rarity_boost(self):
        """Return rarity multiplier."""
        rarity_boosts = {"Common": 1, "Rare": 1.05, "Epic": 1.1, "Legendary": 1.25}
        return rarity_boosts[self.rarity]

    def to_dict(self):
        """Return a dictionary of the weapon information."""
        return {"name": self.name, "damage": self.damage, "rarity": self.rarity, "max_durability": self.max_durability, "durability": self.durability}
    
    def is_broken(self) -> bool:
        """Return true if the item's durability <= 0."""
        return True if self.durability <= 0 else False

class Item:
    """Items.

    ## Description
    Base class for items.
    ## Attributes
    ```
    self.name: str # Item name
    self.effects: dir[str, Any] # Item effect and it's strength
    ```
    ## Methods
    ```
    get_effects(self) -> dict[str, str|int|None] # Return item effects.
    to_dict(self) # Return a dictionary of the item information.
    ```
    """

    def __init__(self, name: str, effect_name: str, strength: int) -> None:
        """Initilise item."""
        self.name = name  # Item name
        self.effects = {
            "effect": effect_name,
            "strength": strength,
        }  # Item effect and it's strength

    def get_effects(self) -> dict[str, str | int | None]:
        """Return item effects."""
        return self.effects

    def to_dict(self):
        """Return a dictionary of the item information."""
        return {"name": self.name, "effects": self.effects}