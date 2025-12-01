"""Encoder."""

# -- Imports --

import torch


def encode_sound_grid(sound_grid: list[float]) -> torch.Tensor:
    """Encode the sound grid into a tensor for NN."""
    return torch.tensor(sound_grid, dtype=torch.float32).view(1, 9)

def encode_player_visibility(fov_dict: dict[tuple[int, int], str]) -> torch.Tensor:
    """Encode the agent's vision into a tensor for NN."""
    player_visible = 1.0 if any(char == ' P ' for char in fov_dict.values()) else 0.0
    return torch.tensor([[player_visible]], dtype=torch.float32)

def encode_level_diff(level: int) -> torch.Tensor:
    """Encode the difference in agent and player level into a tensor for NN."""
    return torch.tensor([[level]], dtype=torch.float32)

def encode_agent_health(health: float) -> torch.Tensor:
    """Encode the agent health into a tensor for NN."""
    return torch.tensor([[health]], dtype=torch.float32)

def encode_allied_agent_count(count: int) -> torch.Tensor:
    """Encode the enenmy count into a tensor for NN."""
    return torch.tensor([[count]], dtype=torch.float32)

def encode_inputs(
    sound_grid: list[float],
    fov_dict: dict[tuple[int, int], str],
    level_diff: int,
    agent_health: float,
    allied_agent_count: int,
) -> torch.Tensor:
    """Return the concatonation of all of the encoded data tensors for the NN."""
    sound_tensor = encode_sound_grid(sound_grid).view(-1)
    visibility_tensor = encode_player_visibility(fov_dict).view(-1)
    level_tensor = encode_level_diff(level_diff).view(-1)
    health_tensor = encode_agent_health(agent_health).view(-1)
    count_tensor = encode_allied_agent_count(allied_agent_count).view(-1)

    return torch.cat([
        sound_tensor,
        visibility_tensor,
        level_tensor,
        health_tensor,
        count_tensor,
    ], dim=0).unsqueeze(0)