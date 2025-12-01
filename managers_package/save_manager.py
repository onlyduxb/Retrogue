"""Save manager."""

# -- Imports --

import json


def save_game(save_name, player_data, overworld_data, weapon_registry, item_registry, debugger):
    """Save the game state and player with a given savename in src/game_data."""
    compiled_data = {
        "player_data": player_data,
        "overworld_data": overworld_data,
        'weapon_registry': weapon_registry,
        'item_registry': item_registry
    }
    with open(f"game_data/{save_name}.json", "w") as file:
        json.dump(compiled_data, file, indent=4)
    debugger.write(f'Game saved to game_data/{save_name}')
    quit()


def load_game(save_name, debugger):
    """Load a game save from src/game_data."""
    with open(f"game_data/{save_name}.json", "r") as file:
        saved_data = json.load(file)
    debugger.write('Loaded game data')
    return saved_data