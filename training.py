"""Train neural network."""

# -- Imports --

import os
import random
import time
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from colorama import Fore

from generators_package.entity_generator import Player
from managers_package.debug_manager import Debugger
from managers_package.room_manager import RoomManager
from nn_package.encoder import encode_inputs
from nn_package.model import MovementNet

from factory_package.item_factory import WeaponFactory, ItemFactory

def score(game: RoomManager) -> list[int]:
    """Algorthim that decides the best move using the provided rules based on agent health, enemy count in the current gamestate and the difference in levels between the player and agent."""
    score_value = 0
    agent = game.entity_manager.Agents[0]
    player = game.entity_manager.player

    if (
        agent.health >= 80
    ):  # When an entity has a high amount of health it will be more confident
        score_value += 50
    elif 50 <= agent.health < 80:
        score_value += 40
    else:
        score_value -= 60  # If weak then the enemy will be more scared
    if (
        game.enemy_count == 1
    ):  # If there is lots of allies for the entity it will be more confident
        score_value -= 30
    elif 2 <= game.enemy_count < 4:
        score_value += 30
    elif game.enemy_count >= 4:
        score_value += 50

    level_diff = player.level - agent.level
    if level_diff <= 5:
        score_value += 40
    else:
        score_value -= 40

    if " P " in game.get_viewport(
        agent
    ):  # If the entity can see the player and is confident it will attack more otherwise it will run away
        if score_value > 60:
            score_value += 100
        else:
            score_value -= 150

    s = game.get_sound_window(agent)  # Gets the sound window
    if score_value >= 50:  # If confident then go to the largest sound intentisty
        i = s.index(max(s))
        return [i, score_value]  #
    else:  # Otherwise go to the minimum sound intensity
        abs_s = []
        for sound in s:
            abs_s.append(abs(sound))
        i = s.index(min(abs_s))
        return [i, score_value]


# --- TESTING ---


