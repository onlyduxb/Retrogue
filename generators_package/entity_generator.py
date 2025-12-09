"""Entity generation."""

# -- Imports --

from generators_package.item_generator import Item, Weapon

import math
import time


class Entity:
    """Entity.

    ## Description
    Base entity class.
    ## Attributes
    ```
    self.char: str
    self.max_health: int
    self.health: float
    self.level: int
    self.pos: tuple[int, int]
    self.vision_angle: int
    self.vision_radius: int
    self.direction: tuple[int, int]
    self.vision: dict[tuple, str]
    self.last_move_time: float
    self.movement_delay: float
    self.is_making_noise: bool
    self.is_hit: bool
    self.hit_timer
    ```
    ## Methods
    ```
    angle_diff(self, a: float, b: float) -> float # Return the magnitude of the difference between two angles.
    get_visible(self, map_size: int) -> set[tuple[int, int]] # Return a set of tuples with coordinates within the convex vector that is the entity's FOV.
    deal_damage(self, damage_points: float) -> None # Apply a damage, damage_points.
    get_max_health(self) -> int # Return the maxium health of the entity.
    ```
    """

    def __init__(
        self, char, health=100, max_health=100, level=0, vision_radius=4, vision_angle=120
    ) -> None:
        """Initialise entity."""
        self.char: str = char
        self.max_health: int = max_health
        self.health: float = health
        self.level: int = level
        self.pos: tuple[int, int] = (0, 0)
        self.vision_angle: int = vision_angle
        self.vision_radius: int = vision_radius
        self.direction: tuple[int, int] = (0, 1)
        self.vision: dict[tuple, str] = {}
        self.last_move_time = time.time()
        self.movement_delay = 0.1
        self.is_making_noise = False
        self.is_hit = False
        self.hit_timer = None

    def angle_diff(self, a: float, b: float) -> float:
        """Return the magnitude of the difference between two angles."""
        return abs((a - b + math.pi) % (2 * math.pi) - math.pi)

    def get_visible(self, map_size: int) -> set[tuple[int, int]]:
        """Return a set of tuples with coordinates within the convex vector that is the entity's FOV."""
        fov_angle = math.radians(self.vision_angle)
        visible = set()
        ox, oy = self.pos
        dir_angle = math.atan2(self.direction[1], self.direction[0]) % (2 * math.pi)
        for dx in range(-self.vision_radius, self.vision_radius + 1):
            for dy in range(-self.vision_radius, self.vision_radius + 1):
                x, y = ox + dx, oy + dy
                if 0 <= x < map_size and 0 <= y < map_size:
                    dist = math.hypot(dx, dy)
                    if 0 < dist <= self.vision_radius:
                        angle = math.atan2(dy, dx) % (2 * math.pi)
                        if self.angle_diff(dir_angle, angle) <= fov_angle / 2:
                            visible.add((x, y))
        return visible

    def deal_damage(self, damage_points: float) -> None:
        """Apply a damage, damage_points."""
        self.health -= damage_points

    def get_max_health(self) -> int:
        """Return the maxium health of the entity."""
        return self.max_health


