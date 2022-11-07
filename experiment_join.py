from cellworld import Experiment, Episode

experiment_log_folder = "/research/data"

def get_experiment_folder (experiment_name):
    return experiment_log_folder + "/" + experiment_name.split('_')[0] + "/" + experiment_name


def get_experiment_file (experiment_name):
    return get_experiment_folder(experiment_name) + "/" + experiment_name + "_experiment.json"


def get_episode_folder (experiment_name, episode_number):
    return get_experiment_folder(experiment_name) + f"/episode_{episode_number:03}"


def get_episode_file (experiment_name, episode_number):
    return get_episode_folder(experiment_name, episode_number) + f"/{experiment_name}_episode_{episode_number:03}.json"


experiment_name = input("experiment_name: ")
experiment_file = get_experiment_file(experiment_name)
print("opening " + experiment_file)
experiment = Experiment.load_from_file(experiment_file)
if not experiment:
    print("file not found")
    exit(1)

experiment.episodes.clear()
for i in range(experiment.episode_count):
    episode = Episode.load_from_file(get_episode_file(experiment_name, i))
    experiment.episodes.append(episode)

experiment.save(get_experiment_file(experiment_name).replace(".json", "_full.json"))



