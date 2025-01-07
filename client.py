import socket
import select
import threading 
from datetime import datetime

import tkinter as tk

stop_client= threading.Event()
chat_window=None
active_clients_frame = None
messages_display=None

def on_client_click(client_name):
    def send_direct_message():
        message = message_entry.get()
        if message.strip():
            command = f"message:to:{client_name}:{message.strip()}"
            try:
                client.send(command.encode('ascii'))
                print(f"Sent message to {client_name}: {message.strip()}")
            except Exception as e:
                print(f"Failed to send message to {client_name}: {e}")
        direct_message_window.destroy()

    
    direct_message_window = tk.Toplevel(chat_window)
    direct_message_window.title(f"Message to {client_name}")
    direct_message_window.geometry("300x150")
    
    tk.Label(direct_message_window, text=f"Send a message to {client_name}").pack(pady=10)

    message_entry = tk.Entry(direct_message_window)
    message_entry.pack(fill=tk.X, padx=10, pady=5)

    send_button = tk.Button(direct_message_window, text="Send", command=send_direct_message)
    send_button.pack(pady=10)

    direct_message_window.mainloop()

def send_msg_after_login(enter_msg_entry):
    if not stop_client.is_set():
        message=enter_msg_entry.get()
        new_message = f'{nickname}: {message}'
        try:
            
            client.send(new_message.encode('ascii'))
            enter_msg_entry.delete(0,tk.END)
        except Exception as e:
                print(f"Error occured at sending message after login: {e}")
                client.close()
                stop_client.set()
                
def open_chat_window():

    global active_clients_frame,chat_window, messages_display

    chat_window = tk.Tk()
    chat_window.title("Chat window")
    chat_window.geometry('600x500')
    chat_window.resizable(True, True)

    
    main_frame = tk.Frame(chat_window)
    main_frame.pack(fill=tk.BOTH, expand=True)

    
    active_clients_frame = tk.Frame(main_frame, width=300, bg="#5D7257")
    active_clients_label = tk.Label(active_clients_frame, text='Message active clients:',bg="#5D7257" ,fg='darkblue')
    active_clients_label.pack(side=tk.TOP, padx=10, pady=5)
    active_clients_frame.pack(side=tk.RIGHT, fill=tk.Y,expand=False)

    # chat - in partea stanga
    chat_frame = tk.Frame(main_frame)
    chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    messages_display = tk.Text(chat_frame, state='disabled', wrap='word')
    messages_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    
    send_message_frame = tk.Frame(chat_frame)
    send_message_frame.pack(fill=tk.X, padx=10, pady=5)

    enter_msg_entry = tk.Entry(send_message_frame)
    enter_msg_entry.grid(row=0, column=0, sticky="ew", padx=5)

    send_message_button = tk.Button(send_message_frame, text='Send',
                                     command=lambda: send_msg_after_login(enter_msg_entry),fg='purple')
    send_message_button.grid(row=0, column=1, padx=5)

    
    send_message_frame.grid_columnconfigure(0, weight=1)

    def close_chat_window():
        client.send('exit'.encode('ascii'))
        stop_client.set()
        chat_window.quit()
        chat_window.destroy()
        client.close()

    chat_window.protocol("WM_DELETE_WINDOW", close_chat_window)
    chat_window.mainloop()


def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(f"{nickname}.txt", 'a') as file:
        file.write(f"[{timestamp}] {message}\n")



client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect_ex(("localhost", 1234))


def receive_message_from_srv():
    
    global active_clients_frame,chat_window,messages_display

    while not stop_client.is_set():
        try: 
            if stop_client.is_set():
                break
            message=client.recv(1024).decode('ascii')
            if not message: 
                break
            
            if message=='the server is closing':
                #client.send('exit'.encode('ascii'))
                stop_client.set()
                tkWindow.quit()
                client.close()
                break
            elif message=='already connected!':
                status_label.config(text='Status: user already connected',fg='red')
                #stop_client.sleep(5)
                #client.send('exit'.encode('ascii'))
                
                stop_client.set()
                tkWindow.quit()
                client.close()
                break
                
            elif message.startswith('login:'):
                if(message=='login:failed'):
                    print('Please enter a valid nickname and password')
                    def delete_entries():
                        nickname_entry.delete(0,tk.END)
                        password_entry.delete(0,tk.END)
                        status_label.config(text='Status: Login failed',fg='red')
                    tkWindow.after(0,delete_entries)
                else:
                    print('login message: ',message)
                    
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
                    #print('lista clientilor:!!!! ',active_users_list)    
                    
                    def update_active_clients():
                        # stergem toate widgeturile din frame pentru a adauga clientii noi 
                        for widget in active_clients_frame.winfo_children():
                            widget.destroy()

                        tk.Label(active_clients_frame,text='Message active clients:', bg="#5D7257", fg='darkblue').pack(anchor="w", padx=10, pady=5)
                        for user in active_users_list:
                            user_label=tk.Label(active_clients_frame, text=user.strip(), bg="#5D7257", fg='darkblue')
                            user_label.pack(anchor="w", padx=10, pady=2)
                            if user!=nickname:
                                user_label.bind("<Button-1>", lambda event, user=user: on_client_click(user))
                    tkWindow.after(0, update_active_clients)


            else:
                #print('am primit mesaj de la srv ')
                log_message(message)
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
    global nickname,password
    nickname = nickname_entry.get()
    password = password_entry.get() 
    print(nickname,password)

    if not nickname or not password:
        
        nickname_entry.delete(0,tk.END)
        password_entry.delete(0,tk.END)
        status_label.config(text='Status: Login failed',fg='red')
        return
    
    try:
        if not stop_client.is_set():
            client.send(nickname.encode('ascii'))
            client.send(password.encode('ascii'))

    except Exception as e:
        print('Error at login ',e)
        return

def write():
    while not stop_client.is_set():
        message= input('')
        if message=='exit':
            print(f'the client {client} is closing')
            client.send('exit'.encode('ascii'))
            stop_client.set()
            client.close()
            tkWindow.quit()
            
            break
        elif message.startswith('message:to:'):
            words=message.split(':')  
            print(words)
            
        else:
            new_message = f'{nickname}: {message}' 
            log_message(new_message)
            
            try:
                client.send(new_message.encode('ascii'))
            except ConnectionAbortedError as e:
                print(f"Connection was aborted while sending message: {e}")
                client.close()
                stop_client.set()
                break
            except:
                
                break




receive_thread = threading.Thread(target=receive_message_from_srv)
receive_thread.start()
# write_thread = threading.Thread(target=write)
# write_thread.start()



def close_app():
    client.send('exit'.encode('ascii'))
    stop_client.set()
    client.close()
    tkWindow.destroy()


tkWindow= tk.Tk()
tkWindow.title('Messenger app')
tkWindow.geometry('400x400')
tkWindow.resizable(True,True)


nickname_label= tk.Label(tkWindow,text='Enter a nickname')
nickname_label.pack(padx=10, pady=5)    

nickname_entry= tk.Entry(tkWindow)

nickname_entry.pack(padx=10, pady=5)

password_label=tk.Label(tkWindow,text='Enter a password')
password_label.pack(padx=10, pady=5)

password_entry=tk.Entry(tkWindow)
password_entry.pack(padx=10, pady=5)

login_button=tk.Button(tkWindow,text='Login',command=login)
login_button.pack(padx=10, pady=5)

status_label=tk.Label(tkWindow,text='Status:',fg='blue')
status_label.pack(padx=10, pady=5)
tkWindow.protocol("WM_DELETE_WINDOW", close_app)

tkWindow.mainloop()
