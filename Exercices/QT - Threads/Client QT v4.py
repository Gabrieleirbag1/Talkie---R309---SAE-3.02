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
        print(self.message)
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
                    print(f'Reception de : {reply}')
                    self.message_received.emit(reply)
                    
            except ConnectionRefusedError as error:
                print(error)

            except ConnectionResetError as error:
                print(error)

            except BrokenPipeError as error:
                print(f'{error} : Wait a few seconds')

        print("ReceptionThread ends")

class ConnectThread(QThread):
    def __init__(self, log, send, connect, log2, send2, connect2, log3, send3, connect3, log4, send4, connect4, log5, send5, connect5):
        super().__init__()
        self.log = log
        self.send = send
        self.connect = connect

        self.log2 = log2
        self.send2 = send2
        self.connect2 = connect2

        self.log3 = log3
        self.send3 = send3
        self.connect3 = connect3

        self.log4 = log4
        self.send4 = send4
        self.connect4 = connect4

        self.log5 = log5
        self.send5 = send5
        self.connect5 = connect5
    
    def run(self):
        print("ConnectThread Up")
        try:
            host, port = ('127.0.0.1', 11111)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))

            self.connect.connect(self.sender)
            self.connect2.connect(self.sender2)
            self.connect3.connect(self.sender3)
            self.connect4.connect(self.sender4)
            self.connect5.connect(self.sender5)

            self.receiver_thread = ReceptionThread(self.client_socket)
            self.receiver_thread.message_received.connect(self.update_reply)      
            self.receiver_thread.start()

        except Exception as err:
            print(err)
            time.sleep(5)
            self.run()

    def update_reply(self, message):
        message = message.split("|")
        print(f'{message[1]}')

        if message[0] == 'Général':
            self.log.append(f'{message[1]}')

        elif message[0] == 'Blabla':
            self.log2.append(f'{message[1]}')
        
        elif message[0] == 'Comptabilité':
            self.log3.append(f'{message[1]}') 
        
        elif message[0] == 'Informatique':
            self.log4.append(f'{message[1]}') 
        
        elif message[0] == 'Marketing':
            self.log5.append(f'{message[1]}') 

    def sender(self):
        print("Général")
        reply = f"Général|{self.send.text()}"
        self.sender_thread = SenderThread(reply, self.client_socket)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def sender2(self):
        reply = f"Blabla|{self.send2.text()}"
        self.sender_thread = SenderThread(reply, self.client_socket)
        self.sender_thread.start()
        self.sender_thread.wait()

    def sender3(self):
        reply = f"Comptabilité|{self.send3.text()}"
        self.sender_thread = SenderThread(reply, self.client_socket)
        self.sender_thread.start()
        self.sender_thread.wait()

    def sender4(self):
        reply = f"Informatique|{self.send4.text()}"
        self.sender_thread = SenderThread(reply, self.client_socket)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def sender5(self):
        reply = f"Marketing|{self.send5.text()}"
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
        self.text_edit2 = QTextEdit(self.tab_2)
        self.text_edit2.setGeometry(QRect(20, 10, 721, 501))
        self.text_edit2.setObjectName("text_edit")
        self.text_edit2.setReadOnly(True)
        self.lineEdit2 = QLineEdit(self.tab_2)
        self.lineEdit2.setGeometry(QRect(20, 560, 721, 51))
        self.lineEdit2.setObjectName("lineEdit")
        self.label2 = QLabel(self.tab_2)
        self.label2.setGeometry(QRect(20, 510, 271, 41))
        self.label2.setMinimumSize(QSize(271, 21))
        self.label2.setFont(font)
        self.label2.setObjectName("label")
        self.pushButton_3 = QPushButton(self.tab_2)
        self.pushButton_3.setGeometry(QRect(770, 20, 81, 71))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton2 = QPushButton(self.tab_2)
        self.pushButton2.setGeometry(QRect(770, 560, 81, 51))
        self.pushButton2.setObjectName("pushButton2")
        self.tabWidget.addTab(self.tab_2, "")

        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.text_edit3 = QTextEdit(self.tab_3)
        self.text_edit3.setGeometry(QRect(20, 10, 721, 501))
        self.text_edit3.setObjectName("text_edit")
        self.text_edit3.setReadOnly(True)
        self.lineEdit3 = QLineEdit(self.tab_3)
        self.lineEdit3.setGeometry(QRect(20, 560, 721, 51))
        self.lineEdit3.setObjectName("lineEdit")
        self.label3 = QLabel(self.tab_3)
        self.label3.setGeometry(QRect(20, 510, 271, 41))
        self.label3.setMinimumSize(QSize(271, 21))
        self.label3.setFont(font)
        self.label3.setObjectName("label")
        self.pushButton_4 = QPushButton(self.tab_3)
        self.pushButton_4.setGeometry(QRect(770, 20, 81, 71))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton3 = QPushButton(self.tab_3)
        self.pushButton3.setGeometry(QRect(770, 560, 81, 51))
        self.pushButton3.setObjectName("pushButton3")
        self.tabWidget.addTab(self.tab_3, "")

        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.text_edit4 = QTextEdit(self.tab_4)
        self.text_edit4.setGeometry(QRect(20, 10, 721, 501))
        self.text_edit4.setObjectName("text_edit")
        self.text_edit4.setReadOnly(True)
        self.lineEdit4 = QLineEdit(self.tab_4)
        self.lineEdit4.setGeometry(QRect(20, 560, 721, 51))
        self.lineEdit4.setObjectName("lineEdit")
        self.label4 = QLabel(self.tab_4)
        self.label4.setGeometry(QRect(20, 510, 271, 41))
        self.label4.setMinimumSize(QSize(271, 21))
        self.label4.setFont(font)
        self.label4.setObjectName("label")
        self.pushButton_5 = QPushButton(self.tab_4)
        self.pushButton_5.setGeometry(QRect(770, 20, 81, 71))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton4 = QPushButton(self.tab_4)
        self.pushButton4.setGeometry(QRect(770, 560, 81, 51))
        self.pushButton4.setObjectName("pushButton4")
        self.tabWidget.addTab(self.tab_4, "")

        self.tab_5 = QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabWidget.addTab(self.tab_5, "")
        self.text_edit5 = QTextEdit(self.tab_5)
        self.text_edit5.setGeometry(QRect(20, 10, 721, 501))
        self.text_edit5.setObjectName("text_edit")
        self.text_edit5.setReadOnly(True)
        self.lineEdit5 = QLineEdit(self.tab_5)
        self.lineEdit5.setGeometry(QRect(20, 560, 721, 51))
        self.lineEdit5.setObjectName("lineEdit")
        self.label5 = QLabel(self.tab_5)
        self.label5.setGeometry(QRect(20, 510, 271, 41))
        self.label5.setMinimumSize(QSize(271, 21))
        self.label5.setFont(font)
        self.label5.setObjectName("label")
        self.pushButton_6 = QPushButton(self.tab_5)
        self.pushButton_6.setGeometry(QRect(770, 20, 81, 71))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton5 = QPushButton(self.tab_5)
        self.pushButton5.setGeometry(QRect(770, 560, 81, 51))
        self.pushButton5.setObjectName("pushButton5")
        self.tabWidget.addTab(self.tab_5, "")

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

        log2 = self.text_edit2
        send2 = self.lineEdit2
        connect2 = self.pushButton2.clicked

        log3 = self.text_edit3
        send3 = self.lineEdit3
        connect3 = self.pushButton3.clicked

        log4 = self.text_edit4
        send4 = self.lineEdit4
        connect4 = self.pushButton4.clicked

        log5 = self.text_edit5
        send5 = self.lineEdit5
        connect5 = self.pushButton5.clicked

        self.accept_thread = ConnectThread(log, send, connect, log2, send2, connect2, log3, send3, connect3, log4, send4, connect4, log5, send5, connect5)
        self.accept_thread.start()

        self.label.setText(f"Messagerie (Connecté)")

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Skype"))
        self.label.setText(_translate("MainWindow", "Envoyer un message"))
        self.pushButton_2.setText(_translate("MainWindow", "PROFIL"))
        self.pushButton.setText(_translate("MainWindow", ">"))
        self.label2.setText(_translate("MainWindow", "Envoyer un message"))
        self.pushButton_3.setText(_translate("MainWindow", "PROFIL"))
        self.pushButton2.setText(_translate("MainWindow", ">"))
        self.label3.setText(_translate("MainWindow", "Envoyer un message"))
        self.pushButton_4.setText(_translate("MainWindow", "PROFIL"))
        self.pushButton3.setText(_translate("MainWindow", ">"))
        self.label4.setText(_translate("MainWindow", "Envoyer un message"))
        self.pushButton_5.setText(_translate("MainWindow", "PROFIL"))
        self.pushButton4.setText(_translate("MainWindow", ">"))
        self.label5.setText(_translate("MainWindow", "Envoyer un message"))
        self.pushButton_6.setText(_translate("MainWindow", "PROFIL"))
        self.pushButton5.setText(_translate("MainWindow", ">"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Général"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Blabla"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Comptabilité"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Informatique"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "Marketing"))


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