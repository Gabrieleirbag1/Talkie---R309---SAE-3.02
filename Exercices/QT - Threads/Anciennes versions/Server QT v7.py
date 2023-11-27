import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket


flag = False
arret = False  

# Création d'une classe qui hérite de QThread pour gérer la réception des messages
class ReceiverThread(QThread):
    # Signal émis lorsque des messages sont reçus
    message_received = pyqtSignal(str)
    def __init__(self, connexion, server_socket):
        super().__init__()
        self.conn = connexion
        self.server_socket = server_socket

    # La méthode run est appelée lorsque le thread démarre
    def run(self):
        print("ReceiverThread Up")
        global flag, arret
        try:
            while not flag:
                recep = self.conn.recv(1024).decode()
                
                if recep == "arret" or recep == "bye":
                    print("Un client se déconnecte")
                    flag = True
                    if recep == "arret":
                        print("Arrêt du serveur")
                        arret = True

                elif not recep:
                    self.conn.close()
                    flag = False

                else:
                    print(f'User : {recep}\n')
                    # Émission du signal avec le message reçu
                    self.message_received.emit(recep)
            
        except Exception as err:
            print(err)

        print("ReceiverThread ends\n")
            
    def quitter(self):
        QCoreApplication.instance().quit()


class SenderThread(QThread):
    def __init__(self, reply, all_threads):
        super().__init__()
        self.reply = reply
        self.all_threads = all_threads

    def run(self):
        print("SenderThread Up")
        print(self.reply)
        try:
            try:
                for conn in self.all_threads:
                    conn.send(self.reply.encode())
            except ConnectionRefusedError as error:
                print(error)

            except ConnectionResetError as error:
                print(error)
        except Exception as err:
            print(err)
        
        print("SenderThread ends")

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

                self.receiver_thread = ReceiverThread(self.conn, self.server_socket)
                self.receiver_thread.message_received.connect(self.update_reply)      
                self.receiver_thread.start()
                self.all_threads.append(self.conn)
   
                #nécessaire sinon à chaque itération de la boucle il y a une nouvelle connexion du bouton à la fonction sender
            
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
        self.log.setText(message)
    
    def listen(self):
        self.server_socket.listen(100)
    
    def sender(self):
        reply = self.send.text()
        self.sender_thread = SenderThread(reply, self.all_threads)
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

        self.line_edit = QLineEdit()
        self.line_edit2= QLineEdit()

        self.countBtn = QPushButton("Envoyer")
        self.btn_quit = QPushButton("Quitter")
        self.dialog = QPushButton("?")

        self.line_edit.setEnabled(False)
        self.dialog.clicked.connect(self.button_clicked)
        self.btn_quit.clicked.connect(self.quitter)

        # Configuration du layout
        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.label2, 2, 0)
        layout.addWidget(self.line_edit, 1, 0)
        layout.addWidget(self.line_edit2, 3, 0)
        layout.addWidget(self.countBtn, 4, 0)
        layout.addWidget(self.btn_quit, 5, 0)
        layout.addWidget(self.dialog, 5, 1)

        self.centralWidget.setLayout(layout)

        self.label.setText(f"Log du serveur")
        self.line_edit.setText(f"")

        self.main_thread()

    def main_thread(self):
        log = self.line_edit
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


# Configuration de l'application PyQt
app = QApplication(sys.argv)
window = Window()
window.show()

sys.exit(app.exec())
