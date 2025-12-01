"""Entity manager."""

# -- Imports --

import random

import torch

from generators_package.entity_generator import Agent, DudEntity, Entity, Player
from nn_package import MovementNet


class EntityManager:
    """Entity manager.

    ## Description
    Entity manager is the parent class controlling the each entity present in a gamestate
    ## Attributes
    ```
    self.model: MovementNet # Nueral network that governs the AI movement
    self.enemy_count: int # The number of enemies in the current gamestate
    self.player: Player # Player object
    self.Agents: list[Agent] # List of enemy objects (length = self.enemy_count)
    ```
    ## Methods
    ```
    get_pos(Entity: Entity) -> tuple[int, int] # Returns the position of a given entity
    set_position(entity: Entity, x: int, y: int, map: list[list[str]]) -> None # Sets the position of an entity and updates the map with its character.
    randomise_positions(map: list[list[str]]) -> None # Randomly places agents on the map in empty spaces
    get_all_entity_chars() -> list[str] # Returns a list of the all of the entity placeholder characters
    get_all_agent_chars() -> list[str] # Returns a list of only the agent characters
    get_entity_at_pos(self, coordiantes, ignore=None) -> Agent | dud_entity | Player # Returns the entity at a provided position, ignore parameter allows for a certain type to be removed from the search
    ```
    """

    def __init__(self, player: Player, enemy_count: int, enemy_level: int = 1) -> None:
        """Initialise entity manager."""
        self.model = MovementNet()  # Gets the neural network
        self.model.load_state_dict(
            torch.load("nn_package/enemy_controller.pth")
        )  # Loads a nueral network
        self.model.eval()
        self.enemy_count = enemy_count  # Enemy count
        self.player: Player = player  # Player object
        self.Agents: list[Agent] = [
            Agent(
                level=enemy_level,
                # health=random.randint(1, 150),
                health=100,
                char=" " + str(i) + " ",
            )
            for i in range(self.enemy_count)
        ]  # List of all the agents

    def get_pos(self, entity: Entity) -> tuple[int, int]:
        """Return the position of a given entity."""
        return entity.pos

    def randomise_positions(self, map, player_position) -> None:
        """Randomly place agents on the map in empty spaces."""
        agent_chars = [agent.char for agent in self.Agents]
        for agent in self.Agents:
            while True:
                y, x = random.randint(1, len(map) - 2), random.randint(1, len(map) - 2)
                if (
                    map[y][x] not in [" / ", " # "]
                    and (y, x) != player_position
                    and map[y][x] not in agent_chars
                ):
                    agent.pos = (y, x)
                    break

    def get_all_entity_chars(self) -> list[str]:
        """Return a list of the all of the entity placeholder characters."""
        return (
            [agent.char for agent in self.Agents]
            + self.get_all_agent_chars()
            + [self.player.char]
        )

    def get_all_agent_chars(self) -> list[str]:
        """Return a list of only the agent characters."""
        return [" " + char + " " for char in "⇖⇗⇘⇙⇚⇛⇑⇓"]

    def get_entity_at_pos(self, coordiantes, ignore=None) -> Agent | DudEntity | Player:
        """Return the entity at a provided position, ignore parameter allows for a certain type to be removed from the search."""
        all_entities = self.Agents + [self.player]
        if ignore == "player":
            all_entities.remove(self.player)
        elif ignore == "agent":
            for agent in self.Agents:
                all_entities.remove(agent)
        for entity in all_entities:
            if self.get_pos(entity) == coordiantes:
                return entity
        return DudEntity()
