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

flag = True
def main():
    while flag:

        host = '0.0.0.0'

        server_socket = socket.socket()

        server_socket.bind((host, 1111))

        server_socket.listen(1)

        conn, address = server_socket.accept()

        t1 = threading.Thread (target=reception, args=[conn, server_socket])

        t1.start()

        t1.join()

        conn.close()

if __name__ == '__main__':
    main()
