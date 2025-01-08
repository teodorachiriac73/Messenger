import ssl
import socket
import os 
import threading
import base64
from file_manipulation import delete_client_folder,return_client_files,save_file
from create_sockets import create_ssl_server_socket 


server = create_ssl_server_socket() 

clients = []
info_about_clients=[]
id_current_client=0
stop_server = threading.Event()

def return_active_clients():
    """
    Iterates over the list of informations about clients and returns the active clients.
    """
    active_clients=[]
    for info_client in info_about_clients:
        if info_client['active']==True:
            active_clients.append(info_client)
    return active_clients

def write_command_in_terminal():
    """
    This function reads the input from the terminal.
    If the input is 'exit', it will close the server and delete the resources.
    """
    while not stop_server.is_set():
        message = input()
        if message == 'exit':
            print("Server is shutting down...")
            
            for active_client in return_active_clients():
                client=active_client['client_socket']
                client.send('the server is closing'.encode('utf-8'))
                client.close()
            info_about_clients.clear()
            delete_client_folder()
            stop_server.set()
            server.close()
            return
        
            

def handle_one_client(client):
    """
    While server is running, it will receive messages from the client.
    Cases: 
    - if the message is 'exit', it will close the connection with the client.
    - if the message is 'file:from:...', it will save the file in the 'clients' folder coresponding to the client.
    - if the message is 'message:from:...', it will send the message to the specified client in private.
    - otherwise, broadcast the message to all clients. 
    """

    while not stop_server.is_set():
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:  
                raise Exception("Empty message, probably client disconnected unexpectedly")
            if message == "exit":
                print("A client requested to disconnect.")
                
                client.close()
                for info_client in info_about_clients:
                    if info_client['client_socket']==client:
                        info_client['active']=False   
                
                broadcast_message(f'one client has left')
                break
                
            if message.startswith("file:from:"):
                arguments = message.split(':')
                sender = arguments[2]
                receiver = arguments[4]
                file_name = arguments[5]
                if "done" in message:
                    print(f"Fisierul {file_name} a fost primit complet.")
                else:
                    file_data_encoded = arguments[6]

                    file_data = base64.b64decode(file_data_encoded)
                    save_file(sender,receiver,file_name,file_data)
                    

            elif message.startswith("message:from:"):
                from_client=message.split(':')[2]
                to_client=message.split(':')[4]
                actual_message=message.split(':')[5]
                print(from_client,to_client,actual_message)
                send_direct_message_to_user(from_client,to_client,message)
    
            else:
                broadcast_message(message)
        except:
            break

def broadcast_message(message):
    """
    Function that sends a message to all active clients.
    """
    active_users=return_active_clients()
    for one_client in active_users:
            try:
                one_client['client_socket'].send(message.encode('utf-8'))
            except:
                print("eroare trimitere mesaj catre client",one_client)
                one_client['active']=False
                break


def broadcast_active_users():
    """
    Broadcast active users to all clients.
    """
    while not stop_server.is_set():
        active_users=return_active_clients()
        active_users = [user['nickname'] for user in active_users if user['active']==True]  
        broadcast_message(f'active users: {active_users}')
        stop_server.wait(1)

def send_direct_message_to_user(from_client,to_client,message):
    """
    Sends a message from a client to another client. 
    """
    for one_client in info_about_clients:
        if one_client['nickname']==to_client:
            try:
                one_client['client_socket'].send(f'{message}'.encode('utf-8'))
            except:
                print("eroare trimitere mesaj catre client",one_client)
                one_client['active']=False
                break
            break

def authenticate_client_then_start(client):
    """
    After connecting with a client, the client should authenticate with a nickname and a password.
    Cases:
    - if the client is already connected, it will close the connection.
    - if the client is not connected and the password and nickname are correct, it will connect the client.
    - if the client is not connected and the password is incorrect, sends login:failed to client.

    """
    while not stop_server.is_set():
        try:
            global id_current_client
            client_address = client.getpeername()

            client_has_logged_in=False
            existing_client=False
            already_connected=False
            while(client_has_logged_in==False):
                client_nickname=client.recv(1024).decode('utf-8')
                client_password=client.recv(1024).decode('utf-8')
                print(client_nickname,client_password )
                
                for info_client in info_about_clients:
                    if info_client['nickname']==client_nickname and info_client['password']==client_password:
                        if info_client['active']==True:
                            client.send('already connected!'.encode('utf-8'))
                            already_connected=True
                            client.close()
                            break
                        existing_client=True
                        for one_client in clients:
                            if one_client==info_client['client_socket']:
                                one_client= client #actualizam socketul in caz de reconectare
                                break
                        info_client['client_socket'] = client
                        info_client['active']=True
                        client_has_logged_in=True
                        client.send('login:successfull'.encode('utf-8'))
                        break
                    elif info_client['nickname']==client_nickname:
                        existing_client=True
                        client.send('login:failed'.encode('utf-8'))
                        break
                    
                if already_connected==True: 
                    break
                
                if existing_client==False:
                    clients.append(client)
                    id_current_client+=1
                    info_about_clients.append({
                        'client_socket':client,
                        'id':id_current_client,
                        'active':True, 
                        'nickname':client_nickname, 
                        'password':client_password
                    })
                    
                    client.send('login:successfull'.encode('utf-8'))
                    client_has_logged_in=True

            if client_has_logged_in:
                for info_abt_one_client in info_about_clients:
                    if info_abt_one_client['client_socket']==client:
                        id_client= info_abt_one_client['id']
                        break
                broadcast_message(f'client {id_client} with the nickname {client_nickname} has joined ')
                
                print(f'Connected to client {id_client} from his address {client_address}')
                print(f'client {id_client} has the nickname {client_nickname}')
                
                handle_one_client(client)
        except:
            break



def connect_with_one_client():
    """
    This function is used to connect with a client when the server is running.
    A new thread starts for each client that connects to the server.
    """
    while not stop_server.is_set():
        try:
            client,client_address= server.accept()

            connect_client_thread= threading.Thread(target=authenticate_client_then_start, args=(client,))
            connect_client_thread.start()

        except Exception as e:
            if stop_server.is_set():
                break
            print("Error at connecting with client",e, client_address)
            break


write_thread = threading.Thread(target=write_command_in_terminal)
write_thread.start()

active_users= threading.Thread(target= broadcast_active_users)
active_users.start()

print("Server is listening")
connect_with_one_client()
