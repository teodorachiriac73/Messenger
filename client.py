import socket
import threading
import tkinter as tk
import os 
import ssl
import socket
import base64
from tkinter import filedialog

from log_functions import log_message_chatAll,log_private_message, open_logs
from create_sockets import create_ssl_client_socket

#Global variables
stop_client = threading.Event()
chat_window = None
active_clients_frame = None
messages_display = None
direct_message_windows_dictionary = {}  


try:  # Create a SSL client socket
    client = create_ssl_client_socket()
    client.connect(('localhost', 1234))  
except ssl.SSLError as e:
    print(f"SSL connection error: {e}")
    client.close()


def send_file_to_user(sender_nickname, sender_client, receiver_client, file_path):
    """
    Function that sends a file to another client. 
    We send chunks of 512 bites of data until there's no data to read from the server.
    Then we send the message with 'done' at the end to signal the end of the file.
    """
    try:
        with open(file_path, 'rb') as file:
        
            while True:
                file_data=  file.read(512)
                message=f'file:from:{sender_nickname}:to:{receiver_client}:{os.path.basename(file_path)}:{file_data}'
                
                if not file_data:
                    message=f'file:from:{sender_nickname}:to:{receiver_client}:{os.path.basename(file_path)}:done'
                    break

                file_data_encoded = base64.b64encode(file_data).decode('utf-8')
                
                message = f'file:from:{sender_nickname}:to:{receiver_client}:{os.path.basename(file_path)}:{file_data_encoded}'
                client.send(message.encode('utf-8'))

    except Exception as e:
        print(f"Error sending file: {e}")

