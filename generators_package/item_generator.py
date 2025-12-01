"""Weapons manager."""

# -- Imports --

import random


class Weapon:
    """Weapons.

    ## Description
    Base class for weapons.
    ## Attributes
    ## Methods
    """

    def __init__(
        self,
        name: str,
        damage: int = 10,
        rarity: str='Common',
    ) -> None:
        """Initilises weapon."""
        self.name: str = name
        self.damage: int = damage
        self.crit_chance = 0.15
        self.crit_mult = 1.45
        self.rarity: str = rarity

    def get_damage(self) -> float:
        """Return the damage a weapon deals."""
        damage_mult = [1, self.crit_mult]
        probabilities = [1 - self.crit_chance, self.crit_chance]
        multiplier = random.choices(damage_mult, weights=probabilities, k=1)[0] * self.get_rarity_boost()
        return self.damage * multiplier
    
    def get_rarity_boost(self):
        """Return rarity multiplier."""
        rarity_boosts = {
            'Common': 1,
            'Rare': 1.05,
            'Epic': 1.1,
            'Legendary': 1.25
        }
        return rarity_boosts[self.rarity]
    
    def to_dict(self):
        """Return a dictionary of the weapon information."""
        return {'name': self.name, 'damage': self.damage, 'rarity': self.rarity}
    
class Item:
    """Items.

    ## Description
    ## Attributes
    ## Methods
    """
    
    def __init__(self, name, effect_name: str, strength: int) -> None:
        """Initilise item."""
        self.name=name
        self.effects={'effect': effect_name, 'strength': strength}

    def get_effects(self) -> dict[str, str|int|None]:
        """Return item effects."""
        return self.effects
    
    def to_dict(self):
        """Return a dictionary of the item information."""
        return {'name': self.name, 'effects': self.effects}