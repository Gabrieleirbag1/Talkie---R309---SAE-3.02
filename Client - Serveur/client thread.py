import socket 
import threading
import time

def task(i):
    print(f"Task {i} starts")
    time.sleep(1)

def main():
    flag = False
    while flag == False:
        message = str(input("User : "))
        host = '127.0.0.1'

        client_socket = socket.socket()

        try :
            client_socket.connect((host, 11111))
        except ConnectionRefusedError as error:
            return error

        client_socket.send(message.encode())

        if message == "bye":
            print("DÉCONNEXION")
            flag = True

        elif message =="arret":
            flag = True

        else :
            t1 = threading.Thread (target=task, args=[1])
            t1.start()
            reply = client_socket.recv(1024).decode()
            t1.join
            print(reply)
            client_socket.close()


if __name__ == "__main__":
    try:
        main()
    except ConnectionResetError as error:
        print(error)