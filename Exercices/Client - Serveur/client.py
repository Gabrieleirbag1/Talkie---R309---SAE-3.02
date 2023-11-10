import socket 

def main():
    flag = False
    while flag == False:
        message = str(input("User 1 : "))
        host = '127.0.0.1'

        client_socket = socket.socket()

        try :
            client_socket.connect((host, 11111))
        except ConnectionRefusedError as error:
            print(error)
            main()


        client_socket.send(message.encode())

        if message == "bye":
            flag = True

        elif message =="arret":
            flag = True

        else :
            reply = client_socket.recv(1024).decode()
            print(reply)
            client_socket.close()


if __name__ == "__main__":
    try:
        main()
    except ConnectionResetError as error:
        print(error)