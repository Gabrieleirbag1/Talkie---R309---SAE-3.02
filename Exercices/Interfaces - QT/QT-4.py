import logging
import random
import sys
import time
import threading
import socket

from PyQt5.QtCore import QRunnable, Qt, QThreadPool
from PyQt5.QtWidgets import *

logging.basicConfig(format="%(message)s", level=logging.INFO)

class Runnable(QRunnable):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        host, port = ('127.0.0.1', 11111)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        try:
            print(self.message)
    
            client_socket.send(self.message.encode())

            if self.message == "bye":
                print("DÉCONNEXION")
                flag = True

            elif self.message == "arret":
                flag = True

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("QThreadPool + QRunnable")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # Create and connect widgets
        self.label = QLabel("Hello, World!")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        countBtn = QPushButton("Click me!")
        countBtn.clicked.connect(self.runTasks)
        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(countBtn)
        self.centralWidget.setLayout(layout)

    def runTasks(self):
        message = str("test")
        self.label.setText(f"Running Threads")
        pool = QThreadPool.globalInstance()
        runnable = Runnable(message)
        # 3. Call start()
        pool.start(runnable)

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