def open_send_file_to_user(nickname,client, another_client):
    """
    Opens a file using 'filedialog' and sends it to another client.
    """
    file_path=filedialog.askopenfilename(title="Select a file to send to {another_client}", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
    if file_path:
        send_file_to_user(nickname,client, another_client, file_path)

def on_emoji_click(emoji_char, message_entry):
    message_entry.insert(tk.END, emoji_char)


def display_message_in_direct_chat(messages_display, message):
    """
    Function that displays a message in the direct / private chat window.
    """
    messages_display.config(state='normal')
    messages_display.insert(tk.END, message + '\n')
    messages_display.config(state='disabled')
    messages_display.see(tk.END)

def on_client_click(client, another_client):
    """
    When there is a click on a client from the active clients list, a new window is created for direct messaging.
    This window has a text box for messages, a list of emojis, 
    an entry for sending messages and a button for sending files.
    """
    if another_client not in direct_message_windows_dictionary:
        direct_message_window = tk.Toplevel(chat_window)

        direct_message_window.title("Direct message to " + another_client)
        direct_message_window.geometry('400x400')
        direct_message_window.resizable(True, True)

        messages_display = tk.Text(direct_message_window, state='disabled', wrap='word')
        messages_display.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        
        direct_message_window.grid_rowconfigure(0, weight=1)  # o coloana=messages display, care se poate extinde si 2 randuri 
        direct_message_window.grid_rowconfigure(1, weight=0) 
        direct_message_window.grid_rowconfigure(2, weight=0) 
        direct_message_window.grid_rowconfigure(3, weight=0)
        direct_message_window.grid_columnconfigure(0, weight=1) 
        def send_private_message():
            message = message_entry.get()
            if message.strip():
                command = f"message:from:{nickname}:to:{another_client}:{message.strip()}"
                try:
                    client.send(command.encode('utf-8'))
                    log_private_message(message,nickname, another_client)
                    display_message_in_direct_chat(messages_display, f"You: {message.strip()}")
                except Exception as e:
                    log_private_message(message,nickname, another_client)
                    display_message_in_direct_chat(messages_display, "Error: Failed to send message.")
                message_entry.delete(0, tk.END)

        
        message_entry = tk.Entry(direct_message_window)
        message_entry.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

        emoji_list=tk.Frame(direct_message_window)
        emoji_list.grid(row=2, column=0, padx=10, pady=5, sticky='ew')
        emojis = ["🙂", "😊", "😂", "😎", "❤️", "👍", "😢", "😡"]
        for emoji in emojis:
            emoji_button = tk.Button(emoji_list, text=emoji, font=("Segoe UI Emoji", 14),
                                    command=lambda e=emoji: on_emoji_click(e, message_entry))
            emoji_button.pack(side=tk.LEFT, padx=5, pady=5)

        send_button = tk.Button(direct_message_window, text="Send", command=send_private_message)
        send_button.grid(row=3, column=0, padx=10, pady=5)

        send_file_button= tk.Button(direct_message_window, text="Send file", command=lambda: open_send_file_to_user(nickname,client, another_client)) 
        send_file_button.grid(row=3, column=1, padx=10, pady=5)

        def close_private_message_window():
            # When closing a private message window, it is also removed from the dictionary
            del direct_message_windows_dictionary[another_client]
            direct_message_window.destroy()

        direct_message_window.protocol("WM_DELETE_WINDOW", close_private_message_window)

        # Save the window in the dictionary
        direct_message_windows_dictionary[another_client] = direct_message_window
    else:
        direct_message_windows_dictionary[another_client].lift()




def send_msg_after_login(enter_msg_entry):
    """
    Function that sends a message to the server after the client logs in.
    The entry for entering messages is deleted after sending the message.
    """
    if not stop_client.is_set():
        message = enter_msg_entry.get()
        new_message = f'{nickname}: {message}'
        try:
            client.send(new_message.encode('utf-8'))
            
            enter_msg_entry.delete(0, tk.END)
        except Exception as e:
            print(f"Error occurred at sending message after login: {e}")
            client.close()
            stop_client.set()


def open_chat_window():
    """
    This function creates the chat window after the client logs in.
    There are 2 frames: one for active clients and one for the chat.
    The active clients section has a button to see the logs.
    The chat section has a text box for messages and an entry for sending messages.
    """
    global active_clients_frame, chat_window, messages_display

    chat_window = tk.Tk()
    chat_window.title("Chat window")
    chat_window.geometry('600x500')
    chat_window.resizable(True, True)

    main_frame = tk.Frame(chat_window)
    main_frame.pack(fill=tk.BOTH, expand=True)

    active_clients_frame = tk.Frame(main_frame, width=300, bg="#5D7257")
    active_clients_label = tk.Label(active_clients_frame, text='Message active clients:', bg="#5D7257", fg='darkblue')
    active_clients_label.pack(side=tk.TOP, padx=10, pady=5)
    active_clients_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    
    open_logs_button = tk.Button(active_clients_frame, text='See your logs', command=lambda: open_logs(nickname), fg='black')
    open_logs_button.pack(side=tk.BOTTOM, padx=10, pady=5)
    # chat - in partea stanga
    chat_frame = tk.Frame(main_frame)
    chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    messages_display = tk.Text(chat_frame, state='disabled', wrap='word',bg="#E1E0E0")
    messages_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    send_message_frame = tk.Frame(chat_frame)
    send_message_frame.pack(fill=tk.X, padx=10, pady=5)

    enter_msg_entry = tk.Entry(send_message_frame)
    enter_msg_entry.grid(row=0, column=0, sticky="ew", padx=5)

    send_message_button = tk.Button(send_message_frame, text='Send',
                                     command=lambda: send_msg_after_login(enter_msg_entry), fg='purple')
    send_message_button.grid(row=0, column=1, padx=5)

    send_message_frame.grid_columnconfigure(0, weight=1)


    def close_chat_window():
        """
        Closes the chat window and sends 'exit' to the server.
        """
        client.send('exit'.encode('utf-8'))
        stop_client.set()
        chat_window.quit()
        chat_window.destroy()
        client.close()

    #Define the protocol for closing the chat window and put chat_window in the main loop
    chat_window.protocol("WM_DELETE_WINDOW", close_chat_window)
    chat_window.mainloop()



def receive_message_from_srv():
    """
    Function that receives message from server while client is running. 
    Cases:
    - from login: already connected, login failed, login successful
    - server is closing
    - tells the ui to actualize if the message is active users

    """
    global active_clients_frame, chat_window, messages_display

    while not stop_client.is_set():
        try:
            if stop_client.is_set():
                break
            message = client.recv(1024).decode('utf-8')
            if not message:
                break

            if message == 'the server is closing':
                stop_client.set()
                tkWindow.quit()
                client.close()
                break
            elif message == 'already connected!':
                status_label.config(text='Status: user already connected', fg='red')
                stop_client.set()
                tkWindow.quit()
                client.close()
                break

            elif message.startswith('login:'):
                if message == 'login:failed':
                    print('Please enter a valid nickname and password')
                    def delete_entries():
                        nickname_entry.delete(0, tk.END)
                        password_entry.delete(0, tk.END)
                        status_label.config(text='Status: Login failed', fg='red')
                    tkWindow.after(0, delete_entries)
                else:
                    print('login message: ', message)
                    tkWindow.after(0, lambda: [
                        status_label.config(text='Status: Login successful', fg='green'),
                        nickname_entry.config(state='disabled'),
                        password_entry.config(state='disabled'),
                        login_button.config(state='disabled'),
                        tkWindow.destroy(),
                        open_chat_window()
                    ])

            elif message.startswith("active users:"):
                active_users_list = message[len("active users: "):]
                active_users_list = active_users_list.strip("[]").replace("'", "").split(", ")

                def update_active_clients():
                    for widget in active_clients_frame.winfo_children():
                        widget.destroy()
                    open_logs_button = tk.Button(active_clients_frame, text='See your logs', command=lambda: open_logs(nickname), fg='black')
                    open_logs_button.pack(side=tk.BOTTOM, padx=10, pady=5)
                    tk.Label(active_clients_frame, text='Message active clients:', bg="#5D7257", fg='darkblue').pack(anchor="w", padx=10, pady=5)
                    for user_to_message in active_users_list:
                        user_label = tk.Label(active_clients_frame, text=user_to_message.strip(), bg="#5D7257", fg='darkblue')
                        user_label.pack(anchor="w", padx=10, pady=2)
                        if user_to_message != nickname:
                            user_label.bind("<Button-1>", lambda event, user_to_message=user_to_message: on_client_click(client, user_to_message))

                tkWindow.after(0, update_active_clients)

            elif message.startswith('message:from:') and f"to:{nickname}:" in message:
                parts = message.split(':')
                sender = parts[2]  
                message_content = ':'.join(parts[5:])  

                log_private_message(f'from {sender}:{message_content}',nickname,sender)

                if sender in direct_message_windows_dictionary:
                    display_message_in_direct_chat(direct_message_windows_dictionary[sender].winfo_children()[0], f"{sender}: {message_content}")
                else:
                    on_client_click(client,sender)
                    display_message_in_direct_chat(direct_message_windows_dictionary[sender].winfo_children()[0], f"{sender}: {message_content}")
            
            else:
                print(message)
                def display_messages_common_chat(message):
                    messages_display.config(state='normal')
                    messages_display.insert(tk.END, message + '\n')
                    messages_display.config(state='disabled')
                    messages_display.see(tk.END)

                tkWindow.after(0, lambda: display_messages_common_chat(message))

        except:
            if stop_client.is_set():
                break
            print("An error occurred at receiving messages")
            client.close()
            break

def login():
    """
    Login function that takes the nickname and password from input and sends them to server.
    """
    global nickname, password
    nickname = nickname_entry.get()
    password = password_entry.get()
    print(nickname, password)

    if not nickname.strip() or not password.strip():
        nickname_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        status_label.config(text='Status: Login failed', fg='red')
        return

    try:
        if not stop_client.is_set():
            client.send(nickname.encode('utf-8'))
            client.send(password.encode('utf-8'))

    except Exception as e:
        print('Error at login ', e)
        return

def close_app():
    """
    Closes login window and client socket.
    """
    client.send('exit'.encode('utf-8'))
    stop_client.set()
    client.close()
    tkWindow.destroy()



receive_thread = threading.Thread(target=receive_message_from_srv)
receive_thread.start()
 


# Basic GUI for introducing nickname and password

tkWindow = tk.Tk()
tkWindow.title('Messenger app')
tkWindow.geometry('400x400')
tkWindow.resizable(True, True)


nickname_label = tk.Label(tkWindow, text='Enter a nickname')
nickname_label.pack(padx=10, pady=5)

nickname_entry = tk.Entry(tkWindow)
nickname_entry.pack(padx=10, pady=5)

password_label = tk.Label(tkWindow, text='Enter a password')
password_label.pack(padx=10, pady=5)

password_entry = tk.Entry(tkWindow)
password_entry.pack(padx=10, pady=5)

login_button = tk.Button(tkWindow, text='Login', command=login)
login_button.pack(padx=10, pady=5)

status_label = tk.Label(tkWindow, text='Status:', fg='blue')
status_label.pack(padx=10, pady=5)

tkWindow.protocol("WM_DELETE_WINDOW", close_app)

tkWindow.mainloop()