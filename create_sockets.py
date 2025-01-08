import ssl
import socket

def create_ssl_client_socket():
    
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # dezactiveaza verificarea numelui de gazda 
    context.verify_mode = ssl.CERT_NONE  # nu valideaza certificatul serverului
    client_socket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname='localhost')
    return client_socket


def create_ssl_server_socket():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server_cert.pem", keyfile="server_key.pem")  

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 1234))
    server_socket.listen(5)
    return context.wrap_socket(server_socket, server_side=True)
