from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket, mysql.connector, datetime, sys, re, time, threading

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='gab',
        password='',
        database='Skype'
    )
except Exception as e:
    print(e)

flag = False
arret = False  
cmd = ["/stop", "/bye", "/kick", "/ban", "/unban"]
user_conn = {'Conn' :[], 'Username' :[], 'Address' :[], 'Port' :[]}

# Création d'une classe qui hérite de QThread pour gérer la réception des messages
class ReceiverThread(QThread):
    # Signal émis lorsque des messages sont reçus
    message_received = pyqtSignal(str)
    def __init__(self, connexion, server_socket, all_threads):
        super().__init__()
        self.conn = connexion
        self.server_socket = server_socket
        self.all_threads = all_threads

    # La méthode run est appelée lorsque le thread démarre
    def run(self):
        print("ReceiverThread Up")
        global flag, arret
        try:
            while not flag:
                recep = self.conn.recv(1024).decode() #Salon|user/pswd|msg
                message = recep.split("|")

                try:
                    sanction = message[2].split(" ")
                except:
                    pass

                if message[0] == "LOGIN":
                    auth = message[1].split("/")
                    self.find_user(auth, self.conn)

                elif message[0] == 'SIGNUP':
                    signup = message[1].split("/")
                    self.create_user(signup, self.conn)

                else :
                    if message[2] in cmd or sanction[0] in cmd:
                        if message[2] == "/bye":
                            for conn in self.all_threads:
                                if conn != self.conn:
                                    continue
                                else:  # Fermer uniquement la connexion qui a dit "bye"
                                    address = str(self.conn)
                                    conn.close()
                                    self.all_threads.remove(conn)
                            recep = f'{recep}|{address}'
                            self.message_received.emit(recep)
                            break

                        elif message[2] == "/stop":
                            if self.check_admin(auth[0]):
                                print("Arrêt du serveur")
                                reply = "Le serveur va s'arrêter dans 10 secondes"
                                self.sender_thread = SenderThread(f'Serveur| {reply}', self.all_threads)
                                self.sender_thread.start()
                                self.sender_thread.wait()
                                stop = threading.Thread(target=self.__stop, args=[])
                                stop.start()
                            else:
                                print("Pas la permission")
                                recep = "CODE"
                                self.sender_thread = CodeThread(f'{recep}|17|PERMISSION ERROR', self.conn)
                                self.sender_thread.start()
                                self.sender_thread.wait()

                        elif sanction[0] == '/ban' or sanction[0] == "/kick":
                            if self.check_admin(auth[0]):
                                if sanction[0] == "/ban":
                                    try:
                                        sanction_type = "BAN"
                                        user = sanction[1]
                                        date_fin = None
                                        self.new_sanction(user, date_fin, sanction_type, self.conn, sanction[2])
                                    except:
                                        recep = "CODE"
                                        self.sender_thread = CodeThread(f'{recep}|22|ERREUR SYNTAXE', self.conn)
                                        self.sender_thread.start()
                                        self.sender_thread.wait()

                                elif sanction[0] == "/kick":
                                    try :
                                        sanction_type = "KICK"
                                        user = sanction[1]
                                        date_fin = f'{sanction[2]} {sanction[3]}'
                                        self.new_sanction(user, date_fin, sanction_type, self.conn, sanction[4])
                                    except:
                                        recep = "CODE"
                                        self.sender_thread = CodeThread(f'{recep}|22|ERREUR SYNTAXE', self.conn)
                                        self.sender_thread.start()
                                        self.sender_thread.wait()
                            else:
                                print("Pas la permission")
                                recep = "CODE"
                                self.sender_thread = CodeThread(f'{recep}|17|PERMISSION ERROR', self.conn)
                                self.sender_thread.start()
                                self.sender_thread.wait()

                        elif sanction[0] == "/unban":
                            if self.check_admin(auth[0]):
                                print("unban1")
                                try:
                                    user = sanction[1]
                                    self.unban_cmd(user)
                                except:
                                    recep = "CODE"
                                    self.sender_thread = CodeThread(f'{recep}|22|ERREUR SYNTAXE', self.conn)
                                    self.sender_thread.start()
                                    self.sender_thread.wait()
                            else:
                                print("Pas la permission")
                                recep = "CODE"
                                self.sender_thread = CodeThread(f'{recep}|17|PERMISSION ERROR', self.conn)
                                self.sender_thread.start()
                                self.sender_thread.wait()

                    elif not message[2]:
                        print("leave")
                        for conn in self.all_threads:
                            if conn != self.conn:
                                continue
                            else:
                                # Fermer uniquement la connexion qui a dit "bye"
                                conn.close()
                                self.all_threads.remove(conn)

                    else:
                        print(f'User : {message[2]}\n')
                        self.insert_data_to_db(recep)
                        # Émission du signal avec le message reçu
                        recep = f'{recep}|{self.conn}'
                        self.message_received.emit(recep)
            
        except IndexError:
            for conn in self.all_threads:
                if conn != self.conn:
                    continue
                else:
                    # Fermer uniquement la connexion qui s'est déconnectée.
                    conn.close()
                    self.all_threads.remove(conn)


        print("ReceiverThread ends\n")
    


    def check_admin(self, user):
        msg_query = f"SELECT is_admin FROM user WHERE username = '{user}'"
        cursor = conn.cursor()
        cursor.execute(msg_query)
        
        result = cursor.fetchone()
        is_admin = result[0]
        self.close(cursor)
        if is_admin:
            return True
        else:
            return False

    def check_sanction(self, user):
        try:
            print("check_sanction")
            msg_query = f"SELECT sanction FROM user WHERE username = '{user}'"
            cursor = conn.cursor()
            cursor.execute(msg_query)
            
            result = cursor.fetchone()
            sanction = result[0]

            self.close(cursor)

            if sanction:
                return True
            else:
                return False
        except Exception as e:
            print(f"check sanction: {e}")

    
    
    def new_sanction(self, user, date_fin, sanction_type, code_conn, argument):
        print("new sanction")
        conn_list = []
        if argument == "-a":
            conn_info = user.split("/")
            address = conn_info[0]
            port1 = conn_info[1]
            try:
                indices = [i for i, (port, addr) in enumerate(zip(user_conn['Port'], user_conn['Address'])) if port == port1 and addr == address]
                if indices:
                    index = indices[0]
                    user = user_conn['Username'][index]
                    conn_info2 = user_conn["Conn"][index]

                else:
                    print(1)
                    reply = f"CODE|22|ERREUR DE SYNTAXE"
                    self.send_code(reply, code_conn)
                    return
            except:
                print(2)
                reply = f"CODE|22|ERREUR DE SYNTAXE"
                self.send_code(reply, code_conn)
                return

        elif argument == '-p':
            for i, username in enumerate(user_conn['Username']):
                if username == user:
                    conn_list.append(user_conn['Conn'][i])

            print(conn_list)
            pass

        else:
            print(3)
            reply = f"CODE|22|ERREUR DE SYNTAXE"
            self.send_code(reply, code_conn)
            return

        
        if self.check_user_exists(user):
            print("user_exists")
            print("try")
            if sanction_type == "BAN":
                print("ban")
                try:
                    sanction_query = f"INSERT INTO sanction (type, date_sanction, date_fin, user) VALUES ('BAN', NOW(), NULL, '{user}')"
                    cursor = conn.cursor()
                    cursor.execute(sanction_query)
                    conn.commit()
                    self.close(cursor) 

                    sanction_query = f"UPDATE user SET sanction = 1 WHERE username = '{user}'"
                    cursor = conn.cursor()
                    cursor.execute(sanction_query)
                    conn.commit()
                    self.close(cursor)

                    reply = f"CODE|25|BAN SUCCESS"
                    if argument == "-p":
                        for con in conn_list:
                            self.send_code(reply, con)

                    else:
                        self.send_code(reply, conn_info2)

                except mysql.connector.Error as err:
                    if err.errno == 1064:
                        print(4)
                        reply = f"CODE|22|ERREUR DE SYNTAXE"
                        self.send_code(reply, code_conn)
                        return

                    if err.errno == 1062:
                        print(6)
                        reply = f"CODE|23|SANCTION DEJA MISE"
                        self.send_code(reply, code_conn)
                        return
                    
                    else:
                        print(7.5)
                        return
            elif sanction_type == "KICK":
                print("kick")
                try:
                    sanction_query = f"INSERT INTO sanction (type, date_sanction, date_fin, user) VALUES ('KICK', NOW(), DATE_ADD(NOW(), INTERVAL {date_fin}), '{user}')"
                    cursor = conn.cursor()
                    cursor.execute(sanction_query)
                    conn.commit()
                    self.close(cursor) 

                    sanction_query = f"UPDATE user SET sanction = 1 WHERE username = '{user}'"
                    cursor = conn.cursor()
                    cursor.execute(sanction_query)
                    conn.commit()
                    self.close(cursor)

                    reply = f"CODE|24|KICK SUCCESS"

                    if argument == "-p":
                        for con in conn_list:
                            self.send_code(reply, con)

                    else:
                        self.send_code(reply, conn_info2)
                    

                except mysql.connector.Error as err:
                    if err.errno == 1064:
                        print(4)
                        reply = f"CODE|22|ERREUR DE SYNTAXE"
                        self.send_code(reply, code_conn)
                        return

                    if err.errno == 1062:
                        print(6)
                        reply = f"CODE|23|SANCTION DEJA MISE"
                        self.send_code(reply, code_conn)
                        return
                    else:
                        print("Erreur inconnue")
                        return

            else: 
                print("Error sanction")
                return
        else:
            reply = f"CODE|21|UTILISATEUR N'EXISTE PAS (SANCTION)"
            self.send_code(reply, code_conn)


    def check_user_exists(self, user):
        try:
            user_query = f"SELECT * from user where username = '{user}'"
            cursor = conn.cursor()
            cursor.execute(user_query)
            result = cursor.fetchone()

            if result[0]:
                return True
        except:
            return False

    def sanction_type(self, user, code_conn):
        reply = "CODE"
        msg_query = f"SELECT type, date_fin FROM sanction WHERE user = '{user}'"
        cursor = conn.cursor()
        cursor.execute(msg_query)
        
        result = cursor.fetchone()
        sanction_type = result[0]
        date_fin = result[1]
        self.close(cursor)
        if sanction_type == "BAN":
            reply = f"{reply}|19|BAN USER"
            self.send_code(reply, code_conn)
        elif sanction_type == "KICK":
            if date_fin > datetime.datetime.now():
                reply = f"{reply}|20/{date_fin}|KICK USER"
                self.send_code(reply, code_conn)

            else:
                self.unban(user, code_conn)
        else:
            print("sanction error")
        
    def unban(self, user, code_conn):
        print('unban')
        try:
            unban_query = f"DELETE FROM sanction where user = '{user}'"
            cursor = conn.cursor()
            cursor.execute(unban_query)
            conn.commit()
            self.close(cursor) 
        except Exception as e:
            print(f"unban{e}")

        unban_query = f"UPDATE user SET sanction = 0 WHERE username = '{user}'"
        cursor = conn.cursor()
        cursor.execute(unban_query)
        conn.commit()
        self.close(cursor) 

        reply = f"CODE|1|LOGIN SUCCESS"
        print(f"LOGIN {self.conn}")
        self.send_code(reply, code_conn)
        self.add_dictionnary(user, code_conn)

        try:
            self.historique(code_conn)
            self.users(code_conn)
        except Exception as e:
            print(e)
        
        self.checkroom(user, code_conn)

    def unban_cmd(self, user):
        print("unban cmd")
        try:
            unban_query = f"DELETE FROM sanction where user = '{user}'"
            cursor = conn.cursor()
            cursor.execute(unban_query)
            conn.commit()
            self.close(cursor) 
        except Exception as e:
            print(f"unban{e}")

        unban_query = f"UPDATE user SET sanction = 0 WHERE username = '{user}'"
        cursor = conn.cursor()
        cursor.execute(unban_query)
        conn.commit()

    def create_user(self, signup, code_conn):
        print(signup)
        reply = 'CODE'
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        date_creation = datetime.datetime.now()
        try :
            if signup[3] != signup [4]:
                reply = f"{reply}|5|MDP DIFFERENTS"
                self.send_code(reply, code_conn)

            elif not re.match(email_pattern, signup[2]):
                reply = f"{reply}|6|MAIL BAD FORMAT"
                self.send_code(reply, code_conn)
            
            else :
                try :
                    create_user_query = "INSERT INTO user (username, password, mail, date_creation, alias) VALUES (%s, %s, %s, %s, %s)"
                    cursor = conn.cursor()
                    data = (signup[0], signup[3], signup[2], date_creation, signup[1])
                    cursor.execute(create_user_query, data)
                    conn.commit()
                    
                    self.salon(signup)

                    reply = f"{reply}|4|SIGN UP SUCCESS"
                    self.send_code(reply, code_conn)
                    
                except mysql.connector.Error as err:
                    if err.errno == 1062:  # Numéro d'erreur MySQL pour la violation de contrainte d'unicité
                        reply = f"{reply}|8|USERNAME NON UNIQUE"
                        self.send_code(reply, code_conn)
                    elif err.errno == 3819:
                        reply = f"{reply}|9|CARACTERES NON AUTORISÉS"
                        self.send_code(reply, code_conn)
                    else:
                        print(f"Erreur MySQL : {err}")
        except Exception as e:
            print(e)
            raise "error"

    def salon(self, signup):
        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('Général', NOW(), (SELECT id_user FROM user WHERE username = '{signup[0]}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()

        self.close(cursor)

    def send_code(self, reply, code_conn):
        print(reply)
        self.sender_thread = CodeThread(f'{reply}', code_conn)
        self.sender_thread.start()
        self.sender_thread.wait()

    def find_user(self, auth, code_conn):
        reply = "CODE"
        print(auth)

        try :
            msg_query = f"SELECT * FROM user WHERE username = '{auth[0]}'"
            cursor = conn.cursor()
            cursor.execute(msg_query)
            
            result = cursor.fetchone()
            username = result[1]
            password = result[2]

            self.close(cursor)

            if auth[0] == username or auth[1] == password:
                if auth[0] == username and auth[1] == password:
                    if not self.check_sanction(auth[0]):
                        reply = f"{reply}|1|LOGIN SUCCESS"
                        print(f"LOGIN {self.conn}")
                        self.send_code(reply, code_conn)
                        self.add_dictionnary(auth[0], code_conn)

                        try:
                            self.historique(code_conn)
                            self.users(code_conn)
                        except Exception as e:
                            print(e)
                        
                        self.checkroom(auth[0], code_conn)
                    else:
                        self.sanction_type(auth[0], code_conn)

                elif auth[0] == username and auth[1] != password:
                    reply = f"{reply}|3|ERREUR DE MDP"
                    self.send_code(reply, code_conn)

                else:
                    reply = f"{reply}|2|L'UTILISATEUR N'A PAS ÉTÉ TROUVÉ"
                    self.send_code(reply, code_conn)

        except TypeError:
            reply = f"{reply}|2|L'UTILISATEUR N'A PAS ÉTÉ TROUVÉ"
            self.send_code(reply, code_conn)

    def add_dictionnary(self, user, conn):
        print("add_dictionnary")
        try:
            match = re.search(r"raddr=\('([^']+)', (\d+)\)", str(conn))
        except Exception as e:
            print(e)

        try:
            if match:
                print("match")
                ip_address = match.group(1)
                port = match.group(2)
                conn_info = f"{ip_address} / {port}"

            else:
                print("not match")
                ip_address = "Unknown Address"
                port = "Unknown Port"
                conn_info = "Unknown Conn"
            
            try:
                print("he tried")
                user_conn["Conn"].append(conn)
                user_conn["Username"].append(user)
                user_conn["Address"].append(ip_address)
                user_conn["Port"].append(port)

                print(user_conn)

            except Exception as e:
                print(e)
        except Exception as e:
            print(e)



    def users(self, users_conn):
        nb_users_query = "SELECT MAX(id_user) FROM user"

        cursor = conn.cursor()
        cursor.execute(nb_users_query)
        
        result = cursor.fetchone()
        nb_users = result[0]

        self.close(cursor)
        for id in range(nb_users+1):
            try:
                i = 0
                while i < 5:

                    if i == 0:
                        salon = "Général"
                    elif i == 1:
                        salon = "Blabla"
                    elif i == 2:
                        salon = "Comptabilité"
                    elif i == 3:
                        salon = "Informatique"
                    elif i == 4:
                        salon = "Marketing"
                    
                    i += 1

                    msg_query = f"SELECT user.alias, user.username, acces_salon.user FROM acces_salon JOIN user ON acces_salon.user = user.id_user WHERE acces_salon.nom = '{salon}' AND user.id_user = {id}"
                    cursor = conn.cursor()
                    cursor.execute(msg_query)
                    
                    result = cursor.fetchone()
                    pseudo = result[0]
                    username = result[1]

                    users = f'USERS|{salon}|{pseudo} @{username}'

                    if username is not None:
                        self.send_users(users, users_conn)
                    else: 
                        continue

                    self.close(cursor)
            except:
                continue
        
    
    def send_users(self, users, users_conn):
        self.users_thread = HistoryThread(users, users_conn)
        self.users_thread.start()
        self.users_thread.wait()

    def checkroom(self, username, code_conn):
        print('checkroom')
        msg_query = f"SELECT (SELECT user FROM acces_salon WHERE nom = 'Général' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_general, (SELECT user FROM acces_salon WHERE nom = 'Blabla' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_blabla, (SELECT user FROM acces_salon WHERE nom = 'Comptabilité' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_comptabilite, (SELECT user FROM acces_salon WHERE nom = 'Informatique' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_informatique, (SELECT user FROM acces_salon WHERE nom = 'Marketing' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_marketing"
        cursor = conn.cursor()
        cursor.execute(msg_query)
            
        result = cursor.fetchone()
        self.close(cursor)

        i = 0
        while i < len(result):
            time.sleep(0.02)
            if result[i] is None:
                reply = f"CODE|{10+i}|PAS ACCES SALON"
                self.send_code(reply, code_conn)
                i += 1
            else:
                reply = f"CODE|15|ACCES SALON"
                self.send_code(reply, code_conn)
                i += 1


    def insert_data_to_db(self, recep):
        recep = recep.split("|")
        loggers = recep[1].split("/")

        user_query = f"select id_user from user where username = '{loggers[0]}'"
        cursor = conn.cursor()
        cursor.execute(user_query)
        result = cursor.fetchone()
        user = result[0]

        self.close(cursor)

        date_envoi = datetime.datetime.now()
        salon = recep[0]
        message = recep[2]
        query = "INSERT INTO message (message, user, date_envoi, salon) VALUES (%s, %s, %s, %s)"
        data = (message, user, date_envoi, salon)
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            print(query)

            self.close(cursor)

        except Exception as error:
            print(f"Erreur d'insertion : {error}")

    def send_history(self, history, history_conn):
        self.history_thread = HistoryThread(history, history_conn)
        self.history_thread.start()
        self.history_thread.wait()

    def historique(self, history_conn):
        nb_msg_query = "SELECT MAX(id_message) FROM message"

        cursor = conn.cursor()
        cursor.execute(nb_msg_query)
        
        result = cursor.fetchone()
        nb_messages = result[0]

        self.close(cursor)

        for id in range(nb_messages+1):
            try:
                msg_query = f"SELECT message.message, user.username, message.date_envoi, message.salon, user.alias FROM message JOIN user ON message.user = user.id_user WHERE message.id_message = {id}"
                cursor = conn.cursor()
                cursor.execute(msg_query)
                
                result = cursor.fetchone()
                message = result[0]
                username = result[1]
                date = result[2]
                salon = result[3]
                pseudo = result[4]

                history = f'{salon}|{date.strftime("%H:%M")} - {pseudo} ~~ |{message}'

                self.send_history(history, history_conn)
            except:
                continue
        
            self.close(cursor)

    def close(self, cursor):
        cursor.close()
    
    def __stop(self):
        global flag, arret
        time.sleep(10)
        flag = True
        arret = True
        self.quitter()
        
    def quitter(self):
        for conn in self.all_threads:
            conn.close()
        self.server_socket.close()
        QCoreApplication.instance().quit()


class SenderThread(QThread):
    def __init__(self, reply, all_threads):
        super().__init__()
        self.reply = reply
        self.all_threads = all_threads

    def run(self):
        print("SenderThread Up")
        print(self.reply)
        date = datetime.datetime.now().strftime("%H:%M")
        reply = self.reply.split("|")
        if reply[0] == "Serveur":
            reply = f'Serveur|{date} - {reply[0]} ~~|{reply[1]}'
        else:
            username = reply[1].split("/")

            cursor = conn.cursor()
            get_alias_query = f"SELECT alias FROM user WHERE username = '{username[0]}'"

            cursor.execute(get_alias_query)
            
            result = cursor.fetchone()
            alias = result[0]

            reply = f"{reply[0]}|{date} - {alias} ~~ |{reply[2]}"

            self.close(cursor)
            
        try:
            try:
                #print(self.all_threads)
                for conne in self.all_threads:
                    conne.send(reply.encode())
            except ConnectionRefusedError as error:
                print(error)

            except ConnectionResetError as error:
                print(error)
        except Exception as err:
            print(err)
        
        print("SenderThread ends")

    def close(self, cursor):
        cursor.close()

    def quitter(self):
        QCoreApplication.instance().quit()

class CodeThread(QThread):
    def __init__(self, code, code_conn):
        super().__init__()
        self.code = code
        self.code_conn = code_conn

    def run(self):
        #print("CodeThread Up")
        try:
            try:
                self.code_conn.send(self.code.encode())
            except ConnectionRefusedError as error:
                print(error)

            except ConnectionResetError as error:
                print(error)
        except Exception as err:
            print(err)
    def quitter(self):
        QCoreApplication.instance().quit()

class HistoryThread(QThread):
    def __init__(self, history, history_conn):
        super().__init__()
        self.history = history
        self.history_conn = history_conn

    def run(self):
        #print("HistoryThread Up")
        try:
            try:
                self.history_conn.send(self.history.encode())
            except ConnectionRefusedError as error:
                print(error)

            except ConnectionResetError as error:
                print(error)
        except Exception as err:
            print(err)
        
        #print("HistoryThread ends")

class AcceptThread(QThread):
    def __init__(self, server_socket, log, send, connect):
        super().__init__()
        self.server_socket = server_socket
        self.log = log
        self.send = send
        self.connect = connect
    
    def run(self):
        print("AcceptThread Up")
        global flag, arret
        self.all_threads = []
        try:
            host, port = ('0.0.0.0', 11111)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.listen()
            self.connect.connect(self.sender)
            while not arret:
                print("En attente d'une nouvelle connexion")
                self.conn, self.address = self.server_socket.accept()
                print(f"Nouvelle connexion !")

                self.receiver_thread = ReceiverThread(self.conn, self.server_socket, self.all_threads)
                self.receiver_thread.message_received.connect(self.update_reply)
                self.receiver_thread.message_received.connect(self.send_everyone)      
                self.receiver_thread.start()
                self.all_threads.append(self.conn)
                
            
            else:
                for conn in self.all_threads:
                    conn.close()

                self.server_socket.close()
                print("Socket closed")
                self.quitter()


        except Exception as err:
            print(err)
        
        print("AcceptThread ends")
    
    # Méthode appelée pour mettre à jour l'interface utilisateur avec le message reçu
    def update_reply(self, message):
        print(message)
        message = message.split("|")
        user = message[1].split("/")
        match = re.search(r"raddr=\('([^']+)', (\d+)\)", message[3])

        if match:
            ip_address = match.group(1)
            port = match.group(2)
            conn_info = f"{ip_address} / {port}"

            if message[2] in cmd:
                self.log.append(f"({conn_info}) - {user[0]} s'est deconnecté.")
                return
        else:
            conn_info = "Inconnu"

        self.log.append(f'({message[0]} - {conn_info}) {user[0]} ~~ {message[2]}') 
    
    def listen(self):
        self.server_socket.listen(100)
    
    def sender(self):
        reply = self.send.text()
        self.send.setText("")
        self.sender_thread = SenderThread(f'Serveur| {reply}', self.all_threads)
        self.sender_thread.start()
        self.sender_thread.wait()

    def send_everyone(self, message):
        print(message)
        print(f"Send everyone : {message}")
        commande = message.split("|")
        commande = commande[2]
        if commande in cmd:
            print(12)
            return
        else:
            print(13)
            print(cmd)
            self.sender_thread = SenderThread(message, self.all_threads)
            self.sender_thread.start()
            self.sender_thread.wait()

    def quitter(self):
        QCoreApplication.instance().quit()

# Classe de la fenêtre principale
class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Serveur")
        self.resize(500, 500)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # Création et connexion des widgets
        self.label = QLabel("Logs")
        self.label2 = QLabel("Message Serveur")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.line_edit2= QLineEdit()

        self.countBtn = QPushButton("Envoyer")
        self.btn_quit = QPushButton("Quitter")
        self.dialog = QPushButton("?")

        self.dialog.clicked.connect(self.button_clicked)
        self.btn_quit.clicked.connect(self.quitter)

        # Configuration du layout
        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.label2, 2, 0, 1, 2)
        layout.addWidget(self.text_edit, 1, 0, 1, 2) 
        layout.addWidget(self.line_edit2, 3, 0, 1, 2)
        layout.addWidget(self.countBtn, 4, 0, 1, 2)
        layout.addWidget(self.btn_quit, 5, 0)
        layout.addWidget(self.dialog, 5, 1)

        self.centralWidget.setLayout(layout)

        self.label.setText(f"Log du serveur")
        self.text_edit.setText(f"")

        self.main_thread()

    def main_thread(self):
        log = self.text_edit
        send = self.line_edit2
        connect = self.countBtn.clicked

        self.accept_thread = AcceptThread(self, log, send, connect)
        self.accept_thread.start()


    def button_clicked(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Aide")
        dlg.setText("Centrale du Serveur.")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Question)
        dlg.exec()

    # Méthode appelée lorsqu'on clique sur le bouton Quitter
    def quitter(self):
        global flag, arret
        flag = True
        arret = True
        QCoreApplication.instance().quit()



if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = Window()
        window.show()
        sys.exit(app.exec())

    finally :
        print("Arrêt du serveur")
        

#mysql> ALTER TABLE user ADD CONSTRAINT CK_username_chars CHECK (username NOT REGEXP "[#&%']");
#mysql> ALTER TABLE sanction ADD CONSTRAINT uc_user UNIQUE (user);
