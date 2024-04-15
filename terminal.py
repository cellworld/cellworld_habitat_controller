import cellworld
from terminal_functions import *
import threading
import keyboard
from experiment_join import ExperimentJoin
from json_cpp import JsonObject
from gdrive import *

tasks = ['BOTEVADE', 'OASIS']
while True:
    task_index = input(f"Please input index of task {tasks} : ")
    try:
        selected_task = tasks[int(task_index)]
        break
    except Exception as e:
        print(e)
experiment_log_folder = "/research/data"
# experiment_log_folder = "C:/Users/AlexT/OneDrive/Laptop Documents/Northwestern/RESEARCH/Testing/"
experiment_join = ExperimentJoin(experiment_log_folder)
gdrive = GDrive(experiment_log_folder, experiment_join)
term_functions = TerminalFunctions(experiment_join, gdrive, tasks)

clients, ip, maze_components = term_functions.get_clients_ips(selected_task)
all_commands = term_functions.get_commands()

for key, client in clients.items():
    try:
        response = client.connect(ip[key])
        if response:
            print(f'connected to {key}')
        else:
            print(f'CANNOT connect to {key}!!!!')
    except:
        print(f'CANNOT connect to {key}!!!!')

# clients['experiment'].on_experiment_finished = term_functions.experiment_finished
# clients['experiment'].connect('127.0.0.1')

defaults = {"experiment_name": "", "occlusions": "21_05", "rewards_cells": cellworld.Cell_group_builder(),
            "rewards_orientations": json_cpp.JsonList(), "rewards_sequence": cellworld.Cell_group_builder()}
command = ""

hotkeys = {'alt+shift': {'command': clients['maze1'].open_door, 'arg': [2]},
           '1+up': {'command': clients['maze1'].open_door, 'arg': [1]},
           '2+up': {'command': clients['maze1'].open_door, 'arg': [2]},
           '3+up': {'command': clients['maze2'].open_door, 'arg': [3]},
           '0+up': {'command': clients['maze2'].open_door, 'arg': [0]},
           '1+down': {'command': clients['maze1'].close_door, 'arg': [1]},
           '2+down': {'command': clients['maze1'].close_door, 'arg': [2]},
           '3+down': {'command': clients['maze2'].close_door, 'arg': [3]},
           '0+down': {'command': clients['maze2'].close_door, 'arg': [0]},
           '1+.': {'command': clients['maze1'].give_reward, 'arg': [2]},
           '2+.': {'command': clients['maze1'].open_door, 'arg': [2]},
           '*+-': {'command': clients['experiment'].finish_episode, 'arg': []},
           '*+plus': {'command': clients['experiment'].start_episode, 'arg': [defaults["experiment_name"]]},
           '*+t': {'command': clients['experiment'].start_experiment, 'arg': ['TEST', 'test', 'hexagonal', 'mice',
                                                                              '00_00', 'test', 10]},
           '*+end': {'command': clients['experiment'].finish_experiment, 'arg': [defaults["experiment_name"]]}
           }
# print(cellworld.Cell_group_builder())
# def check_hotkey(message):
#     print(message)
#     return
#
# hotkey_check = {'alt+shift': {'command': check_hotkey, 'arg': ['alt shift']},
#            '1+up': {'command': check_hotkey, 'arg': ['open_door']},
#            '1+down': {'command': check_hotkey, 'arg': ['close_door']},
#            '1+.': {'command': check_hotkey, 'arg': ['give_reward']},
#            '*+-': {'command': check_hotkey, 'arg': ['finish_episode']},
#            '*+plus': {'command': check_hotkey, 'arg': ["start_episode"]},
#             '*+end': {'command': check_hotkey, 'arg': ["start_test_experiment"]}
#            }

# keyboard.add_hotkey('alt+shift', clients['maze1'].open_door, args=[2])
for hotk, hotk_func in hotkey_check.items():
    keyboard.add_hotkey(hotk, hotk_func['command'], args= hotk_func['arg'])

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
