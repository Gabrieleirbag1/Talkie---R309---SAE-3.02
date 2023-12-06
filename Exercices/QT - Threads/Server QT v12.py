import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket, mysql.connector, datetime


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

                if message[0] != "LOGIN":

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
                        self.message_received.emit(recep)

                else:
                    auth = message[1].split("/")
                    self.find_user(auth, self.conn)
                
        except IndexError:
            for conn in self.all_threads:
                if conn != self.conn:
                    continue
                else:
                    # Fermer uniquement la connexion qui s'est déconnectée.
                    conn.close()
                    self.all_threads.remove(conn)

        print("ReceiverThread ends\n")
    
    def find_user(self, auth, code_conn):
        reply = "CODE"

        try :
            msg_query = f"SELECT * FROM user WHERE username = '{auth[0]}'"
            cursor = conn.cursor()
            cursor.execute(msg_query)
            
            result = cursor.fetchone()
            username = result[1]
            password = result[2]

            if auth[0] == username or auth[1] == password:

                if auth[0] == username and auth[1] == password:
                    reply = f"{reply}|1|SUCCESS"
                    self.sender_thread = CodeThread(f'{reply}', code_conn)
                    self.sender_thread.start()
                    self.sender_thread.wait()

                    try:
                        self.historique(code_conn)
                    except Exception as e:
                        print(e)
                
                elif auth[0] == username and auth[1] != password:
                    reply = f"{reply}|3|ERREUR DE MDP"
                    self.sender_thread = CodeThread(f'{reply}', code_conn)
                    self.sender_thread.start()
                    self.sender_thread.wait()

        except TypeError:
            reply = f"{reply}|2|L'UTILISATEUR N'A PAS ÉTÉ TROUVÉ"
            self.sender_thread = SenderThread(f'{reply}', self.all_threads)
            self.sender_thread.start()
            self.sender_thread.wait()


    def quitter(self):
        for conn in self.all_threads:
            conn.close()
        self.server_socket.close()
        QCoreApplication.instance().quit()

    def insert_data_to_db(self, recep):
        recep = recep.split("|")
        loggers = recep[1].split("/")

        print(f"loggers : {loggers[0]}")

        user_query = f"select id_user from user where username = '{loggers[0]}'"
        cursor = conn.cursor()
        cursor.execute(user_query)
        result = cursor.fetchone()
        user = result[0]

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
        self.sender_thread = HistoryThread(history, history_conn)
        self.sender_thread.start()
        self.sender_thread.wait()

    def historique(self, history_conn):
        nb_msg_query = "SELECT MAX(id_message) FROM message"

        cursor = conn.cursor()
        cursor.execute(nb_msg_query)
        
        result = cursor.fetchone()
        nb_messages = result[0]

        self.close(cursor)

        for id in range(nb_messages+1):
            try:
                msg_query = f"SELECT message.message, user.username, message.date_envoi, message.salon FROM message JOIN user ON message.user = user.id_user WHERE message.id_message = {id}"
                cursor = conn.cursor()
                cursor.execute(msg_query)
                
                result = cursor.fetchone()
                message = result[0]
                username = result[1]
                date = result[2]
                salon = result[3]

                history = f'{salon}|{date.strftime("%H:%M")} - {username} ~~ |{message}'

                self.send_history(history, history_conn)
            except:
                continue
        
            self.close(cursor)

    def close(self, cursor):
        cursor.close()


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
        username = reply[1].split("/")
        reply = f"{reply[0]}|{date} - {username[0]} ~~ |{reply[2]}"
        print(f'LA REPLY{reply}')
        try:
            try:
                print(self.all_threads)
                for conn in self.all_threads:
                    conn.send(reply.encode())
            except ConnectionRefusedError as error:
                print(error)

            except ConnectionResetError as error:
                print(error)
        except Exception as err:
            print(err)
        
        print("SenderThread ends")

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

    def quitter(self):
        QCoreApplication.instance().quit()

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
            self.host = socket.gethostname()
            self.listen()
            self.connect.connect(self.sender)
            while not arret:
                print("En attente d'une nouvelle connexion")
                self.conn, self.address = self.server_socket.accept()
                print(f"Nouvelle connexion de {self.host} !")

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
        self.log.append(f'{self.host}: {message[2]}') 
    
    def listen(self):
        self.server_socket.listen(100)
    
    def sender(self):
        reply = self.send.text()
        self.sender_thread = SenderThread(f'Serveur : {reply}', self.all_threads)
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
        self.resize(250, 150)
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
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.label2, 2, 0)
        layout.addWidget(self.text_edit, 1, 0, 1, 2) 
        layout.addWidget(self.line_edit2, 3, 0)
        layout.addWidget(self.countBtn, 4, 0)
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
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
