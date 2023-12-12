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
signup_window = None


class SenderThread(QThread):
    error_connected = pyqtSignal(str)
    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        global flag, client_socket
        print("SenderThread up")
        print(self.message)
        try:
            client_socket.send(self.message.encode())

            if self.message == "/arret" or self.message == "/bye":
                print("Arret du serveur")
                flag = True
                self.quitter()

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)

        except BrokenPipeError:
            print("Serveur non accessible")
            self.error_connected.emit("16")
        print("SenderThread ends")
                    

class ReceptionThread(QThread):
    message_received = pyqtSignal(str)
    success_connected = pyqtSignal(str)
    users_sended = pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def run(self):
        print("ReceptionThread up")
        global flag, client_socket
        while not flag:
            try:
                reply = client_socket.recv(1024).decode("utf-8")
                code = reply.split("|")

                if not reply:
                    print("Le serveur n'est plus accessible...")
                    flag = True
                    self.quitter()

                elif code[0] == "CODE":
                    print(code[1])
                    self.success_connected.emit(code[1])
                    print(f'Reception de : {reply}')

                elif code[0] == "USERS":
                    users = f"{code[1]}|{code[2]}"
                    self.users_sended.emit(users)
                    #print(f'Reception de : {users}')

                else:
                    #print(f'Reception de : {reply}')
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

        elif message[0] == 'Serveur':
            self.log.append(f'{message[1]}{message[2]}')
            self.log2.append(f'{message[1]}{message[2]}')
            self.log3.append(f'{message[1]}{message[2]}')
            self.log4.append(f'{message[1]}{message[2]}')
            self.log5.append(f'{message[1]}{message[2]}')

    def sender(self):
        global client_socket, username, password
        reply = f"Général|{username}/{password}|{self.send.text()}"
        self.send.setText("")
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def sender2(self):
        global client_socket, username, password
        reply = f"Blabla|{username}/{password}|{self.send2.text()}"
        self.send2.setText("")
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def sender3(self):
        global client_socket, username, password
        reply = f"Comptabilité|{username}/{password}|{self.send3.text()}"
        self.send3.setText("")
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def sender4(self):
        global client_socket, username, password
        reply = f"Informatique|{username}/{password}|{self.send4.text()}"
        self.send4.setText("")
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def sender5(self):
        global client_socket, username, password
        reply = f"Marketing|{username}/{password}|{self.send5.text()}"
        self.send5.setText("")
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def quitter(self):
        reply = "bye"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

