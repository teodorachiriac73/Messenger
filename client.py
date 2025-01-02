import socket
import select
import threading 
from datetime import datetime

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(f"{nickname}.txt", 'a') as file:
        file.write(f"[{timestamp}] {message}\n")



client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect_ex(("localhost", 1234))

nickname = input("Choose a nickname: ")
password = input("Choose a password: ")


def receive_message_from_srv():
    while True:
        try: 
            message=client.recv(1024).decode('ascii')
            if message=='the server is closing':
                client.close()
                break
            if message=='the client should have a nickname':
                client.send(nickname.encode('ascii'))
            elif  message=='the client should have a password':
                client.send(password.encode('ascii'))
            else:
                #print('am primit mesaj de la srv ')
                log_message(message)
                print(message)

        except:
            print("An error occurred")
            client.close()
            break


def write():
    while True:
        message= input('')
        if message=='exit':
            print(f'the client {client} is closing')
            client.send('exit'.encode('ascii'))
            client.close()
            return
        elif message.startswith('message:to:'):
            words=message.split(':')  
            print(words)
            
        else:
            new_message = f'{nickname}: {message}' 
            log_message(new_message)
            client.send(new_message.encode('ascii'))




receive_thread = threading.Thread(target=receive_message_from_srv)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()
