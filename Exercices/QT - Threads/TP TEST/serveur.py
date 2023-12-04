#!/usr/bin/env python3
import sys
import socket
import subprocess
import psutil
import platform
import json

# info of the server
host = "127.0.0.1"
port = int(10000)

# uping the server
server_s = socket.socket()
server_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_s.bind((host, port))
server_s.listen()
data = ''
if __name__ == '__main__':
    try:
        while data != ':kill':  # "kill" command shut down the server
            print("waiting !!")
            try:
                conn, address = server_s.accept()
                print("connected !!")
                data = ''
                # "disconnect" command stop the connexion between the server and the client
                while data != ':disconnect' and data != ':kill' and data != ":reset":
                    dataraw = conn.recv(1024)
                    if not dataraw:
                        break
                    data = dataraw.decode()
                    if data == "CPU":  # give the percent of using form each cpu
                        p = psutil.cpu_percent(interval=1, percpu=True)
                        txt = ', '.join(map(str, p))
                        print(p)
                        conn.send(txt.encode())
                    elif data == "RAM":  # give all  info for memoty
                        p = psutil.virtual_memory()._asdict()
                        txt = json.dumps(p)
                        conn.send(txt.encode())
                    elif data == "NAME":  # give the name of the device
                        p = platform.node()
                        print(p)
                        conn.send(p.encode())
                    elif data == "OS":
                        if sys.platform == "linux":  # give the distribution of the device
                            p = platform.freedesktop_os_release(
                            )['PRETTY_NAME'] + platform.release()
                            print(p)
                            conn.send(p.encode())
                        else:
                            p = platform.system() + platform.release()
                            print(p)
                            conn.send(p.encode())
                    elif data == 'IP':
                        if sys.platform == 'linux':  # give ip address
                            p = subprocess.Popen(
                                "ip a | grep inet | grep global | awk '{print $2}'", stdout=subprocess.PIPE, shell=True)
                            outs, errs = p.communicate()
                            txt = outs.decode().rstrip("\r\n")
                            conn.send(txt.encode())
                        elif  sys.platform == 'win32':  
                            conn.send(socket.gethostbyname(socket.gethostname()).encode())
                            hostname=socket.gethostname()   
                            print(socket.gethostbyname(hostname))
                            
                        else:
                            p = subprocess.Popen(
                                "ipconfig getifaddr en1", stdout=subprocess.PIPE, shell=True)
                            outs, errs = p.communicate()
                            txt = outs.decode().rstrip("\r\n")
                            print(txt)
                            conn.send(txt.encode())
                            print(f"E/R: {data}")
                    # execute command in the shell using the argument "data"
                    else:
                        if sys.platform == 'win32':
                            
                            p = subprocess.Popen(data,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="cp850")
                            out= p.stdout.read().rstrip()
                            err= p.stderr.read().rstrip()
                            ret = f"{out}{err}"
                            txt = ret 
                            conn.send(txt.encode())
                        else:
                            p = subprocess.Popen(
                                data, stdout=subprocess.PIPE, shell=True, encoding='utf-8', stderr=subprocess.STDOUT)
                            try:
                                outs, errs = p.communicate(None, 10)
                            except subprocess.TimeoutExpired:
                                print(f"Timeout on command {data}")
                            else:
                                txt = outs.decode().rstrip("\r\n")
                                conn.send(txt.encode())
                                print(f"E/R1: {data}")
                                print(f"E/R: {txt}")


            except ConnectionResetError:
                print("connexion lost")
            except TimeoutError:
                print("time out")
            except BrokenPipeError:
                print("connexion broke")
            finally:
                conn.close()
    except PermissionError:
        print("connexion port is not correct")
    finally:
        server_s.close()
