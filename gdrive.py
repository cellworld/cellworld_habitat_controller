import os
from tqdm import tqdm
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# MUST USE httplib2==0.15.0 IN PIP



class GDrive():
    def __init__(self, experiment_log_folder, experiment_join):
        self.gauth = GoogleAuth(settings_file= 'config/settings.yaml')
        self.gauth.LoadCredentialsFile("config/mycreds.txt")
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            # Refresh them if expired
            self.gauth.Refresh()
        else:
            # Initialize the saved creds
            self.gauth.Authorize()
        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile("config/mycreds.txt")

        self.drive = GoogleDrive(self.gauth)
        self.habitat_id = '1pwsS5t5w38pVgz13-pt77fN4b5YxGlhq'
        self.data_id = '1SJ0CZyrv3_Fax3SkkDf42P43zVBP3Ful'
        self.experiment_log_folder = experiment_log_folder
        self.experiment_join = experiment_join

    def show_content(self, fileList_command: list, display: bool = True) -> (list,list):
        id = []
        filenames = []
        for j, file in enumerate(fileList_command):
            title = file['title']
            id.append(file['id'])
            filenames.append(title)
            if display:
                print(f'---{j}: {title}, ID: {id[-1]}')
        return {'id':id, 'filenames': filenames}

    def file_exist(self, file_name: str, parent_folder_id: str):
        exist = False
        filelist_command = self.drive.ListFile({'q': f"'{parent_folder_id}' in parents and trashed=false"}).GetList()
        filelist = self.show_content(filelist_command, display=False)
        if file_name in filelist['filenames']:
            exist = True
        return exist

    def find_index(self, file_name: str, parent_folder_id: str):
        filelist_command = self.drive.ListFile({'q': f"'{parent_folder_id}' in parents and trashed=false"}).GetList()
        filelist = self.show_content(filelist_command, display=False)
        id_index = filelist['filenames'].index(file_name)
        index = filelist['id'][id_index]
        return index

    def create_file(self, title: str, parent_id:str, folder: bool = False):
        if folder:
            file_metadata = {
                'title': title,
                'parents': [{'id': [parent_id]}],
                'mimeType': 'application/vnd.google-apps.folder'
            }
        else:
            file_metadata = {
                'title': title,
                'parents': [{'id': [parent_id]}],
            }
        file = self.drive.CreateFile(file_metadata)
        if folder:
            file.Upload()
            file_id = self.find_index(title, parent_id)
            return file, file_id
        else:
            return file

    def get_exp_folder_id(self, experiment_name: str, data_id: str = '1SJ0CZyrv3_Fax3SkkDf42P43zVBP3Ful'):
        prefix = experiment_name.split('_')[0]
        if not self.file_exist(prefix, data_id):
            prefix_folder, prefix_folder_id = self.create_file(prefix, data_id, folder=True)
        else:
            prefix_folder_id = self.find_index(prefix, data_id)

        if not self.file_exist(experiment_name, prefix_folder_id):
            exp_folder, exp_folder_id = self.create_file(experiment_name, prefix_folder_id, folder=True)
        else:
            exp_folder_id = self.find_index(experiment_name, prefix_folder_id)
        return exp_folder_id

    def upload_loop(self, base_path, dir_id, dir_name, prog_bar, level):
        for content in os.listdir(base_path):
            content_path = base_path + '/' + content
            if os.path.isdir(content_path):
                if not self.file_exist(content, dir_id):
                    subdir, subdir_id = self.create_file(content, dir_id, folder=True)
                else:
                    # subdir_id = self.find_index(content, dir_id)
                    continue
                subdir_path = content_path
                sublevel = level + 1
                dir_name = content
                self.upload_loop(subdir_path, subdir_id, dir_name, prog_bar, sublevel)
            else:
                file = self.create_file(content, dir_id, folder=False)
                file.SetContentFile(content_path)
                prog_bar.set_description(f"Uploading {dir_name}/{content}")
                prog_bar.refresh()
                file.Upload()
                prog_bar.update()

    def upload_exp(self, experiment_name: str):
        exp_path = self.experiment_join.get_experiment_folder(experiment_name)
        exp_folder_id = self.get_exp_folder_id(experiment_name)
        prog_bar = tqdm(range(sum([len(files) for r, d, files in os.walk(exp_path)])), position=0, leave=True)
        level = 0
        dir_name = experiment_name
        self.upload_loop(exp_path, exp_folder_id, dir_name, prog_bar, level)
        return