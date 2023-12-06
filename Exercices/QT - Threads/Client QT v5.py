from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, socket, time

flag = False
host, port = ('127.0.0.1', 11111)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_thread = None
MainWindow = None
username = None
password = None

class SenderThread(QThread):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        global flag, client_socket
        print("SenderThread up")
        print(self.message)
        try:
            client_socket.send(self.message.encode())

            if self.message == "arret" or self.message == "bye":
                print("Arret du serveur")
                flag = True
                self.quitter()

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)

        except BrokenPipeError:
            print("Serveur non accessible")
        print("SenderThread ends")
                    

class ReceptionThread(QThread):
    message_received = pyqtSignal(str)
    success_connected = pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def run(self):
        print("ReceptionThread up")
        global flag, client_socket
        while not flag:
            try:
                reply = client_socket.recv(1024).decode("utf-8")
                code = reply.split("|")
                print(code)

                if not reply:
                    print("Le serveur n'est plus accessible...")
                    flag = True
                    self.quitter()

                elif code[0] == "CODE":
                    self.success_connected.emit(code[1])
        
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


    def quitter(self):
        QCoreApplication.instance().quit()

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
        global client_socket, receiver_thread
        try:
            client_socket.connect((host, port))
            self.connect.connect(self.sender)
            self.connect2.connect(self.sender2)
            self.connect3.connect(self.sender3)
            self.connect4.connect(self.sender4)
            self.connect5.connect(self.sender5)

            receiver_thread.message_received.connect(self.update_reply)    
            receiver_thread.start()

        except Exception as err:
            print(err)
            time.sleep(5)
            self.run()

        
    def update_reply(self, message):
        message = message.split("|")
        print(f'GROS DODO {message},{message[2]}')

        if message[0] == 'Général':
            self.log.append(f'{message[1]}{message[2]}')

        elif message[0] == 'Blabla':
            self.log2.append(f'{message[1]}{message[2]}')
        
        elif message[0] == 'Comptabilité':
            self.log3.append(f'{message[1]}{message[2]}') 
        
        elif message[0] == 'Informatique':
            self.log4.append(f'{message[1]}{message[2]}')
        
        elif message[0] == 'Marketing':
            self.log5.append(f'{message[1]}{message[2]}')

    def sender(self):
        global client_socket, username, password
        reply = f"Général|{username}/{password}|{self.send.text()}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def sender2(self):
        global client_socket, username, password
        reply = f"Blabla|{username}/{password}|{self.send2.text()}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def sender3(self):
        global client_socket, username, password
        reply = f"Comptabilité|{username}/{password}|{self.send3.text()}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def sender4(self):
        global client_socket, username, password
        reply = f"Informatique|{username}/{password}|{self.send4.text()}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def sender5(self):
        global client_socket, username, password
        reply = f"Marketing|{username}/{password}|{self.send5.text()}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def quitter(self):
        reply = "bye"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

class Window(object):
    global MainWindow
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
        MainWindow.setEnabled(False)

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


class Login(QMainWindow):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        self.setupUi()

    def setupUi(self):
        global receiver_thread
        self.setObjectName("Login")
        self.resize(400, 300)

        self.setWindowTitle("Log in")

        self.label = QLabel(self)
        self.label.setGeometry(QRect(160, 30, 141, 41))
        self.label.setObjectName("label")
        self.label.setText("Identifiant")

        self.username = QLineEdit(self)
        self.username.setGeometry(QRect(60, 80, 281, 25))
        self.username.setObjectName("lineEdit")

        self.label_2 = QLabel(self)
        self.label_2.setGeometry(QRect(160, 130, 141, 41))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Mot de passe")

        self.password = QLineEdit(self)
        self.password.setGeometry(QRect(60, 180, 281, 25))
        self.password.setObjectName("lineEdit_2")

        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(QRect(220, 250, 121, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("S'inscrire")

        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setGeometry(QRect(60, 250, 121, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Connexion")
        self.pushButton_2.clicked.connect(self.auth)

        receiver_thread = ReceptionThread()
        try:
            receiver_thread.success_connected.connect(self.login)
        except:
            pass

    def auth(self):
        global username, password
        username = self.username.text()
        password = self.password.text()
        reply = f"LOGIN|{username}/{password}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def login(self, code):
        global MainWindow
        if code == '1':
            MainWindow.setEnabled(True)
            self.quitter()
        else:
            self.errorBox(code)

    def quitter(self):
        self.close()

    def errorBox(self, code):
        error = QMessageBox(self)
        error.setWindowTitle("Erreur")
        if code == '2':
            content = "L'utilisateur n'a pas été trouvé"
        elif code == '3':
            content = "Erreur de mot de passe"
        else:
            content = "Erreur inconnue"

        error.setText(content)
        error.setIcon(QMessageBox.Warning)
        error.exec()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        MainWindow = QMainWindow()
        ui = Window()
        ui.setupUi(MainWindow)
        MainWindow.show()

        w = Login()
        w.show()

        sys.exit(app.exec_())
    finally:
        print("Arrêt client")
        flag = True
        arret = True

        MainWindow.setEnabled(False)

        error_dialog = QErrorMessage()
        error_dialog.showMessage('Oh no! La connexion au serveur a été perdue...')

        app.exec_()
