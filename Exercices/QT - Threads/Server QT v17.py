from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import socket, mysql.connector, datetime, sys, re, time, threading

try: #ouverture de la connexion mysql
    conn = mysql.connector.connect(
        host='localhost', #host
        user='gab', #utilisateur
        password='', #mdp assigné (ici aucun)
        database='Skype' #nom de la db
    )
except Exception as e:
    print(e) #impression de l'éventuelle échec de connexion à la bdd mysql


window = None
flag = False
arret = False  
cmd = ("/stop", "/bye", "/kick", "/ban", "/unban", "/help", "/get-ip") #tuple pour regrouper toutes les commandes
user_conn = {'Conn' :[], 'Username' :[], 'Address' :[], 'Port' :[], 'SuperUser': []} #dictionnaire des connexions : connnexion, adresse liée, port ou socket id lié, nom d'utilisateur, superuser ou non

help = "Liste des commandes<br>─────────────────────────────────────────<br>/help (Liste des commandes)<br>/bye (Déconnecte l'utilisateur)<br>─────────────────────────────────────────"
#liste des commandes pour le /help
helpadmin = "Liste des commandes<br>─────────────────────────────────────────<br>/help (Liste des commandes)<br>/bye (Déconnecte l'utilisateur)<br><br>───────────────── Admin ─────────────────<br>/ban (Banni un utilisateur):\<br>* [username] -p<br>* [ip/socket_id] -a<br><br>/kick (Exclu un utilisateur):<br>* [username] [int] [SECOND, MINUTE, HOUR, YEAR] -p<br>* [ip/socket_id] [int] [SECOND, MINUTE, HOUR, YEAR] -a<br><br>/get-ip (Permet d'obtenir l'adresse ip d'un utilisateur:<br>* [username]<br><br>/unban (Retire une sanction):<br>* [username]<br><br>/stop (Arrête le serveur)<br>─────────────────────────────────────────"
#liste des commandes pour le /help lorsque admin

