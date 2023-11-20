import sys
import time
import threading
import socket

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Runnable(QRunnable):
    def __init__(self, reply):
        super().__init__()
        self.reply = reply

    @pyqtSlot()
    def run(self):
        # This method will be called when the QRunnable starts
        self.reception()

    def reception(self):
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
                self.reply.setText(recep)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Serveur")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # Create and connect widgets
        self.label = QLabel("Logs")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.line_edit = QLineEdit()
        self.countBtn = QPushButton("Envoyer")
        self.btn_quit = QPushButton("Quitter")

        self.line_edit.setEnabled(False)
        self.btn_quit.clicked.connect(self.quit)

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.countBtn)
        layout.addWidget(self.btn_quit)
        
        self.centralWidget.setLayout(layout)
        
        self.label.setText(f"Log du serveur")
        
        self.line_edit.setText(f"")
        reply = self.line_edit

        pool = QThreadPool.globalInstance()
        runnable = Runnable(reply)
        # 3. Call start()
        pool.start(runnable)

    def quit(self):
        sender = self.sender()
        if sender is self.btn_quit:
            sys.exit(app.exec_())


host, port = ('0.0.0.0', 1111)
server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

app = QApplication(sys.argv)
window = Window()
window.show()

sys.exit(app.exec())
