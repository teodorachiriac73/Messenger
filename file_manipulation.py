
import shutil
import os
import re

def save_file(sender, receiver, file_name, file_data):
    base_dir='photos'
    try:
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
        safe_receiver = re.sub(r'[<>:"/\\|?*]', '_', receiver)

        new_file_name = f"from_{sender}_file_{safe_file_name}"
        new_file_path = os.path.join(base_dir, safe_receiver)

        os.makedirs(new_file_path, exist_ok=True)

        full_file_path = os.path.join(new_file_path, new_file_name)

        with open(full_file_path, 'ab') as file:
            file.write(file_data)

        return full_file_path

    except Exception as e:
        print(f"Eroare la salvarea fișierului: {e}")
        return None


def delete_client_folder():
    print('Deleting all client folders..')
    folder_path = f"clients"

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder deleted for all clients")
    else:
        print(f"Folder does not exist")
    
    return


def delete_photos_folder():
    folder_path = f"photos"

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder deleted for all photos")
    else:
        print(f"Folder does not exist")
    
    return

def create_client_folder(client_name):
    base_path = "clients"
    folder_path = os.path.join(base_path, client_name)

    if not os.path.exists(base_path):
        os.makedirs(base_path)  
        print(f"Folder principal 'clients' creat.")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  
        print(f"Folder creat pentru {client_name} la {folder_path}")
    
    return folder_path


# def create_file_for_photo(client_name):
#     folder_path = f"server_folder_for_photos/{client_name}"

#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#         print(f"File created")
#     #else:
#         #print(f"Folder already exists for {client_name}")
    
#     return folder_path



def return_client_files(client_nickname):
    folder_path = f"clients/{client_nickname}"
    
    if os.path.exists(folder_path):
        files = os.listdir(folder_path)
        
        print(f"Fisierele clientului {client_nickname}:")
        for file in files:
            print(file)
            
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                print(f.read())  
    else:
        print(f"Nu exista fisiere pentru clientul {client_nickname}")
