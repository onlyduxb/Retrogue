"""Weapon factory."""

# -- Imports --

import random
from typing import Callable, Dict, Generic, TypeVar

from generators_package.item_generator import Item, Weapon

factory_type = TypeVar("factory_type")


class Factory(Generic[factory_type]):
    """Factory base class.

    ## Description
    ## Attributes
    ## Methods
    """

    _data: Dict[str, dict] = {}
    _builders: Dict[str, Callable[..., factory_type]] = {}

    @classmethod
    def initilise_registry(cls):
        """Initilise registry."""
        pass

    @classmethod
    def register(cls, name: str, params: dict):
        """Register an item."""
        cls._data[name] = params
        cls._builders[name] = lambda p=params: cls._build(p)

    @classmethod
    def get_registry(cls):
        """Return the registry."""
        return cls._data

    @classmethod
    def create(cls, name: str, **kwargs) -> factory_type:
        """Create some object which is returned."""
        if cls._builders.get(name, None) is None:  # Check to see if the weapon exists
            raise IndexError("Weapon is not in registry.")
        return cls._builders[name](**kwargs)

    @classmethod
    def create_random(cls) -> factory_type:
        """Return random weapon object with random attributes."""
        raise NotImplementedError

    @classmethod
    def get_registry_save_data(cls):
        """Compile registry data into a dictionary that can be saved to json."""
        return cls._data

    @classmethod
    def load_registry(cls, registry_data):
        """Load save data."""
        cls._data = registry_data
        cls._builders = {
            name: (lambda p=params: cls._build(p))
            for name, params in registry_data.items()
        }

    @classmethod
    def _build(cls, params: dict) -> factory_type:
        raise NotImplementedError


class WeaponFactory(Factory[Weapon]):
    """Weapon factory.

    ## Description
    ## Attributes
    ## Methods
    """

    _data: Dict[str, dict] = {}
    _builders: Dict[str, Callable[..., Weapon]] = {}

    @classmethod
    def initilise_registry(cls):
        """Initilise registry."""
        cls.register("fists", {"name": "fists", "damage": 10, "rarity": "Common"})
        cls.register("sword", {"name": "sword", "damage": 20, "rarity": "Common"})
        cls.register("dagger", {"name": "dagger", "damage": 15, "rarity": "Common"})
        cls.register("mace", {"name": "mace", "damage": 25, "rarity": "Common"})
        cls.register("hammer", {"name": "hammer", "damage": 15, "rarity": "Common"})

    @classmethod
    def _build(cls, params: dict) -> Weapon:
        return Weapon(**params)

    @classmethod
    def create_random(cls):
        """Return random weapon object with random attributes."""
        weapon_list = list(cls._data.keys())
        weapon_list.remove("fists")
        weapon_name = random.choice(weapon_list)
        probabilities = [0.5, 0.35, 0.1, 0.05]
        rarities = ["Common", "Rare", "Epic", "Legendary"]
        rarity = random.choices(rarities, weights=probabilities, k=1)[0]
        params = dict(cls._data[weapon_name])
        params["rarity"] = rarity
        return cls._build(params)


class ItemFactory(Factory[Item]):
    """Item factory.

    ## Description
    ## Attributes
    ## Methods
    """

    _data: Dict[str, dict] = {}
    _builders: Dict[str, Callable[..., Item]] = {}

    @classmethod
    def initilise_registry(cls):
        """Initilise registry."""
        cls.register("None", {"name": "None", "effect_name": None, "strength": 0})
        cls.register(
            "health potion",
            {"name": "health potion", "effect_name": "heal", "strength": 25},
        )
        cls.register(
            "strength potion",
            {"name": "strength potion", "effect_name": "strength", "strength": 1.25},
        )

    @classmethod
    def _build(cls, params: dict) -> Item:
        return Item(**params)
    
    @classmethod
    def create(cls, name: str, **overrides):
        """Create a weapon with the ability to override parameters."""
        if cls._data.get(name) is None:
            raise IndexError("Weapon is not in registry.")
        params = cls._data[name].copy()
        params.update(overrides)  # merge rarity or anything else

        return cls._build(params)
    
    @classmethod
    def create_random(cls):
        """Return a random item."""
        item_list = list(cls._data.keys())
        item_name = random.choice(item_list)
        params = dict(cls._data[item_name])
        return cls._build(params)