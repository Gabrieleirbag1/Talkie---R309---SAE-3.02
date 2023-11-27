import socket 
import threading
import time, sys


def reception(client_socket):
    flag = True
    while flag:
        try:
            reply = client_socket.recv(1024).decode("utf-8")

            if not reply:
                print("Le serveur n'est plus accessible...")
                flag = False
    
            else:
                print(f'Serveur : {reply}')
                
        except ConnectionRefusedError as error:
            print(error)
            main()

        except ConnectionResetError as error:
            print(error)
            main()

        except BrokenPipeError as error:
            print(f'{error} : Wait a few seconds')
            main()
                

host, port = ('127.0.0.1', 11111)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host,port))

def main():
    flag = True
    while flag:
        try :

            t1 = threading.Thread (target=reception, args=[client_socket])
            t1.start()

            message = str(input(">"))
       
            client_socket.send(message.encode())

            if message == "bye":
                print("DÉCONNEXION")
                flag = False

            elif message =="arret":
                flag = False


        except ConnectionRefusedError:
            print("Impossible de se connecter")
            time.sleep(5)


if __name__ == '__main__':
    main()