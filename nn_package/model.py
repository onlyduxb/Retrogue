"""Nueral network."""

# -- Imports --

import torch
import torch.nn
import torch.nn.functional


class MovementNet(torch.nn.Module):
    """Neural Network for movement.
    
    ## Description
    Simple Nueral Network for enemy AI (agent) movement
    ## Attributes
    `self.fc1 = torch.nn.Linear(13, 64)`: Hidden Layer
    `self.fc2 = torch.nn.Linear(64, 32)`: Hidden Layer
    `self.move = torch.nn.Linear(32, 9)`: Output Layer
    """

    def __init__(self):
        """Initilise the neural netwwork's nodes."""
        super().__init__()
        self.fc1 = torch.nn.Linear(13, 64)
        self.fc2 = torch.nn.Linear(64, 32)
        self.move = torch.nn.Linear(32, 9)

    def forward(self, encoded_object):
        """Move logits forwards."""
        encoded_object = torch.nn.functional.relu(self.fc1(encoded_object))
        encoded_object = torch.nn.functional.relu(self.fc2(encoded_object))
        move_logits = self.move(encoded_object)
        return move_logits