class Window(QObject):
    courrier_window_signal = pyqtSignal()
    global MainWindow
    def setupUi(self, MainWindow):
        global receiver_thread
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 700)
        font = QFont()
        font.setPointSize(16)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QRect(10, 0, 980, 671))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.text_edit = QTextEdit(self.tab)
        self.text_edit.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit.setObjectName("text_edit")
        self.text_edit.setReadOnly(True)
        self.users_text_edit = QTextEdit(self.tab)
        self.users_text_edit.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit.setObjectName("users_text_edit")
        self.users_text_edit.setReadOnly(True)
        self.line_edit = QLineEdit(self.tab)
        self.line_edit.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit.setObjectName("lineEdit")
        self.line_edit.setMaxLength(255)
        self.label = QLabel(self.tab)
        self.label.setGeometry(QRect(20, 510, 271, 41))
        self.label.setMinimumSize(QSize(271, 21))
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.profil_button2 = QPushButton(self.tab)
        self.profil_button2.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button2.setObjectName("profil_button2")
        self.courrier_button = QPushButton(self.tab)
        self.courrier_button.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button.setObjectName("courrier_button")
        self.courrier_button.setFont(QFont('Arial', 40))
        self.send_button = QPushButton(self.tab)
        self.send_button.setGeometry(QRect(770, 560, 81, 51))
        self.send_button.setObjectName("send_button")
        self.friends_button = QPushButton(self.tab)
        self.friends_button.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button.setObjectName("friends_button")

        self.tabWidget.addTab(self.tab, "Général")

        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.text_edit2 = QTextEdit(self.tab_2)
        self.text_edit2.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit2.setObjectName("text_edit")
        self.text_edit2.setReadOnly(True)
        self.users_text_edit2 = QTextEdit(self.tab_2)
        self.users_text_edit2.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit2.setObjectName("users_text_edit2")
        self.users_text_edit2.setReadOnly(True)
        self.line_edit2 = QLineEdit(self.tab_2)
        self.line_edit2.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit2.setObjectName("lineEdit")
        self.line_edit2.setMaxLength(255)
        self.label2 = QLabel(self.tab_2)
        self.label2.setGeometry(QRect(20, 510, 271, 41))
        self.label2.setMinimumSize(QSize(271, 21))
        self.label2.setFont(font)
        self.label2.setObjectName("label")
        self.profil_button3 = QPushButton(self.tab_2)
        self.profil_button3.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button3.setObjectName("profil_button3")
        self.courrier_button2 = QPushButton(self.tab_2)
        self.courrier_button2.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button2.setObjectName("courrier_button2")
        self.courrier_button2.setFont(QFont('Arial', 40))
        self.send_button2 = QPushButton(self.tab_2)
        self.send_button2.setGeometry(QRect(770, 560, 81, 51))
        self.send_button2.setObjectName("send_button2")
        self.friends_button2 = QPushButton(self.tab)
        self.friends_button2.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button2.setObjectName("friends_button2")
        self.tabWidget.addTab(self.tab_2, "Blabla")

        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.text_edit3 = QTextEdit(self.tab_3)
        self.text_edit3.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit3.setObjectName("text_edit")
        self.text_edit3.setReadOnly(True)
        self.users_text_edit3 = QTextEdit(self.tab_3)
        self.users_text_edit3.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit3.setObjectName("users_text_edit3")
        self.users_text_edit3.setReadOnly(True)
        self.line_edit3 = QLineEdit(self.tab_3)
        self.line_edit3.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit3.setObjectName("lineEdit")
        self.line_edit3.setMaxLength(255)
        self.label3 = QLabel(self.tab_3)
        self.label3.setGeometry(QRect(20, 510, 271, 41))
        self.label3.setMinimumSize(QSize(271, 21))
        self.label3.setFont(font)
        self.label3.setObjectName("label")
        self.profil_button4 = QPushButton(self.tab_3)
        self.profil_button4.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button4.setObjectName("profil_button4")
        self.courrier_button3 = QPushButton(self.tab_3)
        self.courrier_button3.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button3.setObjectName("courrier_button3")
        self.courrier_button3.setFont(QFont('Arial', 40))
        self.send_button3 = QPushButton(self.tab_3)
        self.send_button3.setGeometry(QRect(770, 560, 81, 51))
        self.send_button3.setObjectName("send_button3")
        self.friends_button3 = QPushButton(self.tab)
        self.friends_button3.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button3.setObjectName("friends_button3")
        self.tabWidget.addTab(self.tab_3, "Comptabilité")

        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.text_edit4 = QTextEdit(self.tab_4)
        self.text_edit4.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit4.setObjectName("text_edit")
        self.text_edit4.setReadOnly(True)
        self.users_text_edit4 = QTextEdit(self.tab_4)
        self.users_text_edit4.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit4.setObjectName("users_text_edit4")
        self.users_text_edit4.setReadOnly(True)
        self.line_edit4 = QLineEdit(self.tab_4)
        self.line_edit4.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit4.setObjectName("lineEdit")
        self.line_edit4.setMaxLength(255)
        self.label4 = QLabel(self.tab_4)
        self.label4.setGeometry(QRect(20, 510, 271, 41))
        self.label4.setMinimumSize(QSize(271, 21))
        self.label4.setFont(font)
        self.label4.setObjectName("label")
        self.profil_button5 = QPushButton(self.tab_4)
        self.profil_button5.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button5.setObjectName("profil_button5")
        self.courrier_button4 = QPushButton(self.tab_4)
        self.courrier_button4.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button4.setObjectName("courrier_button4")
        self.courrier_button4.setFont(QFont('Arial', 40))
        self.send_button4 = QPushButton(self.tab_4)
        self.send_button4.setGeometry(QRect(770, 560, 81, 51))
        self.send_button4.setObjectName("send_button4")
        self.friends_button4 = QPushButton(self.tab)
        self.friends_button4.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button4.setObjectName("friends_button4")
        self.tabWidget.addTab(self.tab_4, "Informatique")

        self.tab_5 = QWidget()
        self.tab_5.setObjectName("tab_5")
        self.text_edit5 = QTextEdit(self.tab_5)
        self.text_edit5.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit5.setObjectName("text_edit")
        self.text_edit5.setReadOnly(True)
        self.users_text_edit5 = QTextEdit(self.tab_5)
        self.users_text_edit5.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit5.setObjectName("users_text_edit")
        self.users_text_edit5.setReadOnly(True)
        self.line_edit5 = QLineEdit(self.tab_5)
        self.line_edit5.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit5.setObjectName("lineEdit")
        self.line_edit5.setMaxLength(255)
        self.label5 = QLabel(self.tab_5)
        self.label5.setGeometry(QRect(20, 510, 271, 41))
        self.label5.setMinimumSize(QSize(271, 21))
        self.label5.setFont(font)
        self.label5.setObjectName("label")
        self.profil_button6 = QPushButton(self.tab_5)
        self.profil_button6.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button6.setObjectName("profil_button6")
        self.courrier_button5 = QPushButton(self.tab_5)
        self.courrier_button5.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button5.setObjectName("courrier_button5")
        self.courrier_button5.setFont(QFont('Arial', 40))
        self.send_button5 = QPushButton(self.tab_5)
        self.send_button5.setGeometry(QRect(770, 560, 81, 51))
        self.send_button5.setObjectName("send_button5")
        self.friends_button5 = QPushButton(self.tab)
        self.friends_button5.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button5.setObjectName("friends_button5")
        self.tabWidget.addTab(self.tab_5, "Marketing")

        self.dialog = QPushButton("?")
        self.dialog.clicked.connect

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
        receiver_thread = ReceptionThread()
        
        self.courrier_button.clicked.connect(self.courrier_window)
        self.courrier_button2.clicked.connect(self.courrier_window)
        self.courrier_button3.clicked.connect(self.courrier_window)
        self.courrier_button4.clicked.connect(self.courrier_window)
        self.courrier_button5.clicked.connect(self.courrier_window)

        try:
            receiver_thread.success_connected.connect(self.history_code)
            receiver_thread.users_sended.connect(self.users_show)
        except:
            pass
    
    def courrier_window(self):
        self.courrier_window_signal.emit()

    def mainthread(self):
        log = self.text_edit
        send = self.line_edit
        connect = self.send_button.clicked

        log2 = self.text_edit2
        send2 = self.line_edit2
        connect2 = self.send_button2.clicked

        log3 = self.text_edit3
        send3 = self.line_edit3
        connect3 = self.send_button3.clicked

        log4 = self.text_edit4
        send4 = self.line_edit4
        connect4 = self.send_button4.clicked

        log5 = self.text_edit5
        send5 = self.line_edit5
        connect5 = self.send_button5.clicked

        self.accept_thread = ConnectThread(log, send, connect, log2, send2, connect2, log3, send3, connect3, log4, send4, connect4, log5, send5, connect5)
        self.accept_thread.start()

        self.label.setText(f"Messagerie (Connecté)")


    def users_show(self, users):
        users = users.split("|")
        if users[0] == "Général":
            self.users_text_edit.append(f"{users[1]}\n─────────────────")
        elif users[0] == "Blabla":
            self.users_text_edit2.append(f"{users[1]}\n─────────────────")
        elif users[0] == "Comptabilité":
            self.users_text_edit3.append(f"{users[1]}\n─────────────────")
        elif users[0] == "Informatique":
            self.users_text_edit4.append(f"{users[1]}\n─────────────────")
        elif users[0] == "Marketing":
            self.users_text_edit5.append(f"{users[1]}\n─────────────────")
        

    def history_code(self, code):
        try:
            if int(code) > 9:
                if code == '10':
                    self.tabWidget.setTabEnabled(0, False)
                
                elif code == "11":
                    self.tabWidget.setTabEnabled(1, False)

                elif code == "12":
                    self.tabWidget.setTabEnabled(2, False)

                elif code == "13":
                    self.tabWidget.setTabEnabled(3, False)

                elif code == "14":
                    self.tabWidget.setTabEnabled(4, False)

                elif code == "17":
                    self.errorbox(code)

                elif code == "21":
                    self.errorbox(code)
                
                elif code == "22":
                    self.errorbox(code)

                elif code == "23":
                    self.errorbox(code)

                elif code == "24":
                    self.errorbox(code)
                
                elif code == "25":
                    self.errorbox(code)

        except:
            pass

    def errorbox(self, code):
        error = QMessageBox()
        error.setWindowTitle("Erreur")
        if code == "17":
            content = "(17) Vous n'avez pas la permission d'effectuer cette commande !"
        elif code == "21":
            content = "(21) L'utilisateur que vous voulez sanctionner n'existe pas."
        elif code == "22":
            content = "(22) Erreur de syntaxe de la commande."
        elif code == "23":
            content = "(23) L'utilisateur a déjà une sanction."
        elif code == "24":
            content = "(24) Vous avez été exclu du serveur."
            quit = True
        elif code == "25":
            content = "(25) Vous avez été banni du serveur."
            quit = True
        error.setText(content)
        error.setIcon(QMessageBox.Warning)
        error.exec()

        if quit:
            print("TRUE")
            self.quitter()

    def quitter(self):
        QCoreApplication.instance().quit()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Skype"))
        self.label.setText(_translate("MainWindow", "Messagerie"))
        self.profil_button2.setText(_translate("MainWindow", "PROFIL"))
        self.courrier_button.setText(_translate("MainWindow", "✉"))
        self.send_button.setText(_translate("MainWindow", ">"))
        self.label2.setText(_translate("MainWindow", "Messagerie"))
        self.profil_button3.setText(_translate("MainWindow", "PROFIL"))
        self.courrier_button2.setText(_translate("MainWindow", "✉"))
        self.send_button2.setText(_translate("MainWindow", ">"))
        self.label3.setText(_translate("MainWindow", "Messagerie"))
        self.profil_button4.setText(_translate("MainWindow", "PROFIL"))
        self.courrier_button3.setText(_translate("MainWindow", "✉"))
        self.send_button3.setText(_translate("MainWindow", ">"))
        self.label4.setText(_translate("MainWindow", "Messagerie"))
        self.profil_button5.setText(_translate("MainWindow", "PROFIL"))
        self.courrier_button4.setText(_translate("MainWindow", "✉"))
        self.send_button4.setText(_translate("MainWindow", ">"))
        self.label5.setText(_translate("MainWindow", "Messagerie"))
        self.profil_button6.setText(_translate("MainWindow", "PROFIL"))
        self.courrier_button5.setText(_translate("MainWindow", "✉"))
        self.send_button5.setText(_translate("MainWindow", ">"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Général"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Blabla"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Comptabilité"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Informatique"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "Marketing"))


