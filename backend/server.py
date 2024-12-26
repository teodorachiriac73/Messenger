import socket

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind(("localhost", 1234))
server.listen(5)
client,addr=server.accept()



done=False

while not done:
    msg=client.recv(1024).decode('utf-8')

    if(msg=="exit"):
        done=True
        client.send("server closed".encode('utf-8'))
    else: print(msg)
    client.send(input("Mesaj: ").encode('utf-8'))


client.close()
server.close()