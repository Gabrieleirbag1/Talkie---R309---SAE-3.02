import sys
import time
import threading
import socket

from PyQt5.QtCore import QRunnable, Qt, QThreadPool
from PyQt5.QtWidgets import *

class Runnable(QRunnable):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        try:
            print(f"Message envoyé : {self.message}")
    
            client_socket.send(self.message.encode())              

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Client")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create and connect widgets
        self.label = QLabel("Messagerie")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.line_edit = QLineEdit()
        self.btn_quit = QPushButton("Quitter")
        self.countBtn = QPushButton("Envoyer")
        self.dialog = QPushButton("?")

        self.countBtn.clicked.connect(self.runTasks)
        self.btn_quit.clicked.connect(self.quit)
        self.dialog.clicked.connect(self.button_clicked)
        
        # Set the layout
        layout = QGridLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.countBtn)
        layout.addWidget(self.btn_quit, 3, 0)
        layout.addWidget(self.dialog, 3, 1)
        self.centralWidget.setLayout(layout)

    def runTasks(self):
        message = self.line_edit.text()
        self.label.setText(f"Running Threads")
        pool = QThreadPool.globalInstance()
        runnable = Runnable(message)
        # Call start()
        pool.start(runnable)

    def button_clicked(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Aide")
        dlg.setText("Envoyer un message pour utiliser la messagerie.")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Question)
        dlg.exec()

    def quit(self):
        sender = self.sender()
        if sender is self.btn_quit: 
            sys.exit(app.exec_())

flag = True
while flag:
    try :
        host, port = ('127.0.0.1', 11111)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        app = QApplication(sys.argv)
        window = Window()
        window.show()
        sys.exit(app.exec())

    except ConnectionRefusedError as error:
        print(error)
        time.sleep(5)

