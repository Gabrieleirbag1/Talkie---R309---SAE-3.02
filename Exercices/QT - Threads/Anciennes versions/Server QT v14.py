from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket, mysql.connector, datetime, sys, re, time


conn = mysql.connector.connect(
    host='localhost',
    user='gab',
    password='',
    database='Skype'
)

flag = False
arret = False  


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
                recep = self.conn.recv(1024).decode() #Salon|log/psw|msg
                message = recep.split("|")

                if message[0] == "LOGIN":
                    auth = message[1].split("/")
                    self.find_user(auth, self.conn)

                elif message[0] == 'SIGNUP':
                    signup = message[1].split("/")
                    self.create_user(signup, self.conn)

                else :
                    if message[2] == "arret" or message[2] == "bye":
                        print("Un client se déconnecte")
                        for conn in self.all_threads:
                            if conn != self.conn:
                                continue
                            else:
                                # Fermer uniquement la connexion qui a dit "bye"
                                conn.close()
                                self.all_threads.remove(conn)

                        if message[2] == "arret":
                            print("Arrêt du serveur")
                            arret = True
                            self.quitter()
                    
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
                    reply = f"{reply}|1|LOGIN SUCCESS"
                    print(f"LOGIN {self.conn}")
                    self.send_code(reply, code_conn)

                    try:
                        self.historique(code_conn)
                        self.users(code_conn)
                    except Exception as e:
                        print(e)
                    
                    self.checkroom(auth[0], code_conn)

                elif auth[0] == username and auth[1] != password:
                    reply = f"{reply}|3|ERREUR DE MDP"
                    self.send_code(reply, code_conn)

                else:
                    reply = f"{reply}|2|L'UTILISATEUR N'A PAS ÉTÉ TROUVÉ"
                    self.send_code(reply, code_conn)

        except TypeError:
            reply = f"{reply}|2|L'UTILISATEUR N'A PAS ÉTÉ TROUVÉ"
            self.send_code(reply, code_conn)

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
        msg_query = f"SELECT (SELECT user FROM acces_salon WHERE nom = 'Général' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_general, (SELECT user FROM acces_salon WHERE nom = 'Blabla' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_blabla, (SELECT user FROM acces_salon WHERE nom = 'Comptabilité' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_comptabilite, (SELECT user FROM acces_salon WHERE nom = 'Informatique' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_informatique, (SELECT user FROM acces_salon WHERE nom = 'Marketing' AND user = (SELECT id_user FROM user WHERE username = '{username}')) AS user_marketing"
        cursor = conn.cursor()
        cursor.execute(msg_query)
            
        result = cursor.fetchone()
        self.close(cursor)

        i = 0
        while i < len(result):
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