
import shutil
import os

def delete_client_folder():
    print('Deleting all client folders..')
    folder_path = f"clients"

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder deleted for all clients")
    else:
        print(f"Folder does not exist")
    
    return


def create_client_folder(client_name):
    folder_path = f"clients/{client_name}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created for {client_name} at {folder_path}")
    #else:
        #print(f"Folder already exists for {client_name}")
    
    return folder_path



def return_client_files(client_name):
    folder_path = f"clients/{client_name}"
    files = os.listdir(folder_path)
    print(files)
    return files