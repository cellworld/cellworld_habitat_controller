from cellworld_experiment_service import ExperimentClient
from pi_client import PiClient
from terminal_functions import TerminalFunctions

clients = {'experiment': ExperimentClient(), 'maze1': PiClient(), 'maze2': PiClient()}
ip = {'experiment': '127.0.0.1', 'maze1': '192.168.137.100', 'maze2': '192.168.137.200'}
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
term_functions = TerminalFunctions(clients, maze_components, ip)
all_commands = term_functions.get_commands()

command = ""
while command != "end":
    selected_commands = {}
    command = input("_________________\nHabitat: ")
    if command == "help":
        for key, commands in all_commands.items():
            print(f'{key}:')
            print(f'\t{list(commands.keys())}')
        continue
    if command == "":
        continue
    if command == "status":
        term_functions.get_status(all_commands)
        continue
    for key, commands in all_commands.items():
        if command in commands:
            selected_commands[key] = commands[command]
    if not selected_commands:
        print("command not found.")
    else:
        parameter_values = term_functions.get_parameters(selected_commands)
        if not parameter_values:
            continue
        for key, parameters in parameter_values.items():
            if None not in parameters:
                # print(key)
                # print(parameters)
                try:
                    print(selected_commands[key]["method"](*parameters))
                except:
                    print(f'request failed for {key}')
