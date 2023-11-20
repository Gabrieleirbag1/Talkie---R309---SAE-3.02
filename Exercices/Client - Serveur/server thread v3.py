import socket
import threading
import time

def reception(conn, server_socket):
    flag = True
    while flag:
        message = conn.recv(1024).decode()

        if message == "arret":
            print("Arret du serveur")
            server_socket.close()
            flag = False

        elif not message:
            print("Un client vient de se déconnecter...")
            flag = False
        
        else:
            print(f'User : {message}\n')


host = '0.0.0.0'
server_socket = socket.socket()
server_socket.bind((host, 11111))
server_socket.listen(1)


def main():
    flag = True
    while flag:
        conn, address = server_socket.accept()

        t1 = threading.Thread (target=reception, args=[conn, server_socket])
        t1.start()

        reply = input(">")
        conn.send(reply.encode())

        conn.close()


if __name__ == '__main__':
    main()
