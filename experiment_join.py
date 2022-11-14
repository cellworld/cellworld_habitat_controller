from cellworld import Experiment, Episode

class ExperimentJoin():

    def __init__(self):
        self.experiment_log_folder = "/research/data"

    def get_experiment_folder(self, experiment_name):
        return self.experiment_log_folder + "/" + experiment_name.split('_')[0] + "/" + experiment_name

    def get_experiment_file(self, experiment_name):
        return self.get_experiment_folder(experiment_name) + "/" + experiment_name + "_experiment.json"

    def get_episode_folder(self, experiment_name, episode_number):
        return self.get_experiment_folder(experiment_name) + f"/episode_{episode_number:03}"

    def get_episode_file(self, experiment_name, episode_number):
        return self.get_episode_folder(experiment_name,
                                  episode_number) + f"/{experiment_name}_episode_{episode_number:03}.json"

    def join_episodes(self, experiment_name):
        experiment_file = self.get_experiment_file(experiment_name)
        print(f'\ncombining episodes for {experiment_file}')
        print("_________________\nHabitat: ")
        experiment = Experiment.load_from_file(experiment_file)
        if not experiment:
            print("file not found")
            print("_________________\nHabitat: ")

        experiment.episodes.clear()
        for i in range(experiment.episode_count):
            episode = Episode.load_from_file(self.get_episode_file(experiment_name, i))
            experiment.episodes.append(episode)

        experiment.save(self.get_experiment_file(experiment_name).replace(".json", "_full.json"))