#Création d'une classe qui hérite de QThread pour gérer la réception des messages
class ReceiverThread(QThread):
    """Cette classe est un Thread qui gère la réception des messages des clients.
    Il y a un Thread par client connecté.

    Attributes:
        conn (str): Variable string, connexion unique du client stocké dans le thread de réception
        server_socket (str): Variable string, socket serveur qui sert à accepter les connexions
        all_threads (list): Variable list, liste de toutes les connexions actuellement connectées au serveur

    Methods:
        run(): La méthode run permet de lancer le QThread de réception de message.

        friends(user, code_conn): Envoie au nouveau client connecté la liste d'amis selon qui il est

        delete_friend(user, code_conn): Supprime la relation amicale entre deux utilisateurs, et envoie aux clients connectés concernés cette modification pour que ce soit mis à jour graphiquement

        user_profil(user, code_conn): Envoie le profl de l'utilisateur sélectionné par le client
        
        stop(all_threads): Arrête le serveur après la commande /stop

        __stop(): Thread qui arrête le serveur en fermant les threads via les variables globales.
        L'utilisation du Thread permet que la communication via socket fonctionne toujours même après la commande d'arrêt.

        private_message(private, code_conn): Ajoute à la base de données un message privé

        send_private(private, code_conn): Envoie les nouveaux messages privés aux clients concernés

        get_ip(user, code_conn): Donne l'ip correspondant au client suite à la commande get-ip

        update_profil(infor_profil, code_conn): Permet la modification du profil d'un utilisateur
        
        notifications(code_conn): Récupère toutes les notifications et les envoient au client concerné
        
        demandes(code_conn): Récupère toutes les demandes et les envoient au client concerné
        
        create_demande(demande, demande_conn): Vérifie le type de demande pour rediriger vers la bonne fonction
        
        demande_ami(demande, code_conn): Vérifie si l'utilisateur a déjà en ami un autre utilisateur
        
        check_ami_accept(user, friend, code_conn): Vérifie si le user concerné a accepté la demande d'ami, selon le cas il renvoie vers une fonction accept/refuse, mets aussi les informations en cas d'accept directement chez les clients.

        demande_admin(demande, code_conn): Vérifie si l'utilisateur demandant les droits admin l'est déjà
        
        send_demande_admin(username, code_conn): Ajoute à la bdd la demande admin et l'envoie aux clients administrateurs connectés
        
        check_admin_accept(user, admin): Vérifie si l'admin a accepté la demande admin, selon le cas il renvoie vers une fonction accept/refuse
        
        demande_salon(demande, code_conn):  Vérifie de quel salon concerne la demande de salon
        
        demande_reponse(demande, code_conn): Ajoute à la bdd une nouvelle "demande" de type réponse
        
        send_demande_salon(username, salon, code_conn):  Ajoute à la bdd la demande salon et l'envoie aux clients administrateurs connectés
        
        check_demande(username, concerne) -> Bool: Vérifie si la demande existe pour ne pas faire de doublons
        
        checkroom2(username, salon) -> Bool: Vérifie si l'utilisateur a accès à un salon précis
        
        check_salon_accept(user, salon): Vérifie si l'admin a accepté la demande salon, selon le cas il renvoie vers une fonction accept/refuse
        
        accept(user, salon): Accept une demande et envoie la réponse positive au client concerné
        
        accept_friend(user, salon): Accept une demande et envoie la réponse positive au client concerné (spécifique aux amis)

        delete_reponse(demandeur, type, receveur, concerne, validate): Supprime la réponse concernant le client demandeur de la BDD.
        
        new_salon(username, salon, code_conn): Ajoute à la BDD un nouvel accès à un salon précis pour un client
        
        send_new_salon(salon, code_conn): Envoie le code succès qui débloque en temps réel chez le client l'accès à un salon

        send_new_user(salon, code_conn): Envoie dans la liste des utilisateurs d'un salon spécifique chez le client, le nouvel utilisateur ayant à présent accès à ce salon
        
        send new_friend(user, friend): Renvoie aux utilisateurs concernés leur nouvel ami (qu'ils sont en fait respectivement) et cherche l'alias correspondant.
        
        send_new_admin(code_conn): Envoie le code succès qui débloque en temps réel chez le client les droits administrateur
        
        add_admin(user): Ajoute les droits administrateur à l'utilisateur concerné dans la BDD
        
        new_friend(username, concerne): Ajoute la nouvelle relation ami à la BDD.

        new_salon2(username, salon): Ajoute à la BDD un nouvel accès à un salon précis pour un client mais ne renvoie pas le code d'accès à l'utilisateur
        
        refuse(user, salon): Envoie au client concerné la réponse négative
        
        refuse(user, salon): Envoie au client concerné la réponse négative (spécifique aux amis)

        delete_demande(user, salon): Supprime la demande suite à une réponse 
        
        check_admin(user): Vérifie si l'utilisateur est admin
        
        check_ami(friend1, friend2): Vérifie si l'utilisateur est ami avec celui a qui il veut faire une demande

        check_sanction(user): Vérifie si l'utilisateur a une sanction
        
        new_sanction(user, date_fin, sanction_type, code_conn, argument): Crée une sanction de type kick ou ban, en vérifiant l'argument (-a, -p) de la commande. 
        Renvoie ensuite cette sanction au clients connectés concernés. Gère les codes d'erreur également et les renvoient.

        check_user_exists(user) -> Bool: Vérifie si l'utilisateur existe lors d'une inscription d'un client.

        sanction_type(user, code_conn): Vérifie le type de sanction pour l'envoyer au client qui tente de se log.

        sanction_type2(user) -> Bool: Vérifie le type de sanction sans renvoyer de code.

        unban(user, code_conn): APRÈS UN KICK TEMPORAIRE - Supprime la sanction assigné à un utilisateur dans la BDD, et envoie la code de connexion à l'utilisateur.

        unban_cmd(user, user): APRÈS LA COMMANDE /unban - Supprime la sanction assigné à un utilisateur dans la BDD, et envoie la code de connexion à l'utilisateur.

        create_user(singup, code_conn): Ajoute l'utilisateur à la BDD en vérifiant si le format est respecté. Renvoie un code de succès ou des codes d'erreurs.

        new_private_user(alias, user, code_conn): Lors de la création d'un utilisateur, ajoute celui-ci à la liste des messages privés des clients connectés.

        salon(signup): Donne l'accès au salon "Général" lors de la création d'un utilisateur, droit par défaut.

        send_code(reply, code_conn): Lance le thread d'envoi spécifique aux codes d'erreur et de succès.

        find_user(auth, code_conn): Fonction majeure qui permet d'abord de récupérer les infos correspondants au user.
        Lance toutes les fonctions nécessaires à l'accès des données du client.

        private(user, code_conn): Sélectionne la liste des messages privés à envoyer au client concerné

        profil(user, code_conn): Envoie les informations du profil du client connecté.

        add_dictionnary(user, conn): Ajoute au dictionnaire la connexion, l'utilisateur, adresse, le port ou id du socket, et enfin si l'utilisateur est super utilisateur ou non.

        users(users_conn): Envoie la liste des utilisateurs existants au client concerné.

        send_users(users, users_conn): Renvoie au thread qui envoie entre autre l'historique des users.

        checkroom(username, code_conn): Lorsqu'un utilisateur se connecte, renvoie des codes correspondant aux droits d'accès aux salons du client.

        insert_data_to_db(recep): Insère les nouveaux messages dans la table message de la BDD.

        send_history(history, history_conn): Renvoie au thread qui envoie entre autre l'historique des messages.

        historique(history_conn): Récupère depuis la BDD l'historique de tous les messages et les envoie 1 par 1 via la fct précédente.

        close(cursor): Ferme la connexion à la BDD.

        quitter(): Ferme toutes les connexions avant de fermer l'instance du programme en cours (la partie graphique).


    """
    #Signal émis lorsque des messages sont reçus
    message_received = pyqtSignal(str)
    def __init__(self, connexion, server_socket, all_threads):
        """Initialise une nouvelle instance de la classe ReceiverThread.

        Args:
            connexion: La valeur initiale est obtenu depuis la classe MainWindow.
            server_socket: La valeur initiale est obtenu depuis la classe AcceptThread.
            all_threads: La valeur initiale est obtenue de la classe AcceptThread.
        """
        super().__init__()
        self.conn = connexion
        self.server_socket = server_socket
        self.all_threads = all_threads

    #La méthode run est appelée lorsque le thread démarre
    def run(self):
        """run(): La méthode run permet de lancer le QThread"""
        print("ReceiverThread Up")
        global flag, arret
        try:
            while not flag:
                recep = self.conn.recv(1024).decode() #Salon|user/pswd|msg
                message = recep.split("|")
                user_profil = recep.split("|")

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
                        self.check_admin_accept(user, concerne, self.conn)

                    elif type == "Ami":
                        print("ami")
                        self.check_ami_accept(user, concerne, self.conn)
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

                elif message[0] == "USER_PROFIL":
                    print(user_profil)
                    self.user_profil(user_profil[1], self.conn)

                elif message[0] == "PRIVATE":
                    print("PRIVATE MESSAGE")
                    self.private_message(message, self.conn)

                elif message[0] == "DELETE_FRIEND":
                    print('DELETE FRIEND')
                    self.delete_friend(message, self.conn)

                elif message[2] == "" or message[2] == " ": #pas de message vide
                    pass

                else :
                    if message[2] in cmd or sanction[0] in cmd:
                        if message[2] == "/bye":
                            for conn in self.all_threads:
                                if conn != self.conn:
                                    continue
                                else:  #Fermer uniquement la connexion qui a dit "bye"
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
                                self.stop(self.all_threads)
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
                                #Fermer uniquement la connexion qui a dit "bye"
                                conn.close()
                                self.all_threads.remove(conn)

                    else:
                        print(f'User : {message[2]}\n')
                        self.insert_data_to_db(recep)
                        #Émission du signal avec le message reçu
                        recep = f'{recep}|{self.conn}'
                        self.message_received.emit(recep)
            
        except IndexError:
            print()
            for conn in self.all_threads:
                if conn != self.conn:
                    continue
                else:
                    #Fermer uniquement la connexion qui s'est déconnectée.
                    conn.close()
                    self.all_threads.remove(conn)

        except ConnectionResetError:
            print("Une connexion réinitalisée a provoquée l'arrêt d'un client.")

        print("ReceiverThread ends\n")

    def delete_friend(self, user, code_conn):
        """delete_friend(user, code_conn): Supprime la relation amicale entre deux utilisateurs, et envoie aux clients connectés concernés cette modification pour que ce soit mis à jour graphiquement"""
        print("delete_reponse")
        conn_list = []
        friend1 = user[1]
        friend2 = user[2]
        print(friend1)
        print(friend2)
        delete_friend_query = f"DELETE FROM friends WHERE friend1 = '{friend1}' AND friend2 = '{friend2}' OR friend1 = '{friend2}' AND friend2 = '{friend1}'"
        cursor = conn.cursor()
        cursor.execute(delete_friend_query)
        conn.commit()
        self.close(cursor)
        
        try :
            for i, username in enumerate(user_conn['Username']):
                if username == friend1:
                    conn_list.append(user_conn['Conn'][i])
            try:
                for friend_conn in conn_list:
                    reply = f"DELETE_FRIEND|{friend1}|{friend2}"
                    self.send_code(reply, friend_conn)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

        try :
            for i, username in enumerate(user_conn['Username']):
                if username == friend2:
                    if conn_list != code_conn:
                        conn_list.append(user_conn['Conn'][i])
            try:
                for friend_conn in conn_list:
                    reply = f"DELETE_FRIEND|{friend2}|{friend1}"
                    self.send_code(reply, friend_conn)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

