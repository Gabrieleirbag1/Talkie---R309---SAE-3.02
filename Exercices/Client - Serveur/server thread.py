import socket
import threading
import time

flag = False
arret = False

def reception(conn):
    global flag, arret
    while not flag:
        message = conn.recv(1024).decode()

        if message == "arret" or message == "bye":
            print("Arret du serveur")
            flag = True
            if message == "arret":
                arret = True

        elif not message:
            print("Un client vient de se déconnecter...")
            flag = True
        
        else:
            print(f'User : {message}\n')

    print("Arret de la Thread reception")

def envoi(conn):
    global flag, arret
    while flag == False:
        reply = input(">")
        conn.send(reply.encode())

        if reply == "arret" or reply == "bye":
            flag = True
            if reply == "arret":
                arret = True
    print("Arret de la Thread envoi")


def main():

    host = '0.0.0.0'

    server_socket = socket.socket()

    server_socket.bind((host, 11111))

    server_socket.listen(1)

    while not arret:
        conn, address = server_socket.accept()

        t1 = threading.Thread (target=reception, args=[conn])
        t2 = threading.Thread (target=envoi, args=[conn])

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        conn.close()

        server_socket.close()

if __name__ == '__main__':
    main()