class Login(QMainWindow):
    signup_window_signal = pyqtSignal()
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
        self.username.returnPressed.connect(self.auth)

        self.label_2 = QLabel(self)
        self.label_2.setGeometry(QRect(160, 130, 141, 41))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Mot de passe")

        self.password = QLineEdit(self)
        self.password.setGeometry(QRect(60, 180, 281, 25))
        self.password.setObjectName("lineEdit_2")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.auth)

        self.signup_button = QPushButton(self)
        self.signup_button.setGeometry(QRect(220, 250, 121, 31))
        self.signup_button.setObjectName("pushButton")
        self.signup_button.setText("S'inscrire")
        self.signup_button.clicked.connect(self.signup_window)

        self.connect_button2 = QPushButton(self)
        self.connect_button2.setGeometry(QRect(60, 250, 121, 31))
        self.connect_button2.setObjectName("pushButton_2")
        self.connect_button2.setText("Connexion")
        self.connect_button2.clicked.connect(self.auth)
        
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
        self.sender_thread.error_connected.connect(self.errorBox)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def login(self, code):
        global MainWindow
        try:
            code20 = code.split("/")
            code200 = code20[0]
        except:
            code200 = '20'

        try:
            if int(code) <= 3 or int(code) == 19:
                if code == '1':
                    time.sleep(1)
                    MainWindow.show()
                    self.quitter()
                else:
                    self.errorBox(code, code20)
        except:
            if int(code200) == 20:
                self.errorBox(code, code20)
            else:
                pass

    def signup_window(self):
        self.signup_window_signal.emit()

        
    def quitter(self):
        self.close()

    def errorBox(self, code, code20):
        error = QMessageBox(self)
        error.setWindowTitle("Erreur")
        if code == '2':
            content = "(2) L'utilisateur n'a pas été trouvé"
        elif code == '3':
            content = "(3) Erreur de mot de passe"
        elif code == '15':
            return
        elif code == '16':
            content = "(16) Erreur de connexion au serveur."
        elif code == '19':
            content = "(19) Vous avez été banni(e) pour une durée indéfinie."
        elif code20[0] == '20':
            content = f"(20) Vous avez été exclu jusqu'au {code20[1]}"
        else:
            content = "Erreur inconnue"

        error.setText(content)
        error.setIcon(QMessageBox.Warning)
        error.exec()