#FAIRE ENCORE check_ami_accept (VALIDATE) ici et tout ce qui est demande d'ami côté client (format DEMANDE|demandé/demandeur|AMI)
    def friends(self, user, code_conn):
        """friends(user, code_conn): Envoie au nouveau client connecté la liste d'amis selon qui il est"""
        friends_query = f"SELECT * FROM friends where friend1 = '{user}' or friend2 = '{user}'"
        cursor = conn.cursor()
        cursor.execute(friends_query)
        result = cursor.fetchall()
        self.close(cursor)

        print("FREIND")
        print(result)

        for i in range(len(result)):
            friend1 = result[i][1]
            friend2 = result[i][2]
            friend = friend1 if user == friend2 else friend2
            i+=1

            friends_query = f"SELECT alias FROM user where username = '{friend}'"
            cursor = conn.cursor()
            cursor.execute(friends_query)
            resulto = cursor.fetchone()
            alias = resulto[0]
            self.close(cursor)

            reply = f"FRIENDS|{friend}|{alias}" #pour le nouvel ami à la liste
            self.send_code(reply, code_conn)



    def user_profil(self, user, code_conn):
        """
        user_profil(user, code_conn): Envoie le profl de l'utilisateur sélectionné par le client
        """
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

        reply = f"USER_PROFIL|{user}|{alias}|{mail}|{is_admin}|{description}|{date}|{photo}"
        self.send_code(reply, code_conn)
    
    def stop(self, all_threads):
        """
        stop(all_threads): Arrête le serveur après la commande /stop
        """
        reply = "Le serveur va s'arrêter dans 10 secondes"
        self.sender_thread = SenderThread(f'Serveur| {reply}', all_threads)
        self.sender_thread.start()
        self.sender_thread.wait()
        stop = threading.Thread(target=self.__stop, args=[])
        stop.start()

    def __stop(self):
        """
        __stop(): Thread qui arrête le serveur en fermant les threads via les variables globales.
        L'utilisation du Thread permet que la communication via socket fonctionne toujours même après la commande d'arrêt.
        """
        global flag, arret
        time.sleep(10)
        flag = True
        arret = True
        self.quitter()

    def private_message(self, private, code_conn):
        """
        private_message(private, code_conn): Ajoute à la base de données un message privé
        """
        user1 = private[1]
        user2 = private[2]
        contenu = private[3]

        sanction_query = "INSERT INTO private (user1, user2, contenu, date) VALUES ((SELECT id_user FROM user WHERE username = %s), (SELECT id_user FROM user WHERE username = %s), %s, NOW())"
        cursor = conn.cursor()
        data = (user1, user2, contenu)
        cursor.execute(sanction_query, data)
        conn.commit()
        self.close(cursor)

        self.send_private(private, code_conn)

    def send_private(self, private, code_conn):
        """
        send_private(private, code_conn): Envoie les nouveaux messages privés aux clients concernés
        """
        conn_list= []
        user1 = private[1]
        user2 = private[2]
        contenu = private[3]
        reply = f"MSG_PRIVATE|{user1}|{user2}|{contenu}|user1"
        try :
            for i, username in enumerate(user_conn['Username']):
                if username == user2:
                    conn_list.append(user_conn['Conn'][i])
            try:
                for private_conn in conn_list:
                    self.sender_thread = HistoryThread(reply, private_conn)
                    self.sender_thread.start()
                    self.sender_thread.wait()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

        try :
            reply = f"MSG_PRIVATE|{user1}|{user2}|{contenu}|user2"
            print(reply)
            print(user1)
            for i, username in enumerate(user_conn['Username']):
                if username == user1:
                    conn_list.append(user_conn['Conn'][i])
            try:
                for private_conn in conn_list:
                    if private_conn != code_conn:
                        self.sender_thread = HistoryThread(reply, private_conn)
                        self.sender_thread.start()
                        self.sender_thread.wait()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)


    
    def get_ip(self, user, code_conn):
        """
        get_ip(user, code_conn): Donne l'ip correspondant au client suite à la commande get-ip
        """
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
        """
        update_profil(infor_profil, code_conn): Permet la modification du profil d'un utilisateur
        """
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
        """
        notifications(code_conn): Récupère toutes les notifications et les envoient au client concerné
        """
        print("notification")
        conn_list = []
        index_conn = user_conn['Conn'].index(code_conn)
        user = user_conn['Username'][index_conn]
        print(user)

        if self.check_admin(user):
            nb_msg_query = f"SELECT * FROM demande where receveur = 'Admin' OR receveur = '{user}' AND type = 'Ami'"

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
        """
        demandes(code_conn): Récupère toutes les demandes et les envoient au client concerné
        """
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
        """
        create_demande(demande, demande_conn): Vérifie le type de demande pour rediriger vers la bonne fonction
        """
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

    def demande_ami(self, demande, code_conn):
        """
        demande_ami(demande, code_conn): Vérifie si l'utilisateur a déjà en ami un autre utilisateur
        """
        friend1 = demande[1]
        friend2 = demande[3]
        if self.check_user_exists(friend2):
            if not self.check_ami(friend1, friend2):
                self.send_demande_ami(friend1, friend2, code_conn)
            else:
                reply = f"CODE|32|DÉJÀ AMI"
                self.send_code(reply, code_conn)

        else:
            reply = f"CODE|33|UTILISATEUR N'EXISTE PAS (DEMANDE D'AMI)"
            self.send_code(reply, code_conn)

    def check_ami_accept(self, user, friend, code_conn):
        """
        check_ami_accept(user, friend, code_conn): Vérifie si le user concerné a accepté la demande d'ami, selon le cas il renvoie vers une fonction accept/refuse, mets aussi les informations en cas d'accept directement chez les clients
        """
        #friend est bien celui qui a accepté la demande de user
        # ex: Admin et Chap/ACCEPT-REFUSE
        friend = friend.split("/")
        friend_nom = friend[0]
        accept = friend[1]
        conn_list = []
        print(friend)
        ami = [friend_nom]
        if not self.check_ami(user, friend_nom):
            if accept == "ACCEPT":
                self.send_new_friend(user, friend_nom)
                self.new_friend(user, friend_nom)
                self.delete_demande(user, ami)
                self.accept_friend(user, ami)
                    
            else:
                self.refuse_friend(user, ami)
        else:
            reply = f"CODE|32|DÉJÀ AMI"
            self.send_code(reply, code_conn)

    def send_demande_ami(self, friend1, friend2, code_conn):
        """
        send_demande_admin(username, code_conn): Ajoute à la bdd la demande admin et l'envoie aux clients administrateurs connectés
        """
        print("send_demande_ami")
        conn_list = []
        if not self.check_demande_friend(friend2, friend1): 
            print("demande checked")
            create_demande_query = f"INSERT INTO demande (type, date_demande, demandeur, receveur, concerne) VALUES ('Ami', NOW(), '{friend1}', '{friend2}', '{friend2}')" #concerne devient le client demandé en ami
            cursor = conn.cursor()
            cursor.execute(create_demande_query)
            conn.commit()
            self.close(cursor)

            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
           
            reply = f"DEMANDE|{friend1}|Ami|{friend2}|{date}|NULL/Salon"#on précise le type de requête DEMANDE
            try :
                for i, is_admin in enumerate(user_conn['Username']):
                    if is_admin == friend2:
                        conn_list.append(user_conn['Conn'][i])
                try:
                    for admin_conn in conn_list:
                        print("send ami")
                        print(reply)
                        try:
                            self.send_history(reply, admin_conn)
                            print("send ami fin")
                        except:
                            continue
                except:
                    pass
            except :
                pass

        else:
            reply = f"CODE|28|DEMANDE DÉJÀ FAITE"
            self.send_code(reply, code_conn)

    def demande_admin(self, demande, code_conn):
        """
        demande_admin(demande, code_conn): Vérifie si l'utilisateur demandant les droits admin l'est déjà
        """
        if not self.check_admin(demande[1]):
            self.send_demande_admin(demande[1], code_conn)
        else:
            reply = f"CODE|30|DÉJÀ SUPER USER"
            self.send_code(reply, code_conn)

    def send_demande_admin(self, username, code_conn):
        """
        send_demande_admin(username, code_conn): Ajoute à la bdd la demande admin et l'envoie aux clients administrateurs connectés
        """
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

    def check_admin_accept(self, user, admin, code_conn):
        """
        check_admin_accept(user, admin): Vérifie si l'admin a accepté la demande admin, selon le cas il renvoie vers une fonction accept/refuse
        """
        admin = admin.split("/")
        accept = admin[1]
        conn_list = []
        print(admin)
        if not self.check_admin(user):
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
        else:            
            reply = f"CODE|34|DÉJÀ ADMIN"
            self.send_code(reply, code_conn)
            

    def demande_salon(self, demande, code_conn):
        """
        demande_salon(demande, code_conn):  Vérifie de quel salon concerne la demande de salon
        """
        if not self.checkroom2(demande[1], demande[3]):
            if demande[3] == "Blabla":
                self.new_salon(demande[1], demande[3], code_conn)
            else:
                self.send_demande_salon(demande[1], demande[3], code_conn)
        else:
            reply = f"CODE|26|DÉJÀ ACCES SALON"
            self.send_code(reply, code_conn)

    def demande_reponse(self, demande, code_conn):
        """
        demande_reponse(demande, code_conn): Ajoute à la bdd une nouvelle "demande" de type réponse
        """
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

        elif reponse[1] == 'Ami':
            if reponse[0] == "0":
                validate = 0
            elif reponse[0] == "1":
                validate = 1
            create_demande_query = f"INSERT INTO demande (type, date_demande, demandeur, receveur, concerne, validate, reponse) VALUES ('Ami', NOW(), '{demande[1]}', '{demande[1]}', '{demande[3]}', '{validate}', 1)"
            cursor = conn.cursor()
            cursor.execute(create_demande_query)
            conn.commit()
            self.close(cursor)

    def send_demande_salon(self, username, salon, code_conn):
        """
        send_demande_salon(username, salon, code_conn):  Ajoute à la bdd la demande salon et l'envoie aux clients administrateurs connectés
        """
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
        """
        check_demande(username, concerne) -> Bool: Vérifie si la demande existe pour ne pas faire de doublons
        """
        try:
            print(concerne)
            print(username)
            msg_query = f"SELECT * FROM demande WHERE concerne = '{concerne}' AND demandeur = '{username}' or concerne = '{username}' AND demandeur = '{concerne}'"
            cursor = conn.cursor()
            cursor.execute(msg_query)
            result = cursor.fetchone()
            self.close(cursor)
            print(result)

            if result[0]:
                return True
        except:
            return False

    def check_demande_friend(self, username, concerne):
        """
        check_demande(username, concerne) -> Bool: Vérifie si la demande existe pour ne pas faire de doublons
        """
        try:
            print(concerne)
            print(username)
            msg_query = f"SELECT * FROM demande WHERE concerne = '{concerne}' demandeur = '{username}' AND reponse = 0 or concerne = '{username}' AND demandeur = '{concerne}' AND reponse = 0"
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
        """
        checkroom2(username, salon) -> Bool: Vérifie si l'utilisateur a accès à un salon précis
        """
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
        """
        check_salon_accept(user, salon): Vérifie si l'admin a accepté la demande salon, selon le cas il renvoie vers une fonction accept/refuse
        """
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
        """
        accept(user, salon): Accept une demande et envoie la réponse positive au client concerné
        """
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

    def accept_friend(self, user, salon):
        """
        accept_friend(user, salon): Accept une demande et envoie la réponse positive au client concerné (spécifique aux amis)
        """
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
                    reply = f"DEMANDE|{user}|Reponse|{salon[0]}|{date}|1/Ami"
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
        """
        delete_reponse(demandeur, type, receveur, concerne, validate): Supprime la réponse concernant le client demandeur de la BDD.
        """
        print("delete_reponse")
        create_user_query = f"DELETE FROM demande WHERE type = '{type}' AND receveur = '{receveur}' AND concerne = '{concerne}' AND VALIDATE = '{validate}' AND reponse = '1' LIMIT 1"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
    
        self.close(cursor)

    def new_salon(self, username, salon, code_conn):
        """
        new_salon(username, salon, code_conn): Ajoute à la BDD un nouvel accès à un salon précis pour un client
        """
        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('{salon}', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()

        self.send_new_salon(salon, code_conn)

        self.close(cursor)

    def send_new_salon(self, salon, code_conn):
        """
        send_new_salon(salon, code_conn): Envoie le code succès qui débloque en temps réel chez le client l'accès à un salon
        """
        print("send_new_salon")
        try:
            reply = f"CODE|27/{salon}|ACCES SALON SPÉCIFIQUE"
            self.send_code(reply, code_conn)
            self.send_new_user(salon, code_conn)
        except Exception as e:
            print(e)
    
    def send_new_user(self, salon, code_conn):
        """send_new_user(salon, code_conn): Envoie dans la liste des utilisateurs d'un salon spécifique chez le client, le nouvel utilisateur ayant à présent accès à ce salon"""
        index_conn = user_conn['Conn'].index(code_conn)
        user = user_conn['Username'][index_conn]

        msg_query = f"SELECT alias FROM user WHERE username = '{user}'"
        cursor = conn.cursor()
        cursor.execute(msg_query)
        result = cursor.fetchone()
        alias = result[0]
        self.close(cursor)

        reply = f"NEW_USER|{salon}|{alias} @{user}"
        self.sender_thread = SenderThread(reply, self.all_threads)
        self.sender_thread.start()
        self.sender_thread.wait()

    
    def send_new_friend(self, user, friend):
        """
        send new_friend(user, friend): Renvoie aux utilisateurs concernés leur nouvel ami (qu'ils sont en fait respectivement) et cherche l'alias correspondant.
        """
        #friend est bien celui qui a accepté la demande de user
        conn_list = []
        msg_query = f"SELECT alias FROM user WHERE username = '{friend}'"
        cursor = conn.cursor()
        cursor.execute(msg_query)
        result = cursor.fetchone()
        alias = result[0]
        self.close(cursor)

        try :
            for i, username in enumerate(user_conn['Username']):
                if username == user:
                    conn_list.append(user_conn['Conn'][i])

            try:
                for demandeur_conn in conn_list:
                    reply = f"NEW_FRIEND|{friend}|{alias}"
                    self.send_code(reply, demandeur_conn)
                print("create demande")
                reply = reply.split("|")
            except:
                pass 
        except :
            pass
        
        conn_list2 = []
        msg_query = f"SELECT alias FROM user WHERE username = '{user}'"
        cursor = conn.cursor()
        cursor.execute(msg_query)
        result = cursor.fetchone()
        alias = result[0]
        self.close(cursor)
        try :
            for i, username in enumerate(user_conn['Username']):
                if username == friend:
                    conn_list2.append(user_conn['Conn'][i])

            try:
                for demandeur_conn in conn_list2:
                    reply = f"NEW_FRIEND|{user}|{alias}"
                    self.send_code(reply, demandeur_conn)
                print("create demande")
                reply = reply.split("|")
            except:
                pass 
        except :
            pass


    def send_new_admin(self, code_conn):
        """
        send_new_admin(code_conn): Envoie le code succès qui débloque en temps réel chez le client les droits administrateur
        """
        print("send_new_admin")
        try:
            reply = f"CODE|31|NOUVEL ADMIN"
            self.send_code(reply, code_conn)
        except Exception as e:
            print("souk")
            print(e)

    def add_admin(self, user):
        """
        add_admin(user): Ajoute les droits administrateur à l'utilisateur concerné dans la BDD
        """
        print("add_admin")
        admin_query = f"UPDATE user SET is_admin = 1 WHERE username = '{user}'"
        cursor = conn.cursor()
        cursor.execute(admin_query)
        conn.commit()

        self.close(cursor)

    def new_friend(self, username, concerne):
        """
        new_friend(username, concerne): Ajoute la nouvelle relation ami à la BDD.
        """
        print("new friend")
        create_friendship_query = f"INSERT INTO friends (friend1, friend2, date) VALUES ('{username}', '{concerne}', NOW())"
        cursor = conn.cursor()
        cursor.execute(create_friendship_query)
        conn.commit()

        self.close(cursor)

        

    def new_salon2(self, username, salon):
        """
        new_salon2(username, salon): Ajoute à la BDD un nouvel accès à un salon précis pour un client mais ne renvoie pas le code d'accès à l'utilisateur
        """
        print("new salon 2")
        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('{salon[0]}', NOW(), (SELECT id_user FROM user WHERE username = '{username}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()

        self.close(cursor)

    def refuse(self, user, salon):
        """
        refuse(user, salon): Envoie au client concerné la réponse négative
        """
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

    def refuse_friend(self, user, salon):
        """
        refuse(user, salon): Envoie au client concerné la réponse négative (spécifique aux amis)
        """
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
                    reply = f"DEMANDE|{user}|Reponse|{salon[0]}|{date}|0/Ami"
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
        """
        delete_demande(user, salon): Supprime la demande suite à une réponse 
        """
        print("delete_demande")
        create_user_query = f"DELETE FROM demande WHERE demandeur = '{user}' AND concerne = '{salon[0]}'"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()
    
        self.close(cursor)

    
    def check_admin(self, user):
        """
        check_admin(user): Vérifie si l'utilisateur est admin
        """
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
        
    def check_ami(self, friend1, friend2):
        """
        check_ami(friend1, friend2): Vérifie si l'utilisateur est ami avec celui a qui il veut faire une demande
        """
        try:
            msg_query = f"SELECT * FROM friends WHERE friend1 = '{friend1}' and friend2 = '{friend2}' or friend1 = '{friend2}' and friend2 = '{friend1}'"
            cursor = conn.cursor()
            cursor.execute(msg_query)
            
            result = cursor.fetchone()
            is_admin = result[0]
            self.close(cursor)
            if is_admin:
                return True
            else:
                return False
        except TypeError:
            return False

    def check_sanction(self, user):
        """
        check_sanction(user): Vérifie si l'utilisateur a une sanction
        """
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
        """
        new_sanction(user, date_fin, sanction_type, code_conn, argument): Crée une sanction de type kick ou ban, en vérifiant l'argument (-a, -p) de la commande. 
        Renvoie ensuite cette sanction au clients connectés concernés. Gère les codes d'erreur également et les renvoient.
        """
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
        """
        check_user_exists(user) -> Bool: Vérifie si l'utilisateur existe lors d'une inscription d'un client.
        """
        try:
            user_query = f"SELECT * FROM user WHERE BINARY username = '{user}'" #binart permet de vérifier même les caractères sensibles à la casse comme les majuscules
            cursor = conn.cursor()
            cursor.execute(user_query)
            result = cursor.fetchone()

            self.close(cursor)
            if result[0]:
                return True
        except:
            return False

    def sanction_type(self, user, code_conn):
        """
        sanction_type(user, code_conn): Vérifie le type de sanction pour l'envoyer au client qui tente de se log.
        """
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
        """
        sanction_type2(user) -> Bool: Vérifie le type de sanction sans renvoyer de code.
        """
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
        """
        unban(user, code_conn): APRÈS UN KICK TEMPORAIRE - Supprime la sanction assigné à un utilisateur dans la BDD, et envoie la code de connexion à l'utilisateur.
        """
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
        """
        unban_cmd(user, user): APRÈS LA COMMANDE /unban - Supprime la sanction assigné à un utilisateur dans la BDD, et envoie la code de connexion à l'utilisateur.
        """
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
        """
        create_user(singup, code_conn): Ajoute l'utilisateur à la BDD en vérifiant si le format est respecté. Renvoie un code de succès ou des codes d'erreurs.
        """
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
                    if signup[0] != "Admin" and signup[0] != "admin":
                        if not re.search(r"\s", signup[0]):
                            create_user_query = "INSERT INTO user (username, password, mail, date_creation, alias) VALUES (%s, %s, %s, %s, %s)"
                            cursor = conn.cursor()
                            data = (signup[0], signup[3], signup[2], date_creation, signup[1])
                            cursor.execute(create_user_query, data)
                            conn.commit()
                            
                            self.salon(signup)

                            reply = f"{reply}|4|SIGN UP SUCCESS"
                            self.send_code(reply, code_conn)

                            self.new_private_user(signup[1], signup[0], code_conn)
                        else:
                            reply = f"{reply}|9|CARACTERES NON AUTORISÉS"
                            self.send_code(reply, code_conn)
                    else:
                        reply = f"{reply}|8|USERNAME NON UNIQUE OU INTERDIT"
                        self.send_code(reply, code_conn)
                        
                except mysql.connector.Error as err:
                    if err.errno == 1062:  #Numéro d'erreur MySQL pour la violation de contrainte d'unicité
                        reply = f"{reply}|8|USERNAME NON UNIQUE OU INTERDIT"
                        self.send_code(reply, code_conn)
                    elif err.errno == 3819:
                        reply = f"{reply}|9|CARACTERES NON AUTORISÉS"
                        self.send_code(reply, code_conn)
                    else:
                        print(f"Erreur MySQL : {err}")
        except Exception as e:
            print(e)
    
    def new_private_user(self, alias, user, code_conn):
        """
        new_private_user(alias, user, code_conn): Lors de la création d'un utilisateur, ajoute celui-ci à la liste des messages privés des clients connectés.
        """
        reply = f"NEW_USER|Général|{alias} @{user}"
        conn_list = []
        for conni in self.all_threads:
            if conni != code_conn:
                conn_list.append(conni)
        self.sender_thread = SenderThread(reply, conn_list)
        self.sender_thread.start()
        self.sender_thread.wait()

    def salon(self, signup):
        """
        salon(signup): Donne l'accès au salon "Général" lors de la création d'un utilisateur, droit par défaut.
        """
        create_user_query = f"INSERT INTO acces_salon (nom, date, user) VALUES ('Général', NOW(), (SELECT id_user FROM user WHERE username = '{signup[0]}'))"
        cursor = conn.cursor()
        cursor.execute(create_user_query)
        conn.commit()

        self.close(cursor)

    def send_code(self, reply, code_conn):
        """
        send_code(reply, code_conn): Lance le thread d'envoi spécifique aux codes d'erreur et de succès.
        """
        print(reply)
        self.sender_thread = CodeThread(f'{reply}', code_conn)
        self.sender_thread.start()
        self.sender_thread.wait()

    def find_user(self, auth, code_conn):
        """
        find_user(auth, code_conn): Fonction majeure qui permet d'abord de récupérer les infos correspondants au user.
        Lance toutes les fonctions nécessaires à l'accès des données du client.
        """
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
                            self.private(auth[0], code_conn)
                            self.friends(auth[0], code_conn)
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

    def private(self, user, code_conn):
        """
        private(user, code_conn): Sélectionne la liste des messages privés à envoyer au client concerné
        """
        private_query = f"""
            SELECT p.*, u1.username AS user1_username, u2.username AS user2_username
            FROM private p
            JOIN user u1 ON p.user1 = u1.id_user
            JOIN user u2 ON p.user2 = u2.id_user
            WHERE u1.username = '{user}' OR u2.username = '{user}'
        """
        cursor = conn.cursor()
        cursor.execute(private_query)
        
        result = cursor.fetchall()

        for i in range(len(result)):
            date = result[i][4].strftime("%d/%m/%Y %H:%M")
            reply = f"PRIVATE|{result[i][5]}|{result[i][6]}|{result[i][3]}|{date}|{user}"
            self.send_history(reply, code_conn)

    def profil(self, user, code_conn):
        """
        profil(user, code_conn): Envoie les informations du profil du client connecté.
        """
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
        """
        add_dictionnary(user, conn): Ajoute au dictionnaire la connexion, l'utilisateur, adresse, le port ou id du socket, et enfin si l'utilisateur est super utilisateur ou non.
        """
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
        """
        users(users_conn): Envoie la liste des utilisateurs existants au client concerné.
        """
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
        """
        send_users(users, users_conn): Renvoie au thread qui envoie entre autre l'historique des users.
        """
        self.users_thread = HistoryThread(users, users_conn)
        self.users_thread.start()
        self.users_thread.wait()

    def checkroom(self, username, code_conn):
        """
        checkroom(username, code_conn): Lorsqu'un utilisateur se connecte, renvoie des codes correspondant aux droits d'accès aux salons du client.
        """
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
        """
        insert_data_to_db(recep): Insère les nouveaux messages dans la table message de la BDD.
        """
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
        """
        send_history(history, history_conn): Renvoie au thread qui envoie entre autre l'historique des messages.
        """
        self.history_thread = HistoryThread(history, history_conn)
        self.history_thread.start()
        self.history_thread.wait()

    def historique(self, history_conn):
        """
        historique(history_conn): Récupère depuis la BDD l'historique de tous les messages et les envoie 1 par 1 via la fct précédente.
        """
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
        """
        close(cursor): Ferme la connexion à la BDD.
        """
        cursor.close()

        
    def quitter(self):
        """
        quitter(): Ferme toutes les connexions avant de fermer l'instance du programme en cours (la partie graphique).
        """
        for conn in self.all_threads:
            conn.close()
        self.server_socket.close()
        QCoreApplication.instance().quit()


class SenderThread(QThread):
    """Cette classe permet d'envoyer de manière "broadcast" des messages aux clients connectés

    Attributes:
        reply (str): Variable string, message qui va être envoyé au client.
        all_threads (list): Variable list, toutes les connexions en cours.

    Methods:
        run(): La méthode run permet de lancer le QThread d'envoi de messages. Cherche également l'alias correspondant au username pour l'envoyer.
        close(cursor): Ferme la connexion à la BDD.

    """
    def __init__(self, reply, all_threads):
        """Initialise une nouvelle instance de la classe SenderThread.

        Args:
            reply: La valeur initiale est obtenue depuis la classe ReceiverThread.
            all_threads: La valeur initiale est obtenue de la classe AcceptThread, mais ici obtenue depuis ReceiverThread.
        """
        super().__init__()
        self.reply = reply
        self.all_threads = all_threads

    #La méthode run est appelée lorsque le thread démarre
    def run(self):
        """
        run(): La méthode run permet de lancer le QThread d'envoi de messages. Cherche également l'alias correspondant au username pour l'envoyer.
        """
        print("SenderThread Up")
        print(self.reply)
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        reply = self.reply.split("|")
        if reply[0] == "Serveur":
            reply = f'Serveur|{date} - {reply[0]} ~~|{reply[1]}'
        elif reply[0] == "NEW_USER":
            reply = f"NEW_USER|{reply[1]}|{reply[2]}"
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
        """
        close(cursor): Ferme la connexion à la BDD.
        """
        cursor.close()

class CodeThread(QThread):
    """Cette classe permet d'envoyer de manière "unicast" des messages au client concerné.

    Attributes:
        code (str): Message qui va être envoyé au client contenant le code d'erreur ou d'accès.
        code_conn (str): Connexion du client concerné.

    Method:
        run(): La méthode run permet de lancer le QThread d'envoi de messages.
    """
    def __init__(self, code, code_conn):
        """Initialise une nouvelle instance de la classe CodeThread.

        Args:
            code: La valeur initiale est obtenue depuis la classe ReceiverThread.
            code_conn: La valeur initiale est obtenue de la classe AcceptThread, mais ici obtenue depuis ReceiverThread.
        """
        super().__init__()
        self.code = code
        self.code_conn = code_conn

    #La méthode run est appelée lorsque le thread démarre
    def run(self):
        """"run(): La méthode run permet de lancer le QThread d'envoi de messages."""
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

class HistoryThread(QThread):
    """Cette classe permet d'envoyer de manière "unicast" des messages au client concerné.

    Attributes:
        history (str): Message qui va être envoyé au client contenant l'historique des messages, utilisateurs, ou message serveur.'
        history_conn (str): Connexion du client concerné.

    Method:
        run(): La méthode run permet de lancer le QThread d'envoi de messages.
    """
    def __init__(self, history, history_conn):
        """Initialise une nouvelle instance de la classe CodeThread.

        Args:
            history: La valeur initiale est obtenue depuis la classe ReceiverThread.
            history_conn: La valeur initiale est obtenue depuis la classe ReceiverThread.
        """
        super().__init__()
        self.history = history
        self.history_conn = history_conn

    #La méthode run est appelée lorsque le thread démarre
    def run(self):
        """
        run(): La méthode run permet de lancer le QThread d'envoi de messages.
        """
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
    """Cette classe permet d'envoyer de manière "unicast" des messages au client concerné.

    Attributes:
        server_socket (str): Variable string correspondant à l'ouverture du socket serveur.
        log (str): Élément string QTextEdit qui permet de stocker les logs du serveurs.
        send (str): Élément string QLineEdit qui permet de rentrer les messages à envoyer aux clients;
        connect (str): Élément string QPushButton qui permet d'envoyer des messages aux clients depuis l'interface serveur.

    Methods:
        run(): La méthode run permet de lancer le QThread d'acceptation de nouveaux clients, qui va ensuite ouvrir les QThread de réception.
        
        update_reply(message): Met à jour grâce un signal présent dans le thread de réception le QTextEdit log du serveur.

        listen(): Permet de définir le temps d'écoute du socket du serveur vis à vis des connexions client.

        sender(): Appel el thread SenderThread pour envoyer un message Serveur aux clients.

        send_everyone(message): Renvoie les messages envoyé par un client à tous les autres clients via un pyQtSignal connecté à cette fonction.
        Vérifie également que le message n'est pas une commande pour ne pas l'enregistrer.

        quitter(): Permet de quitter l'instance du programme
    """
    def __init__(self, server_socket, log, send, connect):
        """Initialise une nouvelle instance de la classe AcceptThread.

        Args:
            server_socket: La valeur initiale est nulle.
            log: La valeur est un QTextEdit de la classe MainWindow.
            send: La valeur est un QLineEdit de la classe MainWindow.
            connect: La valeur est une QPushButton de la classe MainWindow.

        """
        super().__init__()
        self.server_socket = server_socket
        self.log = log
        self.send = send
        self.connect = connect
    
    #La méthode run est appelée lorsque le thread démarre
    def run(self):
        """
        run(): La méthode run permet de lancer le QThread d'acceptation de nouveaux clients, qui va ensuite ouvrir les QThread de réception.
        """
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
    
    #Méthode appelée pour mettre à jour l'interface utilisateur avec le message reçu
    def update_reply(self, message):
        """
        update_reply(message): Met à jour grâce un signal présent dans le thread de réception le QTextEdit log du serveur.
        """
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
        """
        listen(): Permet de définir le temps d'écoute du socket du serveur vis à vis des connexions client.
        """
        self.server_socket.listen(100)
    
    def sender(self):
        """
        sender(): Appel el thread SenderThread pour envoyer un message Serveur aux clients.
        """
        reply = self.send.text()
        date = datetime.datetime.now().strftime("%H%M")
        if reply != "" and reply != " ":
            self.log.append(f"{date} - Serveur ~~ {reply}")
            self.send.setText("")
            self.sender_thread = SenderThread(f'Serveur| {reply}', self.all_threads)
            self.sender_thread.start()
            self.sender_thread.wait()

    def send_everyone(self, message):
        """
        send_everyone(message): Renvoie les messages envoyé par un client à tous les autres clients via un pyQtSignal connecté à cette fonction.
        Vérifie également que le message n'est pas une commande pour ne pas l'enregistrer.
        """
        print(f"Send everyone : {message}")
        commande = message.split("|")
        commande = commande[2]
        if commande in cmd:
            return
        else:
            print(cmd)
            self.sender_thread = SenderThread(message, self.all_threads)
            self.sender_thread.start()
            self.sender_thread.wait()

    def quitter(self):
        QCoreApplication.instance().quit()

class Window(QMainWindow):
    """Cette classe permet d'afficher la fenêtre principale du serveur.

    Methods:
        setupUi(): Affiche les éléments graphiques de la fenêtre.
        main_thread(): Permet de lancer le QThread AcceptThread ouvrant le socket et acceptant les connexions.
        button_clicked(s): Ouvre une fenêtre dialog qui donne des informations sur le serveur.
        quitter(): Méthode appelée lorsqu'on clique sur le bouton Quitter, ferme l'instance du programme.
    """
    global w #classe Login
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        """setupUi(): Affiche les éléments graphiques de la fenêtre."""
        self.setWindowTitle("Serveur")
        self.resize(500, 500)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        #Création et connexion des widgets
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

        #Configuration du layout
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

        w.start_server.connect(self.main_thread) #pyQtSignal permettant de lancer le QThread AcceptThread lors du log in serveur

    def main_thread(self):
        """
        main_thread(): Permet de lancer le QThread AcceptThread ouvrant le socket et acceptant les connexions.
        """
        print("Démarrage du serveur")
        log = self.text_edit
        send = self.line_edit2
        connect = self.countBtn.clicked

        self.accept_thread = AcceptThread(self, log, send, connect)
        self.accept_thread.start()


    def button_clicked(self, s):
        """
        button_clicked(s): Ouvre une fenêtre dialog qui donne des informations sur le serveur.
        """
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Aide")
        dlg.setText("Centrale du Serveur. Vous pouvez envoyez des messages à tous les clients, créer un super utilisateur, obtenir les messages des clients avec leur IP.")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Question)
        dlg.exec()

    def quitter(self):
        global flag, arret
        flag = True
        arret = True
        QCoreApplication.instance().quit()

class Login(QMainWindow):
    """Cette classe permet d'accèder au serveur et de le lancer

    Methods:
        setupUi(): Affiche les éléments graphiques de la fenêtre.
        auth(): Permet si la connexion est juste, d'accéder au serveur.
        errorbox(code): Fenêtre d'erreur si une condition de auth() n'est pas respectée.
        first_time(): Émet un signal qui ouvre la fenêtre d'inscription.


    """
    signup_window_signal = pyqtSignal() #pyQtSignal permettant d'afficher la fenêtre d'inscription
    start_server = pyqtSignal() #permet de lancer le serveur lorsque reçu
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
        else:
            self.errorbox("E")

    def errorbox(self, code):
        error = QMessageBox()
        error.setWindowTitle("Erreur")
        if code == "B":
            content = "(B) Mot de passe incorrect."
        elif code == "E":
            content = "(E) Nom d'utilisateur incorrect"
        error.setText(content)
        error.setIcon(QMessageBox.Warning)
        error.exec()

    def first_time(self):
        self.signup_window_signal.emit()

class Sign_up(QMainWindow):
    """Cette classe permet d'afficher la fenêtre d'inscription d'un super utilisateur.

    Methods:
        setupUi(): Affiche les éléments graphiques de la fenêtre.
        sign_up(): Permet si les conditions sont respectées, d'accéder aux fonctions d'inscription dans la BDD.
        errorbox(self, code): Fenêtre d'erreur de type dialog.
        successBox(self, code): Fenêtre qui affiche le succès de type dialog.
        quitter(): Permet de quitter l'instance du programme.
        create_super_user(self, username, alias, mail, mdp): Ajoute à la BDD le nouveau super utilisateur ainsi que ses droits d'accès aux salons dans la BDD.
        
    """
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
            
            if username != "" and alias != "" and mdp != "":
                if username != "Admin" and username != "admin":
                    if not re.search(r"\s", username):
                        self.create_super_user(username, alias, mail, mdp)
                        self.successBox("A")
                        self.close()
                    else:
                        self.errorbox("G")
                else:
                    self.errorbox("D")

        except mysql.connector.Error as err:
            if err.errno == 1062:  #Numéro d'erreur MySQL pour la violation de contrainte d'unicité
                self.errorbox("D")
            elif err.errno == 3819:
                self.errorbox("G")

    def errorbox(self, code):
        error = QMessageBox()
        error.setWindowTitle("Erreur")
        if code == "C":
            content = "(C) Les mots de passe ne sont pas identiques."
        elif code == "G":
            content = "(G) Les caractères ne sont pas autorisés : %, #, &, ', [espace]"
        elif code == 'F':
            content = "(F) Le mail ne respect pas le format."
        elif code == 'D':
            content = "(D) Le nom d'utilisateur n'est pas unique ou est interdit."
        else:
            content = "Erreur inconnue"
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
            self.errorbox(code)

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
    #Cette méthode permet d'afficher la fenêtre signup grâce à un signal.
    global signup_window
    signup_window = Sign_up()  #instance la classe Sign_up(), fenêtre d'inscription
    signup_window.show()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        w = Login() #instance la classe Login(), fenêtre de connexion
        w.show()
        window = Window() #instance la classe Window(), fenêtre principale du serveur

        w.signup_window_signal.connect(show_signup_window) #affiche la fenêtre d'inscription via le signal émit

        sys.exit(app.exec()) #Éxécute l'application

    finally :
        print("Arrêt du serveur")
        

#mysql> ALTER TABLE user ADD CONSTRAINT CK_username_chars CHECK (username NOT REGEXP "[#&%']");
#mysql> ALTER TABLE sanction ADD CONSTRAINT uc_user UNIQUE (user);
