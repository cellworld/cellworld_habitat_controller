import inspect
import types

class TerminalFunctions():
    def __init__(self, clients, maze_components, ip):
        self.clients = clients
        self.maze_components = maze_components
        self.ip = ip

    def get_commands(self):
        all_members = {}
        for key, client in self.clients.items():
            all_members[key] = [m for m in inspect.getmembers(client) if
                                m[0][0] != "_" and isinstance(m[1], types.MethodType) and
                                m[1].__module__ == client.__module__]

        all_commands = {}
        a = ""
        for key, members in all_members.items():
            commands = {}
            for member in members:
                try:
                    a = inspect.getfullargspec(member[1])
                    # print(type(member[1]), member[0], member[1])
                    member_name = member[0]
                    commands[member_name] = {"method": member[1], "parameters": []}
                    parameters = [p for p in a.args if p != "self"]
                    for parameter in parameters:
                        commands[member_name]["parameters"].append((parameter, a[6][parameter]))
                        # print(parameter, a[6][parameter].__name__)
                except:
                    pass
            all_commands[key] = commands
        return all_commands

    def get_parameters(self, selected_commands): #this function only takes in single unique commands or duplicates
        selected_keys = list(selected_commands.keys())
        parameters_values = []
        chosen_client = selected_keys[0]
        found_comp = False
        for parameter in selected_commands[chosen_client]["parameters"]:
            while True:
                parameter_value = input("- " + parameter[0] + " (" + parameter[1].__name__ + ") : ")
                if parameter_value == '':
                    return '', ''
                if parameter[0] == 'ip':
                    for client_name, address in self.ip.items():
                        if parameter_value in address:
                            chosen_client = client_name
                            found_comp = True
                            print(chosen_client)
                    if not found_comp:
                        print('client ip address does not exist')
                        continue
                if parameter[0] == 'door_num':
                    for maze, component in self.maze_components.items():
                        if parameter_value in str(component['doors']):
                            chosen_client = maze
                            found_comp = True
                    if not found_comp:
                        print('door does not exist')
                        continue
                if parameter[0] == 'feeder_num':
                    for maze, component in self.maze_components.items():
                        if parameter_value in str(component['feeder']):
                            chosen_client = maze
                            found_comp = True
                    if not found_comp:
                        print('feeder does not exist')
                        continue
                try:
                    parameters_values.append(parameter[1](parameter_value))
                    break
                except:
                    print("cannot convert " + parameter_value + " to " + parameter[1].__name__)
        return parameters_values, chosen_client

    def get_status(self, all_commands):
        selected_commands = []
        selected_commands.append({'experiment': all_commands['experiment']['get_experiment']})
        selected_commands.append({'maze1': all_commands['maze1']['status']})
        selected_commands.append({'maze2': all_commands['maze2']['status']})
        for selected_command in selected_commands:
            parameter_values, chosen_client = self.get_parameters(selected_command)
            try:
                status = selected_command[chosen_client]["method"](*parameter_values)
            except:
                print(f"status of {list(selected_command.keys())} could not be found")
                continue
            if chosen_client == 'experiment':
                if status.experiment_name == '':
                    print('experiment could not be found')
                else:
                    print(f'{chosen_client.upper()}:'
                          f'\n\tExperiment name: {status.experiment_name}'
                          f'\n\tDuration: {status.duration} minutes'
                          f'\n\tRemaining Time: {(status.remaining_time)/60} minutes'
                          f'\n\tEpisode Count: {status.episode_count}')
            else:
                print(f'{status.ID.upper()}:'
                      f'\n\tDoor {status.door_state[0].num}: {status.door_state[0].state}'
                      f'\n\tDoor {status.door_state[1].num}: {status.door_state[1].state}'
                      f'\n\tFeeder: {status.feeder_state}')
        return