import socket 
import threading
import time, sys

class DeconnexionError(Exception):
    pass

def envoi(client_socket):
    flag = False
    while flag == False:
        try:
            message = str(input(">"))
       
            client_socket.send(message.encode())

            if message == "bye":
                print("DÉCONNEXION")
                flag = True
                sys.exit()

            elif message =="arret":
                flag = True
                sys.exit()

        except ConnectionRefusedError as error:
            print(error)
            main()

        except ConnectionResetError as error:
            print(error)
            main()
                

def reception(client_socket):
    flag = True
    while flag:
        reply = client_socket.recv(1024).decode("utf-8")
        if not reply:
            print("Le serveur n'est plus accessible...")
            flag = False
            break
 
        else:
            print(f'Serveur : {reply}')

def main():
    while True:
        try :
            host, port = ('127.0.0.1', 11111)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host,port))

            t1 = threading.Thread (target=reception, args=[client_socket])
            t2 = threading.Thread (target=envoi, args=[client_socket])
            t1.start()
            t2.start()

            t1.join()
            t2.join()

            client_socket.close()

        except ConnectionRefusedError:
            print("Impossible de se connecter")
            time.sleep(5)


if __name__ == '__main__':
    main()