def test_model(weapon_factory, item_factory):
    """Creates a demo environment to show what the score_value function produces compared to the model."""
    directions = [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (0, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    ]
    while True:
        game = RoomManager(
            debugger=debug,
            player=Player(debugger=debug, weapon=weapon_factory.create('fists'), inventory=[item_factory.create('None') for i in range(2)],level=random.randint(0, 10)),
            dungeon_manager=None,
            coordinates=(random.randint(0, 1000), random.randint(0, 1000)),
            enemy_count=random.randint(1, 4),
            level=0,
            max_level=5,
            doors=4,
            weapon_factory=weapon_factory,
            item_factory=item_factory
        )  # Creates a test room
        agent = game.entity_manager.Agents[0]  # Picks an agent
        agent.deal_damage(
            random.randint(0, 99)
        )  # Weakens the enemy a bit to affect its confidence
        player = game.entity_manager.player

        game.reset_episode(set_player=False)  # Sets up the game state
        game.get_viewport(agent)  # Gets what the entity can see
        input_tensor = encode_inputs(
            sound_grid=game.get_sound_window(agent),
            fov_dict=agent.vision,
            level_diff=player.level - agent.level,
            agent_health=agent.health,
            allied_agent_count=game.enemy_count,
        )  # Encodes the data to be passed into model

        output = model(input_tensor)  # Output from the model
        label, points = score(game)  # Hueristic output
        m = int(torch.argmax(output, dim=1).item())  # Model result
        move_label = directions[label]
        move_model = directions[m]
        while game.map[agent.pos[0] + move_model[1]][agent.pos[1] + move_model[0]] in [
            " # ",
            " / ",
        ]:
            output = model(input_tensor)
            label, points = score(game)
            m = int(torch.argmax(output, dim=1).item())
            move_label = directions[label]
            move_model = directions[m]
        game.map[agent.pos[0] + move_label[1]][
            agent.pos[1] + move_label[0]
        ] = " A "  # Algorithm label (ideal move)
        game.map[agent.pos[0] + move_model[1]][
            agent.pos[1] + move_model[0]
        ] = " M "  # Model label (attempts to replicated ideal move)
        for row in game.map:
            print(row)  # Shows the output of the model vs the ideal movement
        print(points, directions[m], directions[label])  # Debug info
        print(game.get_sound_window(agent))  # Debug info
        input("Another?")


# --- Training ---


def train_model(desired_accuracy, min_step, log, max_train, name, debug, weapon_factory, item_factory):
    """Trains the model using unsupervised learning by using the score function as the best move."""
    start = time.perf_counter()  # Starts a timer to see how long training takes
    correct_total = 0
    last_100_correct = 0
    last_1000 = 0
    step = 1
    while True:  # Repeatedly reset the room
        correct = False
        game = RoomManager(
            debugger=debug,
            player=Player(debugger=debug, weapon=weapon_factory.create('fists'), inventory=[item_factory.create('None') for i in range(2)],level=random.randint(0, 10)),
            dungeon_manager=None,
            coordinates=(random.randint(0, 1000), random.randint(0, 1000)),
            enemy_count=random.randint(1, 5),
            level=0,
            max_level=5,
            doors=4,
            weapon_factory=weapon_factory,
            item_factory=item_factory
        )

        agent = game.entity_manager.Agents[0]
        player = game.entity_manager.player
        agent.deal_damage(random.randint(0, 99))
        game.reset_episode(set_player=False)
        game.get_viewport(agent)

        input_tensor = encode_inputs(
            sound_grid=game.get_sound_window(agent),
            fov_dict=agent.vision,
            level_diff=player.level - agent.level,
            agent_health=agent.health,
            allied_agent_count=game.enemy_count,
        )
        label, points = score(game)
        label_tensor = torch.tensor([label], dtype=torch.long)
        output = model(input_tensor)
        loss = criterion(output, label_tensor)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        m = int(torch.argmax(output, dim=1).item())
        if m == label:  # if the model matches the algorithm
            correct_total += 1
            last_100_correct += 1
            correct = True
        if step % 1000 == 0:  # Calculates the accuracy of the last 1000 steps
            last_1000 = round((last_100_correct / 1000) * 100, 4)
            last_100_correct = 0
        if log == "y":  # If logging results (slower but helpful)
            time_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Gets the time
            status = "CORRECT" if correct else "INCORRECT"  # Label
            mode = "Aggressive" if points > 50 else "Deffensive"  # attack mode
            color_mode = (
                (Fore.YELLOW + mode) if points > 50 else (Fore.BLUE + mode)
            )  # Colours
            accuracy_color = (
                Fore.RED if last_1000 < 75 else Fore.GREEN
            )  # Goes green if accuracy is >75%
            msg = (
                f"[{time_str}] Step: [{step}] "
                f"{(Fore.GREEN if correct else Fore.RED)}Output: {status} "
                f"(Expected: {label} Got: {m}){Fore.RESET} "
                f"Mode: {color_mode} ({points}) {accuracy_color} "
                f"Accuracy: {last_1000}%{Fore.RESET} Loss: {round(float(loss), 2)}"
            )
            print(msg)
        step += 1
        if last_1000 >= desired_accuracy and step > min_step:
            os.system(
                """osascript -e 'display notification "Model trained to desired accuracy" with title "Trainer"'"""
            )
            break
    end = time.perf_counter()
    print(f"[{step}] Time taken to train to {desired_accuracy}%: {end - start:.3f}s")
    if max_train:
        torch.save(model.state_dict(), f"nn_package/{name}.pth")
        print(f"Saved model under nn_package/{name}.pth!")
        for i in range(4):
            train_model(desired_accuracy, min_step, log, max_train, name, debug, weapon_factory, item_factory)
    else:
        if input("Save model (y/n)? \n-> ").lower() == "y":
            name = input("Enter model name: ")
            torch.save(model.state_dict(), f"nn_package/{name}.pth")
            print(f"Saved model under nn_package/{name}.pth!")


if __name__ == "__main__":
    model = MovementNet()
    load_choice = input("Load existing model? (y/n) \n-> ").lower()
    debug = Debugger("Trainer", dud=True)
    weapon_factory=WeaponFactory()
    item_factory=ItemFactory()
    weapon_factory.initilise_registry()
    item_factory.initilise_registry()

    if load_choice == "y":
        model_path = input("Enter name of model: ")
        model.load_state_dict(torch.load("nn_package/" + model_path + ".pth"))
        model.eval()
        print(f"Model loaded from nn_oackage/{model_path}")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    if load_choice == "y":
        choice = input("1 - Train Model \n2 - Test Model \n-> ")
        match choice:
            case "1":
                max_train = False
                name = None
                desired_accuracy = float(
                    input("What accuracy would you like to train to? \n-> ")
                )
                if desired_accuracy == 100:
                    if input("Max train? (y/n) ").lower() == "y":
                        max_train = True
                        name = input("Enter model name: ")
                min_step = int(
                    input(
                        "Enter the minimum steps (this is just to stop the model accidently getting n accuracy before its been trained to that accuracy) \n-> "
                    )
                )
                log = input("Would you like to see the output log? (y/n) \n-> ").lower()
                train_model(desired_accuracy, min_step, log, max_train, name, debug, weapon_factory, item_factory)
            case "2":
                test_model(weapon_factory, item_factory)
            case _:
                quit()
    else:
        max_train = False  # When True it keeps saving and reloading the file after training completes and then restarts
        name = None
        desired_accuracy = float(
            input("What accuracy would you like to train to? \n-> ")
        )
        if desired_accuracy == 100:
            if input("Max train? (y/n) ").lower() == "y":
                max_train = True
                name = input("Enter model name: ")
        min_step = int(
            input(
                "Enter the minimum steps (this is just to stop the model accidently getting n accuracy before its been trained to that accuracy) \n-> "
            )
        )
        log = input("Would you like to see the output log? (y/n) \n-> ").lower()
        train_model(desired_accuracy, min_step, log, max_train, name, debug, weapon_factory, item_factory)
