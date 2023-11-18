import sys
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

import socket

# Création d'une classe qui hérite de QThread pour gérer la réception des messages
class ReceiverThread(QThread):
    # Signal émis lorsque des messages sont reçus
    message_received = pyqtSignal(str)

    # La méthode run est appelée lorsque le thread démarre
    def run(self):
        flag = True
        conn, address = server_socket.accept()
        while flag:
            recep = conn.recv(1024).decode()
            if recep == "arret":
                print("Arret du serveur")
                server_socket.close()
                flag = False
            elif not recep:
                continue
            else:
                print(f'User : {recep}\n')
                # Émission du signal avec le message reçu
                self.message_received.emit(recep)

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
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.line_edit = QLineEdit()
        self.countBtn = QPushButton("Envoyer")
        self.btn_quit = QPushButton("Quitter")

        self.line_edit.setEnabled(False)
        self.btn_quit.clicked.connect(self.quit)

        # Configuration du layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.countBtn)
        layout.addWidget(self.btn_quit)

        self.centralWidget.setLayout(layout)

        self.label.setText(f"Log du serveur")

        self.line_edit.setText(f"")
        
        # Instanciation du thread de réception et connexion du signal, 
        # ReceiverThread possède toutes les caractéristiques d'un thread, car il hérite de la classe QThread.
        self.receiver_thread = ReceiverThread()
        self.receiver_thread.message_received.connect(self.update_reply)
        self.receiver_thread.start()

    # Méthode appelée pour mettre à jour l'interface utilisateur avec le message reçu
    def update_reply(self, message):
        self.line_edit.setText(message)

    # Méthode appelée lorsqu'on clique sur le bouton Quitter
    def quit(self):
        sender = self.sender()
        if sender is self.btn_quit:
            #je sais pas si c'est nécessaire mais ça arrête le thread normalement
            self.receiver_thread.terminate()
            sys.exit(app.exec())


# Configuration du socket serveur
host, port = ('0.0.0.0', 1111)
server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

# Configuration de l'application PyQt
app = QApplication(sys.argv)
window = Window()
window.show()

sys.exit(app.exec())