class Player(Entity):
    """Player.

    ## Description
    Player entity.
    ## Attributes
    ```
    self.char: str
    self.max_health: int
    self.health: float
    self.level: int
    self.pos: tuple[int, int]
    self.vision_angle: int
    self.vision_radius: int
    self.direction: tuple[int, int]
    self.vision: dict[tuple, str]
    self.last_move_time: float
    self.movement_delay: float
    self.is_making_noise: bool
    self.is_hit: bool
    self.hit_timer
    ```
    ## Methods
    ```
    angle_diff(self, a: float, b: float) -> float # Return the magnitude of the difference between two angles.
    get_visible(self, map_size: int) -> set[tuple[int, int]] # Return a set of tuples with coordinates within the convex vector that is the entity's FOV.
    deal_damage(self, damage_points: float) -> None # Apply a damage, damage_points.
    get_max_health(self) -> int # Return the maxium health of the entity.
    """

    def __init__(
        self, debugger, weapon: Weapon, inventory: list[Item], level: int = 0, health: int = 100, base_strength=1, permadeath: bool=False, keep_inventory: bool=True
    ) -> None:
        """Initialise the player."""
        super().__init__(char=" P ", level=level, health=health)
        self.debugger=debugger
        self.movement_delay = 0
        self.inventory_size = 6
        self.step_timer = None
        self.base_strength: float=base_strength
        self.weapon=weapon
        self.inventory = inventory
        self.permadeath=permadeath
        self.keep_inventory=keep_inventory

    def get_damage(self) -> float:
        """Return the damage the player will inflict."""
        return self.weapon.get_damage() * self.base_strength

    def get_char(self) -> str:
        """Return the player char."""
        return self.char

    def get_save_data(self):
        """Return the save data."""
        return {"health": self.health, "level": self.level, "weapon": self.weapon.to_dict(), "inventory": [item.to_dict() for item in self.inventory], "settings": {"permadeath": self.permadeath, "keep_inventory": self.keep_inventory}}
    
    def use_item(self, index: int):
        """Use item at index `index`."""
        if 0<=index<=len(self.inventory):
            effect=self.inventory[index].get_effects()
            self.debugger.write(effect)
            match effect.get('effect'):
                case 'heal':
                    self.debugger.write('healing')
                    self.health += effect.get('strength') # type: ignore
                    pass
                case 'strength':
                    self.base_strength *= effect.get('strength') # type: ignore
                    pass
                case _:
                    pass

    def pickup(self, obj: Item | Weapon):
        """Pickup an item."""
        if isinstance(obj, Item):
            for index, slot in enumerate(self.inventory):
                if slot.name == 'None':
                    self.inventory[index]=obj
                    return
        else:
            self.weapon=obj

    def death_action(self):
        """Return the action for player death."""
        return {'action': 'death', 'permadeath': self.permadeath, 'keep_inventory': self.keep_inventory}


class Agent(Entity):
    """Agent.

    ## Description
    Enemy class.
    ## Attributes
    ```
    self.char: str
    self.max_health: int
    self.health: float
    self.level: int
    self.pos: tuple[int, int]
    self.vision_angle: int
    self.vision_radius: int
    self.direction: tuple[int, int]
    self.vision: dict[tuple, str]
    self.last_move_time: float
    self.movement_delay: float
    self.is_making_noise: bool
    self.is_hit: bool
    self.hit_timer
    ```
    ## Methods
    ```
    angle_diff(self, a: float, b: float) -> float # Return the magnitude of the difference between two angles.
    get_visible(self, map_size: int) -> set[tuple[int, int]] # Return a set of tuples with coordinates within the convex vector that is the entity's FOV.
    deal_damage(self, damage_points: float) -> None # Apply a damage, damage_points.
    get_max_health(self) -> int # Return the maxium health of the entity.
    get_char(self) -> str # Return the entity char
    """

    def __init__(self, level: int = 0, health=100, char: str = " E ") -> None:
        """Initialise the enemy."""
        super().__init__(char=char, level=level, health=health)
        self.movement_delay = 0.85

    def get_char(self) -> str:
        """Return the enemy character."""
        match self.direction:
            case (-1, -1):
                return " ⇖ "
            case (-1, 1):
                return " ⇗ "
            case (0, -1):
                return " ⇚ "
            case (0, 1):
                return " ⇛ "
            case (1, -1):
                return " ⇙ "
            case (1, 0):
                return " ⇓ "
            case (1, 1):
                return " ⇘ "
            case _:
                return " ⇑ "


class DudEntity(Entity):
    """Dud entity.

    ## Description
    Dud entity is a placeholder in entity maps.
    ## Attributes
    ```
    self.char: str
    self.max_health: int
    self.health: float
    self.level: int
    self.pos: tuple[int, int]
    self.vision_angle: int
    self.vision_radius: int
    self.direction: tuple[int, int]
    self.vision: dict[tuple, str]
    self.last_move_time: float
    self.movement_delay: float
    self.is_making_noise: bool
    self.is_hit: bool
    self.hit_timer
    ```
    ## Methods
    ```
    angle_diff(self, a: float, b: float) -> float # Return the magnitude of the difference between two angles.
    get_visible(self, map_size: int) -> set[tuple[int, int]] # Return a set of tuples with coordinates within the convex vector that is the entity's FOV.
    deal_damage(self, damage_points: float) -> None # Apply a damage, damage_points.
    get_max_health(self) -> int # Return the maxium health of the entity.
    """

    def __init__(
        self, char="", health=10000000, level=0, vision_radius=0, vision_angle=0
    ) -> None:
        """Initialise dud entity."""
        super().__init__(char, health, level, vision_radius, vision_angle)
        self.is_hit = False
