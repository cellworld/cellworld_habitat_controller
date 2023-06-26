from cellworld_experiment_service import ExperimentClient
from pi_client import PiClient
from terminal_functions import TerminalFunctions
import threading
import keyboard
from experiment_join import ExperimentJoin
from json_cpp import JsonObject
from gdrive import *

clients = {'experiment': ExperimentClient(), 'maze1': PiClient(), 'maze2': PiClient()}
ip = {'experiment': '127.0.0.1', 'maze1': '192.168.137.100', 'maze2': '192.168.137.200'}
experiment_log_folder = "/research/data"
# experiment_log_folder = "C:/Users/AlexT/OneDrive/Laptop Documents/Northwestern/[0] Research/Testing/"
for key, client in clients.items():
    try:
        response = client.connect(ip[key])
        if response:
            print(f'connected to {key}')
        else:
            print(f'CANNOT connect to {key}!!!!')
    except:
        print(f'CANNOT connect to {key}!!!!')
maze_components = {'maze1': {'doors': [1, 2], 'feeder': [1]},
                   'maze2': {'doors': [0, 3], 'feeder': [2]}}
experiment_join = ExperimentJoin(experiment_log_folder)
gdrive = GDrive(experiment_log_folder, experiment_join)
term_functions = TerminalFunctions(experiment_join, gdrive, clients, maze_components, ip)
all_commands = term_functions.get_commands()
# clients['experiment'].on_experiment_finished = term_functions.experiment_finished
# clients['experiment'].subscribe()

defaults = {"experiment_name": "", "occlusions": "21_05", "rewards_cells": "none", "rewards_orientations": "none", "rewards_sequence": "none"}
command = ""
keyboard.add_hotkey('alt+shift', clients['maze1'].open_door, args=[2])


while command != "end":
    selected_commands = {}
    command = input("_________________\nHabitat: ")
    command = command.replace(" ", "_")
    if command == "exp_join":
        experiment_name = input("experiment_name" + "[" + str(defaults["experiment_name"]) + "]: ") or str(defaults["experiment_name"])
        experiment_join.join_episodes(experiment_name)
        continue
    if command == "upload_experiment":
        check = input("This will LOCK terminal for several minutes. Proceed? (Y/N): ")
        if check == 'y' or check == 'Y':
            experiment_name = input("experiment_name" + "[" + str(defaults["experiment_name"]) + "]: ") or str(
                defaults["experiment_name"])
            experiment_join.join_episodes(experiment_name)
            gdrive.upload_exp(experiment_name)
        continue
    if command == "reconnect":
        for key, client in clients.items():
            try:
                response = client.connect(ip[key])
                if response:
                    print(f'connected to {key}')
                else:
                    print(f'CANNOT connect to {key}!!!!')
            except:
                print(f'CANNOT connect to {key}!!!!')
        continue
    if command == "help":
        for key, commands in all_commands.items():
            print(f'{key}:')
            print(f'\t{list(commands.keys())}')
        continue
    if command == "":
        continue
    if command == "status":
        term_functions.get_status(all_commands, defaults)
        continue
    for key, commands in all_commands.items():
        if command in commands:
            selected_commands[key] = commands[command]
    if not selected_commands:
        print("command not found.")
    else:
        parameter_values = term_functions.get_parameters(selected_commands, defaults)
        if not parameter_values:
            continue
        for key, parameters in parameter_values.items():
            if None not in parameters:
                try:
                    response = selected_commands[key]["method"](*parameters)
                    print()
                    print("Response: ")
                    if isinstance(response, JsonObject):
                        for member in response.__dict__:
                            print("- " + member + ":", getattr(response, member))
                            if member in defaults:
                                defaults[member] = getattr(response, member)
                    else:
                        print(response)
                except:
                    print(f'request failed for {key}')
