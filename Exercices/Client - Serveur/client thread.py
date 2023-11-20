import socket 
import threading
import time, sys

flag = False
arret = False

def envoi(client_socket):
    global flag, arret
    while flag == False:
        try:
            message = str(input(">"))
       
            client_socket.send(message.encode())

            if message == "arret" or message == "bye":
                print("Arret du serveur")
                flag = True
                arret = True

        except ConnectionRefusedError as error:
            print(error)
            main()

        except ConnectionResetError as error:
            print(error)
            main()
    print("Arret de la Thread envoi")
                

def reception(client_socket):
    global flag, arret
    while not flag:
        try:
            reply = client_socket.recv(1024).decode("utf-8")

            if not reply:
                print("Le serveur n'est plus accessible...")
                flag = True
                arret = True
    
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
    print("Arret de la Thread reception")


def main():
    try :
        host, port = ('127.0.0.1', 11111)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host,port))

        while not arret:
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