class Sign_up(QMainWindow):
    def __init__(self, parent=None):
        super(Sign_up, self).__init__(parent)

        self.setupUi()

    def setupUi(self):
        global receiver_thread

        self.setObjectName("Sign_up")
        self.resize(432, 593)
        self.setWindowTitle("Sign up")

        font = QFont()
        font.setPointSize(14)

        self.label = QLabel(self)
        self.label.setGeometry(20, 20, 221, 31)
        self.label.setFont(font)
        self.label.setObjectName("label_identifiant")
        self.label.setText("Identifiant")

        self.line_edit = QLineEdit(self)
        self.line_edit.setGeometry(20, 60, 391, 31)
        self.line_edit.setObjectName("lineEdit_identifiant")
        self.line_edit.setMaxLength(45)

        self.label_2 = QLabel(self)
        self.label_2.setGeometry(20, 120, 221, 31)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2_pseudo")
        self.label_2.setText("Pseudo")

        self.line_edit_2 = QLineEdit(self)
        self.line_edit_2.setGeometry(20, 160, 391, 31)
        self.line_edit_2.setObjectName("lineEdit_2_pseudo")
        self.line_edit_2.setMaxLength(20)

        self.label_3 = QLabel(self)
        self.label_3.setGeometry(20, 220, 221, 31)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3_mail")
        self.label_3.setText("Mail")

        self.line_edit_3 = QLineEdit(self)
        self.line_edit_3.setGeometry(20, 260, 391, 31)
        self.line_edit_3.setObjectName("lineEdit_3_mail")
        self.line_edit_3.setMaxLength(320)

        self.label_4 = QLabel(self)
        self.label_4.setGeometry(20, 320, 281, 31)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4_mdp")
        self.label_4.setText("Mot de passe")

        self.line_edit_4 = QLineEdit(self)
        self.line_edit_4.setGeometry(20, 360, 391, 31)
        self.line_edit_4.setText("")
        self.line_edit_4.setObjectName("lineEdit_4_mdp")
        self.line_edit_4.setMaxLength(45)
        self.line_edit_4.setEchoMode(QLineEdit.Password)

        self.label_5 = QLabel(self)
        self.label_5.setGeometry(20, 420, 261, 31)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5_cmdp")
        self.label_5.setText("Confirmer le mot de passe")

        self.line_edit_5 = QLineEdit(self)
        self.line_edit_5.setGeometry(20, 460, 391, 31)
        self.line_edit_5.setObjectName("lineEdit_5_cmdp")
        self.line_edit_5.setMaxLength(45)
        self.line_edit_5.setEchoMode(QLineEdit.Password)

        self.signup_button = QPushButton(self)
        self.signup_button.setGeometry(QRect(150, 520, 131, 41))
        self.signup_button.setFont(font)
        self.signup_button.setObjectName("pushButton")
        self.signup_button.setText("S'inscrire")
        self.signup_button.clicked.connect(self.sign_up)

        receiver_thread.success_connected.connect(self.sign_code)

    def sign_up(self):
        try:
            username = self.line_edit.text()
            alias = self.line_edit_2.text()
            mail = self.line_edit_3.text()
            mdp = self.line_edit_4.text()
            cmdp = self.line_edit_5.text()
            
            reply = f"SIGNUP|{username}/{alias}/{mail}/{mdp}/{cmdp}"

            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()

        except Exception as e:
            print(e)

    def sign_code(self, code):
        if int(code) > 3:
            if code == '4':
                self.successBox(code)
            else:
                self.errorBox(code)

    def errorBox(self, code):
        error = QMessageBox(self)
        error.setWindowTitle("Erreur")

        if code == '5':
            content = "(5) Les mots de passes ne correspondent pas"
        elif code == '6':
            content = "(6) Le mail ne respecte pas le format"
        elif code == '8':
            content = "(8) L'utilisateur existe déjà, votre identifiant doit être unique."
        elif code == '9':
            content = "(9) Les caractères ne sont pas autorisés : %, #, &, '"
        else:
            return

        error.setIcon(QMessageBox.Warning)
        error.setText(content)
        error.exec()

    def successBox(self, code):
        if code == '4':
            success = QMessageBox(self)
            success.setWindowTitle("Succès")
            content = "Vous avez été inscrit avec succès !"
            success.setIcon(QMessageBox.Information)
            success.setText(content)
            success.exec()
            self.quitter()
        else:
            self.errorBox(code)

    def quitter(self):
        self.close()

