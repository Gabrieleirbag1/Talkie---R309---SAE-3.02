from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, socket, time


flag = False

class SenderThread(QThread):
    def __init__(self, message, client_socket):
        super().__init__()
        self.message = message
        self.client_socket = client_socket

    def run(self):
        global flag
        print("SenderThread up")
        try:
            self.client_socket.send(self.message.encode())

            if self.message == "arret" or self.message == "bye":
                print("Arret du serveur")
                flag = True
                self.quitter()

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)
        print("SenderThread ends")
    
    def quitter(self):
        QCoreApplication.instance().quit()

                    

class ReceptionThread(QThread):
    message_received = pyqtSignal(str)
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        print("ReceptionThread up")
        global flag
        while not flag:
            try:
                reply = self.client_socket.recv(1024).decode("utf-8")

                if not reply:
                    print("Le serveur n'est plus accessible...")
                    flag = True
        
                else:
                    print(f'{reply}')
                    self.message_received.emit(reply)
                    
            except ConnectionRefusedError as error:
                print(error)

            except ConnectionResetError as error:
                print(error)

            except BrokenPipeError as error:
                print(f'{error} : Wait a few seconds')

        print("ReceptionThread ends")

class ConnectThread(QThread):
    def __init__(self, log, send, connect):
        super().__init__()
        self.log = log
        self.send = send
        self.connect = connect
    
    def run(self):
        print("ConnectThread Up")
        try:
            host, port = ('127.0.0.1', 11111)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.connect.connect(self.sender)

            self.receiver_thread = ReceptionThread(self.client_socket)
            self.receiver_thread.message_received.connect(self.update_reply)      
            self.receiver_thread.start()

        except Exception as err:
            print(err)
            time.sleep(5)
            self.run()

    def update_reply(self, message):
        self.log.append(f'{message}') 

    def sender(self):
        reply = self.send.text()
        self.sender_thread = SenderThread(reply, self.client_socket)
        self.sender_thread.start()
        self.sender_thread.wait()

    def quitter(self):
        reply = "bye"
        self.sender_thread = SenderThread(reply, self.client_socket)
        self.sender_thread.start()
        self.sender_thread.wait()

class Window(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QRect(10, 0, 881, 671))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.text_edit = QTextEdit(self.tab)
        self.text_edit.setGeometry(QRect(20, 10, 721, 501))
        self.text_edit.setObjectName("text_edit")
        self.text_edit.setReadOnly(True)
        self.lineEdit = QLineEdit(self.tab)
        self.lineEdit.setGeometry(QRect(20, 560, 721, 51))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QLabel(self.tab)
        self.label.setGeometry(QRect(20, 510, 271, 41))
        self.label.setMinimumSize(QSize(271, 21))
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton_2 = QPushButton(self.tab)
        self.pushButton_2.setGeometry(QRect(770, 20, 81, 71))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton = QPushButton(self.tab)
        self.pushButton.setGeometry(QRect(770, 560, 81, 51))
        self.pushButton.setObjectName("pushButton")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 886, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(MainWindow)

        self.mainthread()
    
    def mainthread(self):
        log = self.text_edit
        send = self.lineEdit
        connect = self.pushButton.clicked

        self.accept_thread = ConnectThread(log, send, connect)
        self.accept_thread.start()

        self.label.setText(f"Messagerie (Connecté)")

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Skype"))
        self.label.setText(_translate("MainWindow", "Envoyer un message"))
        self.pushButton_2.setText(_translate("MainWindow", "PROFIL"))
        self.pushButton.setText(_translate("MainWindow", ">"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Général"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Admin"))


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        MainWindow = QMainWindow()
        ui = Window()
        ui.setupUi(MainWindow)
        MainWindow.show()

        sys.exit(app.exec_())
    finally:
        print("Arrêt client")
        flag = True
        arret = True