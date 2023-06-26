import inspect
import types

import cellworld
import json_cpp
from tqdm import tqdm
from cellworld import Experiment, Episode


class TerminalFunctions():
    def __init__(self, experiment_join, gdrive, clients, maze_components, ip):
        self.experiment_join = experiment_join
        self.gdrive = gdrive
        self.clients = clients
        self.maze_components = maze_components
        self.ip = ip
        self.resumed_exp = ''

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

    def get_parameters(self, selected_commands, defaults: {}): #this function only takes in single unique commands or duplicates
        selected_keys = list(selected_commands.keys())
        parameters_values = {key: [] for key in selected_keys}
        print(parameters_values)
        if not selected_commands[selected_keys[0]]["parameters"]:
            return parameters_values

        for parameter in selected_commands[selected_keys[0]]["parameters"]:
            requests = True
            found_comp = False
            check = []
            while requests:
                if parameter[0] == 'world_configuration':
                    parameter_value = 'hexagonal'
                elif parameter[0] == 'world_implementation':
                    parameter_value = 'mice'
                else:
                    if parameter[0] in defaults:
                        parameter_value = input("- " + parameter[0] + " (" + parameter[1].__name__ + ") [" + str(defaults[parameter[0]]) + "]: ") or str(defaults[parameter[0]])
                    else:
                        parameter_value = input("- " + parameter[0] + " (" + parameter[1].__name__ + "): ")

                if parameter_value == '':
                    return False

                if parameter[0] == 'ip':
                    if parameter_value not in list(self.ip.values()):
                        print('client ip address does not exist')
                        continue
                    for key in selected_keys:
                        if parameter_value != self.ip[key]:
                            parameters_values[key].append(None)
                            check.append(False)
                        else:
                            parameters_values[key].append(parameter[1](parameter_value))
                            check.append(True)
                            requests = False

                elif parameter[0] == 'rewards_cells':
                    if parameter_value == 'none':
                        parameters_values[key].append(cellworld.Cell_group_builder())
                    else:
                        parameter_value = cellworld.Cell_group_builder([int(x) for x in parameter_value.split(',')])
                        parameters_values[key].append(parameter_value)
                    requests = False
                elif parameter[0] == 'rewards_orientations' or parameter[0] == 'rewards_sequence':
                    if parameter_value == 'none':
                        parameters_values[key].append(json_cpp.JsonList())
                    else:
                        parameter_value = json_cpp.JsonList([int(x) for x in parameter_value.split(',')], list_type = int)
                        parameters_values[key].append(parameter_value)
                    requests = False

                elif parameter[0] == 'door_num':
                    for maze, component in self.maze_components.items():
                        if parameter_value in str(component['doors']):
                            found_comp = True
                    if not found_comp:
                        print('client ip address does not exist')
                        continue

                    for key in selected_keys:
                        if parameter[1](parameter_value) not in self.maze_components[key]['doors']:
                            parameters_values[key].append(None)
                        else:
                            parameters_values[key].append(parameter[1](parameter_value))
                            requests = False

                elif parameter[0] == 'feeder_num':
                    for maze, component in self.maze_components.items():
                        if parameter_value in str(component['feeder']):
                            found_comp = True
                    if not found_comp:
                        print('feeder does not exist')
                        continue

                    for key in selected_keys:
                        if parameter[1](parameter_value) not in self.maze_components[key]['feeder']:
                            parameters_values[key].append(None)
                        else:
                            parameters_values[key].append(parameter[1](parameter_value))
                            requests = False

                else:
                    for key in selected_keys:
                        try:
                            parameters_values[key].append(parameter[1](parameter_value))
                            requests = False
                        except:
                            print("cannot convert " + parameter_value + " to " + parameter[1].__name__)
                            break
        return parameters_values

    def get_status(self, all_commands, defaults):
        selected_commands = []
        selected_commands.append({'experiment': all_commands['experiment']['get_experiment']})
        selected_commands.append({'maze1': all_commands['maze1']['status']})
        selected_commands.append({'maze2': all_commands['maze2']['status']})
        for selected_command in selected_commands:
            parameter_values = self.get_parameters(selected_command, defaults)
            chosen_client = list(parameter_values.keys())[0]
            parameters = parameter_values[chosen_client]
            try:
                status = selected_command[chosen_client]["method"](*parameters)
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

    # def experiment_finished(self, exp_name):
    #     exp_log = self.experiment_join.get_experiment_file(exp_name).replace(".json", "_full.json")
    #     experiment = Experiment.load_from_file(exp_log)
    #     resumed = False
    #     if experiment and not experiment.episodes[-1]:
    #         self.experiment_join.join_episodes(exp_name)
    #     self.gdrive.upload_exp(exp_name, resumed)
    #     return
