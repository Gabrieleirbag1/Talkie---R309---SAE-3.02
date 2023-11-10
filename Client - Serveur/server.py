import socket

def main():
    reply = "Message reçu\n"
    host = '0.0.0.0'

    server_socket = socket.socket()

    server_socket.bind(('0.0.0.0', 11111))

    server_socket.listen(1)

    flag = True
    
    while flag == True:
        conn, address = server_socket.accept()
        message = conn.recv(1024).decode()
        print(message)
        if message == "arret":
            server_socket.close()
            flag = False
        else :
            conn.send(reply.encode())
            conn.close()



if __name__ == "__main__":
    main()


