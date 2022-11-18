from gdrive import *
from experiment_join import ExperimentJoin

# vid_dir_path = 'test-alex-2022-02-25/videos'
# results_dir_path = 'test-alex-2022-02-25/analysis-results'
# part_labels = {'head': 'bodypart1', 'body': 'bodypart2', 'butt': 'bodypart3'}

experiment_log_folder = "C:/Users/AlexT/OneDrive/Laptop Documents/Northwestern/[0] Research/Testing/"

experiment_join = ExperimentJoin(experiment_log_folder)
gdrive = GDrive(experiment_log_folder, experiment_join)
file_list = gdrive.drive.ListFile({'q': f"'{gdrive.data_id}' in parents and trashed=false"}).GetList()
# gdrive.get_exp_folder_id('TESTING_20221114_1426_test_21_05_test')
gdrive.upload_exp('t_20221116_1022_MMM11_21_05_RT1')
# for file1 in file_list:
#   print('title: %s, id: %s' % (file1['title'], file1['id']))



# runDLC = RunDLC(config_path='test-alex-2022-02-25/config.yaml', vid_dir_path='test-alex-2022-02-25/videos')
# chosenfile = gdrive.grab_json(path='logs')
# json_head_dir = JsonHeadDir(chosenfile, results_dir_path)

# #SAVE VIDEOS FROM GOOGLE DRIVE
# experiment = gdrive.find_exp(chosenfile, gdrive.musculus_id)
# gdrive.save_video(chosenfile, dir_path = vid_dir_path, exp_content = experiment)