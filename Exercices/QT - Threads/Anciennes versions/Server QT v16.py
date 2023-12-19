from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
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


window = None
flag = False
arret = False  
cmd = ("/stop", "/bye", "/kick", "/ban", "/unban", "/help", "/get-ip")
user_conn = {'Conn' :[], 'Username' :[], 'Address' :[], 'Port' :[], 'SuperUser': []}

help = "Liste des commandes<br>─────────────────────────────────────────<br>/help (Liste des commandes)<br>/bye (Déconnecte l'utilisateur)<br>─────────────────────────────────────────"
helpadmin = "Liste des commandes<br>─────────────────────────────────────────<br>/help (Liste des commandes)<br>/bye (Déconnecte l'utilisateur)<br><br>───────────────── Admin ─────────────────<br>/ban (Banni un utilisateur):\<br>* [username] -p<br>* [ip/socket_id] -a<br><br>/kick (Exclu un utilisateur):<br>* [username] [int] [SECOND, MINUTE, HOUR, YEAR] -p<br>* [ip/socket_id] [int] [SECOND, MINUTE, HOUR, YEAR] -a<br><br>/get-ip (Permet d'obtenir l'adresse ip d'un utilisateur:<br>* [username]<br><br>/unban (Retire une sanction):<br>* [username]<br><br>/stop (Arrête le serveur)<br>─────────────────────────────────────────"

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

                elif message[0] == 'DEMANDE':
                    self.create_demande(message, self.conn)

                elif message[0] == 'VALIDATE':
                    user = message[1]
                    type = message[2]
                    concerne = f"{message[3]}/{message[5]}"
                    print(message)
                    print(concerne)
                    nom_salon = concerne.split("/")
                    if type == "Salon":
                        if not self.checkroom2(user, nom_salon[0]):
                            self.check_salon_accept(user, concerne)
                        else:
                            reply = f"CODE|29|USER DEJA ACCES AU SALON"
                            self.send_code(reply, self.conn)
                    elif type == "Admin":
                        self.check_admin_accept(user, concerne)
                    else:
                        print("validate error")

                elif message[0] == "DELETE_REPONSE":
                    demandeur = message[1]
                    type = message[2]
                    receveur = message[3]
                    concerne = message[4]
                    validate = message[5]
                    print('DELETE REPONSE')
                    print(message)
                    print(concerne)
                    self.delete_reponse(demandeur, type, receveur, concerne, validate)

                elif message[0] == "PROFIL":
                    self.update_profil(message, self.conn)

                elif message[2] == "" or message[2] == " ": #pas de message vide
                    pass

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

                        elif message[2] == "/help":
                            if self.check_admin(auth[0]):
                                reply = helpadmin
                            else:
                                reply = help
                            self.sender_thread = HistoryThread(f'Serveur| {reply}', self.conn)
                            self.sender_thread.start()
                            self.sender_thread.wait()

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

                        elif sanction[0] == '/ban' or sanction[0] == "/kick" or sanction[0] == "/get-ip":
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

                                elif sanction[0] == "/get-ip":
                                    print(sanction)
                                    try:
                                        print(sanction[1])
                                        user = sanction[1]
                                        self.get_ip(user, self.conn)
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
    
    def get_ip(self, user, code_conn):
        print("get_ip")
        index_conn = user_conn['Username'].index(user)
        address = user_conn['Address'][index_conn]
        port = user_conn['Port'][index_conn]
        reply = f"{address}/{port}"
        print(reply)
        
        self.sender_thread = HistoryThread(f'Serveur| {reply}', code_conn)
        self.sender_thread.start()
        self.sender_thread.wait()

    def update_profil(self, info_profil, code_conn):
        index_conn = user_conn['Conn'].index(code_conn)
        user = user_conn['Username'][index_conn]

        try:
            if info_profil[1] == "Description":
                sanction_query = f"UPDATE user SET description = '{info_profil[2]}' WHERE username = '{user}'"
                cursor = conn.cursor()
                cursor.execute(sanction_query)
                conn.commit()
                self.close(cursor)
            
            elif info_profil[1] == "Photo":
                sanction_query = f"UPDATE user SET photo = '{info_profil[2]}' WHERE username = '{user}'"
                cursor = conn.cursor()
                cursor.execute(sanction_query)
                conn.commit()
                self.close(cursor)

        except Exception as e:
            print(e)


    def notifications(self, code_conn):
        print("notification")
        conn_list = []
        index_conn = user_conn['Conn'].index(code_conn)
        user = user_conn['Username'][index_conn]
        print(user)

        if self.check_admin(user):
            nb_msg_query = f"SELECT * FROM demande where receveur = 'Admin'"

        else:
            nb_msg_query = f"SELECT * FROM demande where receveur = '{user}'"

        cursor = conn.cursor()
        cursor.execute(nb_msg_query)
        
        result = cursor.fetchall()

        self.close(cursor)

        try :
            for i, username in enumerate(user_conn['Username']):
                if username == user:
                    conn_list.append(user_conn['Conn'][i])
        except :
            print("user n'est pas co")
            pass
        print(conn_list)
        print(result)

        i=0
        for i in range(len(result)):
            print("notifs")
            print(result[i])
            print(result[i][7])
            reply = f"DEMANDE|{result[i][3]}|{result[i][1]}|{result[i][5]}|{result[i][2]}|{result[i][6]}/Salon|{result[i][7]}" #username, type, concerne, date
            print(reply)
            i+=1
            
            self.send_history(reply, code_conn)

            print("stop")
    
    def demandes(self, code_conn):
        print("demandes")
        conn_list = []
        index_conn = user_conn['Conn'].index(code_conn)
        user = user_conn['Username'][index_conn]

        nb_msg_query = f"SELECT * FROM demande where demandeur = '{user}'"

        cursor = conn.cursor()
        cursor.execute(nb_msg_query)
        
        result = cursor.fetchall()

        self.close(cursor)

        try :
            for i, username in enumerate(user_conn['Username']):
                if username == user:
                    conn_list.append(user_conn['Conn'][i])
        except :
            print("user n'est pas co")
            pass

        i=0
        for i in range(len(result)):
            print(result[i])
            reply = f"DEMANDELISTE|{result[i][3]}|{result[i][1]}|{result[i][5]}|{result[i][2]}"
            print("envoi") #username, type, concerne, date
            print(reply)
            print(result[i][7])
            
            
            if result[i][7] == 0:
                self.send_history(reply, code_conn)
                print("thisdone")
            i+=1

    def create_demande(self, demande, demande_conn):
        print("create demande real")
        print(demande)
        if demande[2] == "SALON":
            print("SALON")
            self.demande_salon(demande, demande_conn)
        elif demande[2] == "ADMIN":
            self.demande_admin(demande, demande_conn)
        elif demande[2] == "AMI":
            self.demande_ami(demande, demande_conn)
        elif demande[2] == "Reponse":
            print("REPONSE")
            self.demande_reponse(demande, demande_conn)

    def demande_admin(self, demande, code_conn):
        if not self.check_admin(demande[1]):
            self.send_demande_admin(demande[1], code_conn)
        else:
            reply = f"CODE|30|DÉJÀ SUPER USER"
            self.send_code(reply, code_conn)

    def send_demande_admin(self, username, code_conn):
        print("send_demande_admin")
        conn_list = []
        if not self.check_demande(username, "Admin"):
            print("demande checked")
            create_demande_query = f"INSERT INTO demande (type, date_demande, demandeur, receveur, concerne) VALUES ('Admin', NOW(), '{username}', 'Admin', 'Admin')"
            cursor = conn.cursor()
            cursor.execute(create_demande_query)
            conn.commit()
            self.close(cursor)

            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

            reply = f"DEMANDE|{username}|Admin|Admin|{date}|NULL/Salon"#on précise le type de requête DEMANDE
            try :
                for i, is_admin in enumerate(user_conn['SuperUser']):
                    if is_admin == "1":
                        conn_list.append(user_conn['Conn'][i])
                try:
                    for admin_conn in conn_list:
                        print("send admin")
                        print(reply)
                        try:
                            self.send_history(reply, admin_conn)
                            print("send admin fin")
                        except:
                            continue
                except:
                    pass
            except :
                pass

        else:
            reply = f"CODE|28|DEMANDE DÉJÀ FAITE"
            self.send_code(reply, code_conn)

    def check_admin_accept(self, user, admin):
        admin = admin.split("/")
        accept = admin[1]
        conn_list = []
        print(admin)
        if accept == "ACCEPT":
            try :
                for i, username in enumerate(user_conn['Username']):
                    if username == user:
                        conn_list.append(user_conn['Conn'][i])
                try:
                    for admin_conn in conn_list:
                        self.send_new_admin(admin_conn)
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
            self.add_admin(user)
            index = user_conn['Username'].index(user)
            user_conn['SuperUser'][index] = '1'

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
                if not self.checkroom2(user, salon):
                    try:
                        for admin_conn in conn_list:
                            self.send_new_salon(salon, admin_conn)
                            lesalon = [salon]
                            self.new_salon2(user, lesalon)
                    except:
                        pass
                else:
                    continue
            
            self.delete_demande(user, admin)
            self.accept(user, admin)
                
        else:
            self.refuse(user, admin)

    def demande_salon(self, demande, code_conn):
        if not self.checkroom2(demande[1], demande[3]):
            if demande[3] == "Blabla":
                self.new_salon(demande[1], demande[3], code_conn)
            else:
                self.send_demande_salon(demande[1], demande[3], code_conn)
        else:
            reply = f"CODE|26|DÉJÀ ACCES SALON"
            self.send_code(reply, code_conn)

    def demande_reponse(self, demande, code_conn):
        print("demande_reponse")
        reponse = demande[5].split("/")
        if reponse[1] == 'Salon':
            if reponse[0] == "0":
                validate = 0
            elif reponse[0] == "1":
                validate = 1
            create_demande_query = f"INSERT INTO demande (type, date_demande, demandeur, receveur, concerne, validate, reponse) VALUES ('Salon', NOW(), 'Admin', '{demande[1]}', '{demande[3]}', '{validate}', 1)"
            cursor = conn.cursor()
            cursor.execute(create_demande_query)
            conn.commit()
            self.close(cursor)


    def send_demande_salon(self, username, salon, code_conn):
        print("send_demande_salon")
        conn_list = []
        if not self.check_demande(username, salon):
            create_demande_query = f"INSERT INTO demande (type, date_demande, demandeur, receveur, concerne) VALUES ('Salon', NOW(), '{username}', 'Admin', '{salon}')"
            cursor = conn.cursor()
            cursor.execute(create_demande_query)
            conn.commit()
            self.close(cursor)

            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

            reply = f"DEMANDE|{username}|Salon|{salon}|{date}|NULL/Salon"#on précise le type de requête DEMANDE
            try :
                for i, is_admin in enumerate(user_conn['SuperUser']):
                    if is_admin == "1":
                        conn_list.append(user_conn['Conn'][i])
                try:
                    for admin_conn in conn_list:
                        print("send admin")
                        print(reply)
                        self.send_history(reply, admin_conn)
                        print("send admin fin")
                except:
                    pass
            except :
                pass

        else:
            reply = f"CODE|28|DEMANDE DÉJÀ FAITE"
            self.send_code(reply, code_conn)


    def check_demande(self, username, concerne):
        try:
            print(concerne)
            print(username)
            msg_query = f"SELECT * FROM demande WHERE concerne = '{concerne}' AND demandeur = '{username}'"
            cursor = conn.cursor()
            cursor.execute(msg_query)
            result = cursor.fetchone()
            self.close(cursor)
            print(result)

            if result[0]:
                return True
        except:
            return False
            
        
    def checkroom2(self, username, salon):
        try:
            msg_query = f"SELECT user FROM acces_salon WHERE nom = '{salon}' AND user = (SELECT id_user FROM user WHERE username = '{username}')"
            cursor = conn.cursor()
            cursor.execute(msg_query)
                
            result = cursor.fetchone()
            self.close(cursor)

            if result[0]:
                return True
        except:
            return False
        
    def check_salon_accept(self, user, salon):
        salon = salon.split("/")
        salon_nom = salon[0]
        accept = salon[1]
        conn_list = []
        print(salon)
        if accept == "ACCEPT":
            try :
                for i, username in enumerate(user_conn['Username']):
                    if username == user:
                        conn_list.append(user_conn['Conn'][i])
                try:
                    for admin_conn in conn_list:
                        self.send_new_salon(salon_nom, admin_conn)
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
            self.new_salon2(user, salon)
            self.delete_demande(user, salon)
            self.accept(user, salon)
                
        else:
            self.refuse(user, salon)

    def accept(self, user, salon):
        print("accept")
        
        self.delete_demande(user, salon)

        conn_list = []

        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        try :
            for i, username in enumerate(user_conn['Username']):
                if username == user:
                    conn_list.append(user_conn['Conn'][i])

            try:
                for demandeur_conn in conn_list:
                    reply = f"DEMANDE|{user}|Reponse|{salon[0]}|{date}|1/Salon"
                    self.send_code(reply, demandeur_conn)
                print("create demande")
                reply = reply.split("|")
            except:
                pass 
        except :
            pass

        self.create_demande(reply, demandeur_conn)
        print('accepted')

    def delete_reponse(self, demandeur, type, receveur, concerne, validate):
        print("delete_reponse")
        create_user_query = f"DELETE FROM demande WHERE type = '{type}' AND receveur = '{receveur}' AND concerne = '{concerne}' AND VALIDATE = '{validate}' AND reponse = '1' LIMIT 1"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
    
        self.close(cursor)

    def new_salon(self, username, salon, code_conn):
        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('{salon}', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()

        self.send_new_salon(salon, code_conn)

        self.close(cursor)

    def send_new_salon(self, salon, code_conn):
        print("send_new_salon")
        try:
            reply = f"CODE|27/{salon}|ACCES SALON SPÉCIFIQUE"
            self.send_code(reply, code_conn)
        except Exception as e:
            print("nog")
            print(e)

    def send_new_admin(self, code_conn):
        print("send_new_admin")
        try:
            reply = f"CODE|31|NOUVEL ADMIN"
            self.send_code(reply, code_conn)
        except Exception as e:
            print("souk")
            print(e)

    def add_admin(self, user):
        print("add_admin")
        admin_query = f"UPDATE user SET is_admin = 1 WHERE username = '{user}'"
        cursor = conn.cursor()
        cursor.execute(admin_query)
        conn.commit()

        self.close(cursor)


    def new_salon2(self, username, salon):
        print("new salon 2")
        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('{salon[0]}', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()

        self.close(cursor)

    def refuse(self, user, salon):
        print("refuse")
        
        self.delete_demande(user, salon)

        conn_list = []

        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        try :
            for i, username in enumerate(user_conn['Username']):
                if username == user:
                    conn_list.append(user_conn['Conn'][i])

            try:
                for demandeur_conn in conn_list:
                    reply = f"DEMANDE|{user}|Reponse|{salon[0]}|{date}|0/Salon"
                    self.send_code(reply, demandeur_conn)
                print("create demande")
                reply = reply.split("|")
            except:
                pass 
        except :
            pass

        self.create_demande(reply, demandeur_conn)
        print('fact')

    def delete_demande(self, user, salon):
        print("delete_demande")
        create_user_query = f"DELETE FROM demande WHERE demandeur = '{user}' AND concerne = '{salon[0]}'"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
    
        self.close(cursor)

    
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
                        index_conn = user_conn['Conn'].index(conn_info2)
                        user = user_conn['Username'][index_conn]

                        for i, username in enumerate(user_conn['Username']):
                            if username == user:
                                conn_list.append(user_conn['Conn'][i])

                        for con in conn_list:
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
                        index_conn = user_conn['Conn'].index(conn_info2)
                        user = user_conn['Username'][index_conn]

                        for i, username in enumerate(user_conn['Username']):
                            if username == user:
                                conn_list.append(user_conn['Conn'][i])

                        for con in conn_list:
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

            self.close(cursor)
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

    def sanction_type2(self, user):
        reply = "CODE"
        msg_query = f"SELECT type, date_fin FROM sanction WHERE user = '{user}'"
        cursor = conn.cursor()
        cursor.execute(msg_query)
        
        result = cursor.fetchone()
        sanction_type = result[0]
        print(sanction_type)
        date_fin = result[1]
        self.close(cursor)
        if sanction_type == "BAN":
            return True
        elif sanction_type == "KICK":
            return False
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
                            self.notifications(code_conn)
                            self.demandes(code_conn)
                            self.profil(auth[0], code_conn)
                        except:
                            pass

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


    def profil(self, user, code_conn):
        profil_query = f"SELECT * FROM user where username = '{user}'"

        cursor = conn.cursor()
        cursor.execute(profil_query)
        
        result = cursor.fetchone()
        alias = result[5]
        is_admin = result[6]
        mail = result[3]
        description = result[8]
        date = result[4]
        date = date.strftime("%d/%m/%Y %H:%M")
        photo = result[9]

        self.close(cursor)

        reply = f"PROFIL|{user}|{alias}|{mail}|{is_admin}|{description}|{date}|{photo}"
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

                if self.check_admin(user):
                    user_conn["SuperUser"].append("1")
                else:
                    user_conn["SuperUser"].append("0")


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

                    if self.check_admin(username):
                        admin = ' 👑'
                    else:
                        admin = ""
                    if self.check_sanction(username):
                        if self.sanction_type2(username):
                            users = f'USERS|{salon}|{pseudo} @{username}{admin}|ban'
                        else:
                            users = f'USERS|{salon}|{pseudo} @{username}{admin}|kick'
                    else:
                        users = f'USERS|{salon}|{pseudo} @{username}{admin}|free'

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

                history = f'{salon}|{date.strftime("%d/%m/%Y %H:%M")} - {pseudo} ~~ |{message}'

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
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
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
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        try :
            reply = self.history.split("|")
            if reply[0] == "Serveur":
                reply = f'Serveur|{date} - {reply[0]} ~~|{reply[1]}'
                self.history_conn.send(reply.encode())
                return
            else:
                pass
        except:
            pass
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
            self.send.returnPressed.connect(self.sender)
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
    global w
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

        w.start_server.connect(self.main_thread)

    def main_thread(self):
        print("Démarrage du serveur")
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

class Login(QMainWindow):
    signup_window_signal = pyqtSignal()
    start_server = pyqtSignal()
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        self.setupUi()

    def setupUi(self):
        global receiver_thread
        self.setObjectName("Login")
        self.resize(400, 300)

        self.setWindowTitle("Log in - Serveur")

        self.label = QLabel(self)
        self.label.setGeometry(QRect(160, 30, 141, 41))
        self.label.setObjectName("label")
        self.label.setText("Identifiant")

        self.username = QLineEdit(self)
        self.username.setGeometry(QRect(60, 80, 281, 25))
        self.username.setObjectName("lineEdit")
        self.username.returnPressed.connect(self.auth)

        self.label_2 = QLabel(self)
        self.label_2.setGeometry(QRect(160, 130, 141, 41))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Mot de passe")

        self.password = QLineEdit(self)
        self.password.setGeometry(QRect(60, 180, 281, 25))
        self.password.setObjectName("lineEdit_2")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.auth)

        self.signup_button = QPushButton(self)
        self.signup_button.setGeometry(QRect(220, 250, 121, 31))
        self.signup_button.setObjectName("pushButton")
        self.signup_button.setText("Inscrire")
        self.signup_button.clicked.connect(self.first_time)
        self.signup_button.setEnabled(False)

        self.connect_button2 = QPushButton(self)
        self.connect_button2.setGeometry(QRect(60, 250, 121, 31))
        self.connect_button2.setObjectName("pushButton_2")
        self.connect_button2.setText("Connexion")
        self.connect_button2.clicked.connect(self.auth)

    def auth(self):
        global window
        username = self.username.text()
        password = self.password.text()

        if username == 'root':
            if password == "root":
                self.username.setEnabled(False)
                self.password.setEnabled(False)
                self.connect_button2.setEnabled(False)
                self.signup_button.setEnabled(True)
                self.start_server.emit()
                window.show()
            else:
                self.errorbox("B")

    def errorbox(self, code):
        error = QMessageBox()
        error.setWindowTitle("Erreur")
        if code == "B":
            content = "(B) Mot de passe incorrect."
        error.setText(content)
        error.setIcon(QMessageBox.Warning)
        error.exec()

    def first_time(self):
        self.signup_window_signal.emit()

class Sign_up(QMainWindow):
    def __init__(self, parent=None):
        super(Sign_up, self).__init__(parent)

        self.setupUi()

    def setupUi(self):
        global receiver_thread

        self.setObjectName("Sign_up")
        self.resize(432, 593)
        self.setWindowTitle("Sign up")

        font = QFont()
        font.setPointSize(14)

        self.label = QLabel(self)
        self.label.setGeometry(20, 20, 221, 31)
        self.label.setFont(font)
        self.label.setObjectName("label_identifiant")
        self.label.setText("Identifiant")

        self.line_edit = QLineEdit(self)
        self.line_edit.setGeometry(20, 60, 391, 31)
        self.line_edit.setObjectName("lineEdit_identifiant")
        self.line_edit.setMaxLength(45)

        self.label_2 = QLabel(self)
        self.label_2.setGeometry(20, 120, 221, 31)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2_pseudo")
        self.label_2.setText("Pseudo")

        self.line_edit_2 = QLineEdit(self)
        self.line_edit_2.setGeometry(20, 160, 391, 31)
        self.line_edit_2.setObjectName("lineEdit_2_pseudo")
        self.line_edit_2.setMaxLength(20)

        self.label_3 = QLabel(self)
        self.label_3.setGeometry(20, 220, 221, 31)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3_mail")
        self.label_3.setText("Mail")

        self.line_edit_3 = QLineEdit(self)
        self.line_edit_3.setGeometry(20, 260, 391, 31)
        self.line_edit_3.setObjectName("lineEdit_3_mail")
        self.line_edit_3.setMaxLength(320)

        self.label_4 = QLabel(self)
        self.label_4.setGeometry(20, 320, 281, 31)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4_mdp")
        self.label_4.setText("Mot de passe")

        self.line_edit_4 = QLineEdit(self)
        self.line_edit_4.setGeometry(20, 360, 391, 31)
        self.line_edit_4.setText("")
        self.line_edit_4.setObjectName("lineEdit_4_mdp")
        self.line_edit_4.setMaxLength(45)
        self.line_edit_4.setEchoMode(QLineEdit.Password)

        self.label_5 = QLabel(self)
        self.label_5.setGeometry(20, 420, 261, 31)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5_cmdp")
        self.label_5.setText("Confirmer le mot de passe")

        self.line_edit_5 = QLineEdit(self)
        self.line_edit_5.setGeometry(20, 460, 391, 31)
        self.line_edit_5.setObjectName("lineEdit_5_cmdp")
        self.line_edit_5.setMaxLength(45)
        self.line_edit_5.setEchoMode(QLineEdit.Password)

        self.line_edit.returnPressed.connect(self.sign_up)
        self.line_edit_2.returnPressed.connect(self.sign_up)
        self.line_edit_3.returnPressed.connect(self.sign_up)
        self.line_edit_4.returnPressed.connect(self.sign_up)
        self.line_edit_5.returnPressed.connect(self.sign_up)


        self.signup_button = QPushButton(self)
        self.signup_button.setGeometry(QRect(150, 520, 140, 41))
        self.signup_button.setFont(font)
        self.signup_button.setObjectName("pushButton")
        self.signup_button.setText("S'inscrire")
        self.signup_button.clicked.connect(self.sign_up)


    def sign_up(self):
        try:
            username = self.line_edit.text()
            alias = self.line_edit_2.text()
            mail = self.line_edit_3.text()
            mdp = self.line_edit_4.text()
            cmdp = self.line_edit_5.text()
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

            if mdp != cmdp:
                self.errorbox("C")
                return
            
            elif not re.match(email_pattern, mail):
                self.errorbox("F")
                return
            
            self.create_super_user(username, alias, mail, mdp)
            self.successBox("A")
            self.close()

        except mysql.connector.Error as err:
            if err.errno == 1062:  # Numéro d'erreur MySQL pour la violation de contrainte d'unicité
                self.errorbox("D")
            elif err.errno == 3819:
                self.errorbox("E")

    def errorbox(self, code):
        error = QMessageBox()
        error.setWindowTitle("Erreur")
        if code == "C":
            content = "(C) Les mots de passe ne sont pas identiques."
        elif code == "D":
            content = "(D) Les caractères ne sont pas autorisés : %, #, &, '"
        elif code == 'F':
            content = "(F) Le mail ne respect pas le format."
        error.setText(content)
        error.setIcon(QMessageBox.Warning)
        error.exec()

    def successBox(self, code):
        if code == 'A':
            success = QMessageBox(self)
            success.setWindowTitle("Succès")
            content = "Creation du compte super utilisateur réussie !"
            success.setIcon(QMessageBox.Information)
            success.setText(content)
            success.exec()
            self.quitter()
        else:
            self.errorBox(code)

    def quitter(self):
        self.close()

    def create_super_user(self, username, alias, mail, mdp):
        create_user_query = f"INSERT INTO user (username, password, mail, date_creation, alias, is_admin) VALUES ('{username}', '{mdp}', '{mail}', NOW(), '{alias}', '1')"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
        cursor.close()

        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('Général', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
        cursor.close()

        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('Blabla', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
        cursor.close()

        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('Comptabilité', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
        cursor.close()

        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('Informatique', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
        cursor.close()

        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('Marketing', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
        cursor.close()

def show_signup_window():
    global signup_window
    signup_window = Sign_up()
    signup_window.show()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        w = Login()
        w.show()
        window = Window()

        w.signup_window_signal.connect(show_signup_window)

        sys.exit(app.exec())

    finally :
        print("Arrêt du serveur")
        

#mysql> ALTER TABLE user ADD CONSTRAINT CK_username_chars CHECK (username NOT REGEXP "[#&%']");
#mysql> ALTER TABLE sanction ADD CONSTRAINT uc_user UNIQUE (user);
