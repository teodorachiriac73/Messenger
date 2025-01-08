import os
from datetime import datetime
from file_manipulation import create_client_folder
from tkinter import messagebox, filedialog


def open_logs(client_nickname):
    """
    Every client has a folder with their nickname in the 'clients' folder.
    This function opens a file dialog to select a log file from the client's folder, if the folder isn't empty.
    """

    folder_path = f"clients/{client_nickname}"

    if os.path.exists(folder_path):
        file_path = filedialog.askopenfilename(
            initialdir=folder_path,  
            title="Selecteaza un fisier de log",  
            filetypes=(
                ("All files", "*"),
                ("Image files", "*.png;*.jpg;*.jpeg"),
                ("Text files", "*.txt")
            )
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    
                messagebox.showinfo("Continut fisier", file_content)

            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la fisier/ fisierul e poza")
        else:
            print("Nu a fost selectat niciun fisier.")
    else:
        messagebox.showerror("Eroare", f"Folderul clientului {client_nickname} nu exista.")


def log_message_chatAll(message, client_nickname):
    """
    Creates a file that has records of the common chat.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    folder_path = create_client_folder(client_nickname)
    file_path = os.path.join(folder_path, f"common_chat.txt")
    
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"[{timestamp}] {message}\n")

def log_private_message(message, client_nickname, another_client):
    """
    Between two clients that have a private conversation, a file is created to store the messages.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    folder_path = create_client_folder(client_nickname)
    file_path = os.path.join(folder_path, f"chat_me_to_{another_client}.txt")
    
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"[{timestamp}] {message}\n")
