import socket
import threading
import time

def task(i):
    print(f"Task {i} starts")
    time.sleep(1)


def main():
    reply = "Message reçu\n"
    host = '0.0.0.0'

    server_socket = socket.socket()

    server_socket.bind(('0.0.0.0', 11111))

    server_socket.listen(1)

    flag = True
    while flag:
        start = time.perf_counter()
    #task 1 : réception
        t1 = threading.Thread (target=task, args=[1])
        t1.start()
        conn, address = server_socket.accept()
        message = conn.recv(1024).decode()
        print(f'\nUser : {message}\n')

        t1.join()
        
        end = time.perf_counter()
        print(f"Tasks ended in {round(end - start, 2)} second(s)")

        if message == "arret":
            server_socket.close()
            flag = False
        else :
            conn.send(reply.encode())
            conn.close()


       


if __name__ == "__main__":
    main()