class CourrierWidget(QWidget):
    def __init__(self, text):
        super().__init__()

        self.initUI(text)

    def initUI(self, text):
        layout = QVBoxLayout(self)

        self.button = QPushButton(text, self)
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("Option 1")
        self.comboBox.addItem("Option 2")
        self.comboBox.addItem("Option 3")

        layout.addWidget(self.button)
        layout.addWidget(self.comboBox)

class CourrierWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Notifications')
        self.setGeometry(100, 100, 400, 300)

        self.list_widget = QListWidget(self)

        self.add_button = QPushButton('Ajouter', self)
        self.add_button.clicked.connect(self.add_line_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.list_widget)
        main_layout.addWidget(self.add_button)

        self.line_widgets = []

    def add_line_widget(self):
        text = f'Ligne {len(self.line_widgets) + 1}'
        line_widget = CourrierWidget(text)

        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(line_widget.sizeHint())  # Définir la hauteur de l'élément
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, line_widget)

        self.line_widgets.append(line_widget)

def show_courrier_window():
    global courrier_window
    courrier_window = CourrierWindow()
    courrier_window.show()

def show_signup_window():
    global signup_window
    signup_window = Sign_up()
    signup_window.show()

def end():
    global flag, arret
    error_dialog = QErrorMessage()
    error_dialog.showMessage('Oh no!')
    flag = True
    arret = True
    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        MainWindow = QMainWindow()
        ui = Window()
        ui.setupUi(MainWindow)
        w = Login()
        w.show()

        # Connecter le signal show_self_signal à la fonction d'affichage de l'inscription
        w.signup_window_signal.connect(show_signup_window)
        ui.courrier_window_signal.connect(show_courrier_window)

        sys.exit(app.exec_())
    finally:
        print("Arrêt client")
        #end()


