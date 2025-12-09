"""Room manager."""

# -- Imports --

import math
import random
import threading
import time
from collections import deque

import torch

from generators_package.entity_generator import Agent, DudEntity, Entity, Player
from generators_package.room_generator import RoomGenerator
from managers_package.chest_manager import Chest
from managers_package.entity_manager import EntityManager
from nn_package import encode_inputs


class RoomManager:
    """Room manager.

    ### Attributes
    ```
    self.debugger: Debug_manager # Debugger
    self.Dungeon_manager: Dungeon_manager # Parent dungeon
    self.empty_char: str
    self.wall_char: str
    self.door_char: str
    self.coordinates: tuple[int, int] # For hashing in room generation
    self.map_size: int # nxn size of the map
    self.map: list[list[str]] # Initilised map structure
    self.heat_map: list[list[float]] # Initilised sound intentisty map
    self.enemy_count: int # Number of enemies present
    self.entity_manager: Entity_manager # Entity manager
    self.activated: bool # Stops room from being re-generated if a player re-enters
    self.level: int # Depth of the room in tree
    self.max_level: int # Maximum depth in tree
    self.SOUND_DECAY_CONSTANT: float # Multiplier to stop decay the sound over a distance
    self.FOOTSTEP_DURATION: float  # Time that a footstep lasts for
    self.HIT_COLOUR_DURATION: float # Time that an entity turns red after being attacked
    self.entity_map: list[list[entity]] # Stores all of the entity objects in their positions on the map
    self.door_count: int # Number of doors
    self.up: None | Exit | RoomManager # Room above
    self.down: None | Exit | RoomManager # Room below
    self.left: None | Exit | RoomManager # Room left
    self.right: None | Exit | RoomManager # Room right
    ```
    ### Methods
    ```
    # --- Misc ---
    activate_room(self, player_pos: tuple[int, int] | None = None) #  Starts the room
    door_pos(self, original_pos: tuple[int, int] | None) -> list[tuple[int, int]] # Gets the position of the door on the opposing side for where a player came through
    reset_episode(self, player_pos=None, set_player: bool = True) -> None # Regenerates map when not self.activated and selects new random positions
    add_next_room(self, vector: tuple[int, int], player_pos) # Creates the next room for where the player entered

    # -- Sound Generation and processing ---
    generate_heat_map(self) -> None # Generates sound heat map
    zero_heat_map(self) -> None # Sets the heat_map to be all 0s, this is for after a player takes a step
    get_sound_window(self, Entity: Entity) -> list[float] # Returns a 3x3 grid (including center) around entity position of sound strengths

    # --- FOV ---
    generate_fov_map(self, entity: Agent) -> None # Places ' x ' wherever the provided entity can see
    get_viewport(self, entity: Agent) -> list[str] # Sets entity.vision to a dictionary (pos: char) that the entity can 'see'
    bresenham(self, x1: int, y1: int, x2: int, y2: int, entity: Agent) # Uses bresenham's line algorithm to draw convex vector between the edges of the fov

    # --- Entity Movements ---
    start_hit_timer(self, entity: Player | Agent) # Begins a timer for an entity thats been damaged with time `self.HIT_COLOUR_DURATION` to colour the attacked entity red
    kill_footsteps(self) # Zeros the heatmap to kill sound
    start_footstep_timer(self, player: Player) #  Starts a timer that will zero the heat_map after FOOTSTEP_DURATION seconds. If the timer is already running, it will be reset.
    move_entity(self, entity: Agent | player, vector: tuple[int, int], force_move: bool = False) # Accepts either Agent or player class to move said entity in a given vector direction.
    get_agent_movement(self) # Gets the movement from the AI model for each agent.
    update_entity_map(self) # Refreshes the positions of the entities on the entity map
    move_agents(self) # Moves all of the agents then update the entity map
    ```
    """

    def __init__(
        self,
        player: Player,
        dungeon_manager,
        debugger,
        weapon_factory,
        item_factory,
        level: int,
        max_level: int,
        doors: int,
        coordinates: tuple[int, int] = (
            random.randint(1000, 9999),
            random.randint(1000, 9999),
        ),
        enemy_count=1,
        map_size=11,
    ) -> None:
        """Initilise room object."""
        self.debugger = debugger  # Debugger
        self.weapon_factory = weapon_factory
        self.item_factory = item_factory
        self.dungeon_manager = dungeon_manager  # Parent dungeon
        self.empty_char = " _ "
        self.wall_char = " # "
        self.door_char = " / "
        self.chest_char = ' C '
        self.coordinates: tuple[int, int] = (
            coordinates  # For hashing in room generation
        )
        self.map_size = map_size  # nxn size of the map
        self.map = []  # Initilised map structure
        self.heat_map = []  # Initilised sound intentisty map
        self.enemy_count: int = enemy_count  # Number of enemies present
        self.entity_manager: EntityManager = EntityManager(
            player=player, enemy_count=enemy_count, enemy_level=random.randint(0, 100)
        )  # Entity manager
        self.activated = (
            False  # Stops room from being re-generated if a player re-enters
        )
        self.level = level  # Depth of the room in tree
        self.max_level = max_level  # Maximum depth in tree
        self.SOUND_DECAY_CONSTANT: float = (
            0.65  # Multiplier to stop decay the sound over a distance
        )
        self.FOOTSTEP_DURATION: float = 1.5  # Time that a footstep lasts for
        self.HIT_COLOUR_DURATION: float = (
            1  # Time that an entity turns red after being attacked
        )
        self.dud_entity=DudEntity()
        self.entity_map = [
            [self.dud_entity for i in range(11)] for i in range(11)
        ]  # Stores all of the entity objects in their positions on the map
        if 1 <= doors <= 4:  # Prevents too many or too little doors from being created
            self.door_count = doors
        else:
            raise ValueError("doors must be in the range 1 to 4 inclusive")
        self.up: None | Exit | RoomManager = None  # Room above
        self.down: None | Exit | RoomManager = None  # Room below
        self.left: None | Exit | RoomManager = None  # Room left
        self.right: None | Exit | RoomManager = None  # Room right
        self.debugger.write("Sucessfully created room")  # Debug

    # --- Misc ---

    def activate_room(self, player_pos: tuple[int, int] | None = None):
        """Start the room."""
        self.reset_episode(player_pos)
        self.zero_heat_map()
        self.update_entity_map()
        return {"action": "room_ready"}

    def door_pos(self, original_pos: tuple[int, int] | None) -> list[tuple[int, int]]:
        """Get the position of the door on the opposing side for where a player came through."""
        if original_pos == None:  # Default just returns the bottom middle
            return [
                (self.map_size - 1, (self.map_size - 1) // 2),
                ((self.map_size - 2, (self.map_size - 1) // 2)),
            ]
        if original_pos[0] == 0:  # Top
            return [
                (self.map_size - 1, original_pos[1]),
                (self.map_size - 2, original_pos[1]),
            ]
        if original_pos[0] == self.map_size - 1:  # Bottom
            return [(0, original_pos[1]), (1, original_pos[1])]
        if original_pos[1] == self.map_size - 1:  # Left
            return [(original_pos[0], 0), (original_pos[0], 1)]
        if original_pos[1] == 0:  # Right
            return [
                (original_pos[0], self.map_size - 1),
                (original_pos[0], self.map_size - 2),
            ]
        return [
            (self.map_size - 1, self.map_size - 1 // 2),
            ((self.map_size - 2, self.map_size - 1 // 2)),
        ]

    def reset_episode(self, player_pos=None, set_player: bool = True) -> None:
        """Set/reset the room."""
        door_pos, player_start = self.door_pos(
            player_pos
        )  # Gets the door and player position for entering a room
        if (
            self.activated == False
        ):  # If the room has not been previously initilised, initilise the map and enemy positions
            self.map = RoomGenerator(
                doors=self.door_count, start_door=door_pos
            ).generate_dungeon()
            self.entity_manager.randomise_positions(self.map, player_start)
            self.activated = True
            if self.door_count == 1:
                self.entity_map[self.map_size // 2][self.map_size // 2] = Chest(debugger=self.debugger, weapon_factory=self.weapon_factory, item_factory=self.item_factory)  # type: ignore
                self.map[self.map_size // 2][self.map_size // 2] = self.chest_char
        if (
            set_player
        ):  # If set player then place the player with a pre-defined position
            self.entity_manager.player.pos = player_start
            self.map[player_start[0]][player_start[1]] = self.entity_manager.player.char
        else:  # Randomly place the player
            while True:
                y, x = random.randint(1, len(self.map) - 2), random.randint(
                    1, len(self.map) - 2
                )
                if self.map[y][x] not in [self.door_char, self.wall_char]:
                    self.map[y][x] = self.entity_manager.player.char
                    self.entity_manager.player.pos = (y, x)
                    break
        for entity in self.entity_manager.Agents:
            pos = entity.pos
            self.map[pos[0]][pos[1]] = entity.char
        self.generate_heat_map()  # Generates the sound intensity map

    def add_next_room(self, vector: tuple[int, int], player_pos):
        """Create the next room for where the player entered."""
        door_num = random.randint(2, 4)  # Random door number
        enemy_count = random.randint(0, 4)  # Random enemy count
        if (
            self.level >= self.max_level
        ):  # If the new room is on the max level then set the room to be empty
            door_num = 1
            enemy_count = 0
        room = RoomManager(
            player=self.entity_manager.player,
            dungeon_manager=self.dungeon_manager,
            debugger=self.debugger,
            weapon_factory=self.weapon_factory,
            item_factory=self.item_factory,
            doors=door_num,
            level=self.level + 1,
            max_level=self.max_level,
            coordinates=(random.randint(1000, 9999), random.randint(1000, 9999)),
            enemy_count=enemy_count,
        )  # Create the room manager
        direction = None  # Initlise direction that is returned the new room objected returned to the director
        match str(
            vector
        ):  # Sets the corresponding room direction to the new room and the opposing direction of the new room to the current room
            case "(-1, 0)":
                if self.up == None:
                    self.up = room
                    self.up.down = self
                direction = self.up
            case "(1, 0)":
                if self.down == None:
                    self.down = room
                    self.down.up = self
                direction = self.down
            case "(0, 1)":
                if self.right == None:
                    self.right = room
                    self.right.left = self
                direction = self.right
            case "(0, -1)":
                if self.left == None:
                    self.left = room
                    self.left.right = self
                direction = self.left
            case _:
                direction = Exit()  # Catch case will return the player to the overworld
        return {
            "action": "room_transition",
            "obj": direction,
            "player_pos": self.entity_manager.player.pos,
        }  # Returns the new room and player position to the director

    # -- Sound Generation and processing ---

    def generate_heat_map(self) -> None:
        """Generate sound heat map."""
        grid_height = len(self.map) - 1
        grid_width = len(self.map[0]) - 1
        heat_map = [
            [0.0 for _ in range(grid_width)] for _ in range(grid_height)
        ]  # Initilises the heat map

        for y in range(grid_height):
            for x in range(grid_width):
                if self.map[y][x] == (self.wall_char or self.door_char):
                    heat_map[y][x] = -1.0
        visited = {}

        def in_bounds(
            y, x
        ) -> (
            bool
        ):  # Checks whether a point (y, x) is within the bounds of the map to prevent an index error
            return 0 <= y < grid_height and 0 <= x < grid_width

        def is_wall(y, x) -> bool:  # Checks if this point (y, x) is a wall
            return self.map[y][x] == self.wall_char

        py, px = self.entity_manager.player.pos
        queue = deque([(py, px, 1.0)])

        while (
            queue
        ):  # Goes through the entirety of the heat map and assiging sound intentsity values to each point
            y, x, strength = queue.popleft()
            if strength < 0.05 or ((y, x) in visited and strength <= visited[(y, x)]):
                continue
            visited[(y, x)] = strength
            heat_map[y][x] = max(heat_map[y][x], strength)

            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                if not in_bounds(ny, nx) or is_wall(ny, nx):
                    continue
                new_strength = strength * self.SOUND_DECAY_CONSTANT
                if (ny, nx) not in visited or new_strength > visited[(ny, nx)]:
                    queue.append((ny, nx, new_strength))

        self.heat_map = heat_map

    def zero_heat_map(self) -> None:
        """Set the heat_map to be all 0s, this is for after a player takes a step, the sound only lasts for (self.FOOTSTEP_DURATION)s."""
        empty_heat_map = [
            [0.0 for _ in range(len(self.map))] for _ in range(len(self.map))
        ]
        for col in range(len(self.map)):
            for ele in range(len(self.map)):
                if self.map[col][ele] == (self.wall_char or self.door_char):
                    empty_heat_map[col][
                        ele
                    ] = -1.0  # Sets any places in the wall to have an intensity of -1
        self.heat_map = empty_heat_map

    def get_sound_window(self, entity: Entity) -> list[float]:
        """Get the sound window.

        Returns a 3x3 grid (including center) around entity position of sound strengths,
        in this order:
        ```
            A B C
            D E F
            G H I
        ```
        """
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        neighbors = []
        for dy, dx in directions:  # Checks a 3x3 zone around the player
            ny, nx = entity.pos[0] + dy, entity.pos[1] + dx
            if 0 <= ny < len(self.map) - 1 and 0 <= nx < len(self.map[0]) - 1:
                neighbors.append(self.heat_map[ny][nx])
            else:
                neighbors.append(-1)
        return neighbors

    # --- FOV ---

    def generate_fov_map(self, entity: Agent) -> None:
        """Place ' x ' wherever the provided entity can see."""
        self.fov_map = [[cell for cell in row] for row in self.map]
        self.get_viewport(entity)
        for visible in entity.vision:
            self.fov_map[visible[0]][visible[1]] = " x "
        self.fov_map[self.entity_manager.player.pos[0]][
            self.entity_manager.player.pos[1]
        ] = self.entity_manager.player.char
        for agent in self.entity_manager.Agents:
            self.fov_map[agent.pos[0]][agent.pos[1]] = agent.get_char()

    def get_viewport(self, entity: Agent) -> list[str]:
        """Set entity.vision to a dictionary (pos: char) that the entity can 'see'."""
        entity.vision.clear()
        ox, oy = self.entity_manager.get_pos(entity)
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        dir_dx, dir_dy = entity.direction  # Entity direction
        dir_angle = math.atan2(dir_dy, dir_dx) % (
            2 * math.pi
        )  # Gets the angle between the players direction vector components
        vision_half_angle = (
            math.radians(entity.vision_angle) / 2
        )  # Divides the vision angle by 2
        for dx, dy in directions:
            if dx == 0 and dy == 0:
                continue
            ray_angle = math.atan2(dy, dx) % (
                2 * math.pi
            )  # Gets angle between the points
            diff = abs(
                ray_angle - dir_angle
            )  # Difference between ray and direction angle
            if diff > math.pi:
                diff = 2 * math.pi - diff
            if diff <= vision_half_angle:
                x2 = ox + dx * entity.vision_radius
                y2 = oy + dy * entity.vision_radius
                self.bresenham(ox, oy, x2, y2, entity)
        return list(entity.vision.values())

    def bresenham(self, x1: int, y1: int, x2: int, y2: int, entity: Agent):
        """Use bresenham's line algorithm to draw convex vector between the edges of the fov."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            if 0 <= x1 < len(self.map) and 0 <= y1 < len(self.map[0]):
                if self.map[x1][y1] == self.wall_char:
                    break
                if (x1, y1) not in entity.vision:
                    if self.map[x1][y1] != entity.char:
                        entity.vision[(x1, y1)] = self.map[x1][y1]  # type: ignore
            if (x1, y1) == (x2, y2):
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    # --- Entity Movements ---

    def start_hit_timer(self, entity: Player | Agent):
        """Begin a timer for an entity that's been damaged with time `self.HIT_COLOUR_DURATION` to colour the attacked entity red."""
        entity.is_hit = True
        if hasattr(entity, "hit_timer") and entity.hit_timer is not None and entity.hit_timer.is_alive():
            entity.hit_timer.cancel()  # Cancel the old timer if it exists

        def hit_falisy():
            entity.is_hit = False

        entity.hit_timer = threading.Timer(self.HIT_COLOUR_DURATION, hit_falisy) # type: ignore
        entity.hit_timer.start()

    def kill_footsteps(self):
        """Zero the heatmap to kill sound."""
        self.zero_heat_map()

    def start_footstep_timer(self, player: Player):
        """Start a timer that will zero the heat_map after FOOTSTEP_DURATION seconds. If the timer is already running, it will be reset."""
        if (
            hasattr(player, "step_timer")
            and player.step_timer is not None
            and player.step_timer.is_alive()
        ):  # Checks if the player already has a footestep timer
            player.step_timer.cancel()
            player.is_making_noise = True

        def reset_heat():
            self.zero_heat_map()
            player.is_making_noise = False

        player.step_timer = threading.Timer(  # type: ignore
            self.FOOTSTEP_DURATION, reset_heat
        )  # Starts a hit timer # type: ignore
        player.step_timer.start()  # type: ignore

    def move_entity(
        self, entity: Agent | Player, vector: tuple[int, int], force_move: bool = False
    ):
        """Accept either Agent or player class to move said entity in a given vector direction. Force_move=True requires a non-zero vector."""
        current_time = time.time()  # Gets the current time
        if type(entity) == Player:
            if not hasattr(entity, "last_move_time"):
                entity.last_move_time = 0
            if (
                not force_move
                and current_time - entity.last_move_time
                < entity.movement_delay  # If the entity is trying to move before they are allowed to return 0
            ):
                return 0
            if entity.health <=0:
                return entity.death_action()

        target_y = entity.pos[0] + vector[0]  # Target y position
        target_x = entity.pos[1] + vector[1]  # Target x position

        dissallowed_chars = self.entity_manager.get_all_entity_chars() + [
            self.wall_char,
            self.door_char,
            self.chest_char
        ]  # All characters the current entity is not allowed to move to
        if not isinstance(entity, Player):
            dissallowed_chars.append(
                self.entity_manager.player.char
            )  # If the entity is not a player then dont allow the entities to enter the same time as the player

        if 0 <= target_y < len(self.map) and 0 <= target_x < len(
            self.map[0]
        ):  # Checks if the target position is within the bounds of the map
            if (
                self.map[target_y][target_x] not in dissallowed_chars
            ):  # Checks if the entity is attempting to move to an occupied position
                self.map[entity.pos[0]][
                    entity.pos[1]
                ] = self.empty_char  # Sets the old poisition to an empty character
                entity.pos = (target_y, target_x)  # Changes the entity position
                self.map[target_y][
                    target_x
                ] = entity.get_char()  # Sets the new position to the entity character
                entity.last_move_time = current_time  # Gets the current time
                if isinstance(entity, Player):
                    self.start_footstep_timer(
                        entity
                    )  # If the entity is a player then start a footstep timer
            elif (
                self.map[target_y][target_x]
                in self.entity_manager.get_all_entity_chars()
            ):  # If an entity is attmempting to move into an occupied position to attacck
                ignore = (
                    "player" if isinstance(entity, Player) else "agent"
                )  # Prevents the entity from trying to attack itself or others of the same type
                attacked_entity: Agent = self.entity_manager.get_entity_at_pos(
                    (target_y, target_x), ignore=ignore
                )  # Gets the entity at the position # type: ignore
                if not (
                    isinstance(attacked_entity, DudEntity)
                    or isinstance(attacked_entity, Chest)
                ):  # Checks if the entity is not a 'dud' meaning a placeholder
                    damage: float=0
                    if not isinstance(attacked_entity, Player):
                        damage=self.entity_manager.player.get_damage()
                        self.entity_manager.player.weapon.durability-=1
                        if self.entity_manager.player.weapon.is_broken():
                            self.entity_manager.player.pickup(self.weapon_factory.create('fists'))
                    else:
                        damage=10
                    attacked_entity.deal_damage(damage)  # Deals damage to the attacked entity
                    self.start_hit_timer(
                        attacked_entity
                    )  # Starts a hit timer to colour the enemy red
                    self.debugger.write(
                        {
                            "action": "deal_damage",
                            "attacker": entity,
                            "damage_delt": damage, 
                            "victim": attacked_entity,
                        }  # Debug
                    )
                    return {
                        "action": "deal_damage",
                        "attacker": entity,
                        "victim": attacked_entity,
                    }  # Returns the action to dungeon manager
            elif (
                self.map[target_y][target_x] == self.door_char
            ):  # If an entity attempts to move into a door
                if isinstance(
                    entity, Player
                ):  # Disallow enemies to walk into other rooms
                    entity.pos = (target_y, target_x)
                    return {
                        "action": "room_transition",
                        "vector": vector,
                        "noise": entity.is_making_noise,
                        "player_pos": entity.pos,
                    }  # Returns the action to dungeon manager
            elif (
                self.map[target_y][target_x] == self.chest_char
            ):
                return {
                    "action": 'open_chest',
                    'chest_obj': self.entity_map[target_y][target_x]
                }
        return {
            "action": "moved",
            "vector": vector,
            "noise": entity.is_making_noise,
        }  # Action returned to dungeon manager

    def get_agent_movement(self):
        """Get the movement from the AI model for each agent."""
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        for agent in self.entity_manager.Agents:  # Gets movement for every agent
            current_time = time.time()  # Gets current time
            if not hasattr(
                agent, "last_move_time"
            ):  # Checks if the entity is attempting to move before it is allowed
                agent.last_move_time = 0
            if agent.health <= 0:  # If dead replace the entity with an X
                self.map[agent.pos[0]][agent.pos[1]] = " X "
                continue
            if (
                current_time - agent.last_move_time >= agent.movement_delay
                and agent.health > 0
            ):  # If the entity is allowed to move and not dead allow movement
                self.get_viewport(agent)  # Gets what the agent can see
                input_tensor = encode_inputs(
                    sound_grid=self.get_sound_window(agent),
                    fov_dict=agent.vision,
                    level_diff=self.entity_manager.player.level - agent.level,
                    agent_health=agent.health,
                    allied_agent_count=self.enemy_count,
                )  # Encodes all the information of the room
                output = self.entity_manager.model(input_tensor)  # Output of NN
                vector_key = int(
                    torch.argmax(output, dim=1).item()
                )  # Gets the vector ket from the output of the NN
                vector = directions[vector_key]  # Movement vector
                agent.direction = (
                    vector  # Sets the direction to the direction of the vector
                )

                self.move_entity(
                    agent, vector, force_move=False
                )  # Moves the entity to target position
                agent.last_move_time = current_time  # Sets time to movement time

    def update_entity_map(self):
        """Refresh the positions of the entities on the entity map."""
        for row in range(len(self.entity_map) - 1):
            for col in range(len(self.entity_map[0]) - 1):
                existing = self.entity_map[row][col]
                new = self.entity_manager.get_entity_at_pos((row, col)) # Gets the entity at the current position

                if not isinstance(existing, Chest):
                    self.entity_map[row][col] = new # type: ignore

    def move_agents(self):
        """Move all of the agents then update the entity map."""
        self.entity_moved=False
        self.get_agent_movement()
        self.update_entity_map()


class Exit:
    """Exit class used for exit doors to return the player back to overworld when exiting the dungeon."""

    def activate_room(self):
        """Send exit action to the director."""
        return {"action": "exit"}
