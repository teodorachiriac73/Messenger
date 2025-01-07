import os

def create_client_folder(client_name):
    folder_path = f"clients/{client_name}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created for {client_name} at {folder_path}")
    #else:
        #print(f"Folder already exists for {client_name}")
    
    return folder_path
