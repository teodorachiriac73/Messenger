
import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 1234))
server.listen(5)

clients = []
info_about_clients=[]
id_current_client=0
stop_server = threading.Event()

def return_active_clients():
    active_clients=[]
    for info_client in info_about_clients:
        if info_client['active']==True:
            active_clients.append(info_client)
    return active_clients

def write_exit_command():
    while not stop_server.is_set():
        message = input()
        if message == 'exit':
            print("Server is shutting down...")
            
            
            for active_client in return_active_clients():
                client=active_client['client_socket']
                client.send('the server is closing'.encode('ascii'))
                client.close()
            info_about_clients.clear()
            stop_server.set()
            server.close()
            return

def handle_one_client(client):
    while not stop_server.is_set():
        try:
            message = client.recv(1024).decode('ascii')
            if message == "exit":
                print("A client requested to disconnect.")

                client.close()
                info_about_clients[clients.index(client)]['active']=False   
                #clients.remove(client)
                break
            else:
                broadcast_message(message)
        except:
            break

def broadcast_message(message):
    active_users=return_active_clients()
    for one_client in active_users:
            try:
                one_client['client_socket'].send(message.encode('ascii'))
            except:
                print("eroare trimitere mesaj catre client",one_client)


def broadcast_active_users():
    while not stop_server.is_set():
        active_users=return_active_clients()
        active_users = [user['nickname'] for user in active_users if user['active']==True]  
        broadcast_message(f'active users: {active_users}')
        stop_server.wait(5)

def connect_with_client():
    while not stop_server.is_set():
        try:
            global id_current_client
            client, client_address= server.accept()
            id_current_client+=1
            

            client.send('the client should have a nickname'.encode('ascii'))
            client_nickname=client.recv(1024).decode('ascii')
            client.send('the client should have a password'.encode('ascii'))
            client_password=client.recv(1024).decode('ascii')

            clients.append(client)
            info_about_clients.append({'client_socket':client,'id':id_current_client,'active':True, 'nickname':client_nickname, 'password':client_password})

            broadcast_message(f'client {id_current_client} with the nickname {client_nickname} has joined')
            
            print(f'Connected to client {id_current_client} from his address {client_address}')
            print(f'client {id_current_client} has the nickname {client_nickname}')
            client.send('Connected to the server!'.encode('ascii'))
    

            new_thread= threading.Thread(target=handle_one_client, args=(client,))
            new_thread.start()
        except:
            break

write_thread = threading.Thread(target=write_exit_command)
write_thread.start()

active_users= threading.Thread(target= broadcast_active_users)
active_users.start()

print("Server is listening")
connect_with_client()
