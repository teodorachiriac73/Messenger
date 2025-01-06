import socket
import select
import threading 
from datetime import datetime

import tkinter as tk

stop_client= threading.Event()



def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(f"{nickname}.txt", 'a') as file:
        file.write(f"[{timestamp}] {message}\n")



client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect_ex(("localhost", 1234))


def receive_message_from_srv():
    while not stop_client.is_set():
        try: 
            message=client.recv(1024).decode('ascii')
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
                    nickname_entry.delete(0,tk.END) 
                    password_entry.delete(0,tk.END)
                    status_label.config(text='Status: Login failed',fg='red')
                    
                else:
                    print('login message: ',message)
                    
                    status_label.config(text='Status: Login successful',fg='green')
                    nickname_entry.config(state='disabled')
                    password_entry.config(state='disabled')
                    login_button.config(state='disabled')
                    

            else:
                #print('am primit mesaj de la srv ')
                log_message(message)
                print(message)

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

    # if not nickname or not password:
    #     print('Please enter a nickname and a password')
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
write_thread = threading.Thread(target=write)
write_thread.start()



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
