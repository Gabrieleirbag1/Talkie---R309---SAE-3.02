import sys
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import *
import socket

flag = False    
arret = False

# Création d'une classe qui hérite de QThread pour gérer la réception des messages
class ReceiverThread(QThread):
    # Signal émis lorsque des messages sont reçus
    message_received = pyqtSignal(str)

    def __init__(self, connexion):
        super().__init__()
        self.conn = connexion

    # La méthode run est appelée lorsque le thread démarre
    def run(self):
        print("ReceiverThread Up")
        global flag, arret
        #conn, address = server_socket.accept()
        while not flag:
            recep = self.conn.recv(1024).decode()

        if recep == "arret" or recep == "bye":
            print("Arret du serveur")
            flag = True
            if recep == "arret":
                arret = True

            elif not recep:
                flag = False

            else:
                print(f'User : {recep}\n')
                # Émission du signal avec le message reçu
                self.message_received.emit(recep)

        print("ReceiverThread ends")

class SenderThread(QThread):
    def __init__(self, reply, connexion):
        super().__init__()
        self.reply = reply
        self.conn = connexion

    def run(self):
        print("SenderThread Up")
        print(self.reply)
        try:
            self.conn.send(self.reply.encode())         

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)

        print("SenderThread ends")

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
        self.label2 = QLabel("Réponse du Serveur")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.line_edit = QLineEdit()
        self.line_edit2= QLineEdit()

        self.countBtn = QPushButton("Envoyer")
        self.btn_quit = QPushButton("Quitter")
        self.dialog = QPushButton("?")

        self.line_edit.setEnabled(False)
        self.btn_quit.clicked.connect(self.quit)
        self.dialog.clicked.connect(self.button_clicked)
        self.countBtn.clicked.connect(self.sender)

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

        # Configuration du socket serveur
        host, port = ('0.0.0.0', 11111)
        self.server_socket = socket.socket()
        self.server_socket.bind((host, port))
        self.server_socket.listen(100)
        self.conn, self.address = self.server_socket.accept()

        # Instanciation du thread de réception et connexion du signal, 
        # ReceiverThread possède toutes les caractéristiques d'un thread, car il hérite de la classe QThread.
        self.receiver_thread = ReceiverThread(self.conn)
        self.receiver_thread.message_received.connect(self.update_reply)        
        self.receiver_thread.start()
    
    def sender(self):
        reply = self.line_edit2.text()
        self.sender_thread = SenderThread(reply, self.conn)
        self.sender_thread.start()

    def button_clicked(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Aide")
        dlg.setText("Centrale du Serveur.")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Question)
        dlg.exec()

    # Méthode appelée pour mettre à jour l'interface utilisateur avec le message reçu
    def update_reply(self, message):
        self.line_edit.setText(message)

    # Méthode appelée lorsqu'on clique sur le bouton Quitter
    def quit(self):
        sender = self.sender()
        if sender is self.btn_quit:
            #je sais pas si c'est nécessaire mais ça arrête le thread normalement
            self.receiver_thread.terminate()
            self.sender_thread.terminate()
            self.server_socket.close()
            sys.exit(app.exec())




# Configuration de l'application PyQt
app = QApplication(sys.argv)
window = Window()
window.show()

sys.exit(app.exec())
