import socket 
import threading
import time, sys


def envoi(client_socket):
    flag = True
    while flag:
        try:
            message = str(input(">"))
       
            client_socket.send(message.encode())

            if message == "bye":
                print("DÉCONNEXION")
                client_socket.close()
                flag = False

            elif message =="arret":
                flag = False

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)
                


def main():
    flag = True
    while flag:
        try :
            host, port = ('127.0.0.1', 11111)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host,port))

            t2 = threading.Thread (target=envoi, args=[client_socket])
            t2.start()

            t2.join()
            flag = False

        except ConnectionRefusedError:
            print("Impossible de se connecter")
            time.sleep(5)


if __name__ == '__main__':
    main()