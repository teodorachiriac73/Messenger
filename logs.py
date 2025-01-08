import os
from datetime import datetime
from file_manipulation import create_client_folder

def log_message_chatAll(message, client_nickname):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    folder_path = create_client_folder(client_nickname)
    file_path = os.path.join(folder_path, f"{client_nickname}.txt")
    
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"[{timestamp}] {message}\n")

def log_private_message(message, client_nickname, another_client):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    folder_path = create_client_folder(client_nickname)
    file_path = os.path.join(folder_path, f"chat_me_to_{another_client}.txt")
    
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"[{timestamp}] {message}\n")
