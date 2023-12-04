import sys, time, threading, socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



flag = True

host, port = ('127.0.0.1', 10000)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        try :
            self.setWindowTitle("Chronomètre")


            self.label1 = QLabel("Compteur :")
            self.btn = QPushButton("Start")
            self.btn_reset = QPushButton("Reset")
            self.btn_stop = QPushButton("Stop")
            self.btn_connect = QPushButton("Connect")
            self.btn_quit = QPushButton("Quitter")
            self.line_edit1= QLineEdit("0")

            layout = QGridLayout()

            layout.addWidget(self.label1, 0, 0)
            layout.addWidget(self.line_edit1, 1, 0, 2, 2)

            self.btn.clicked.connect(self.start)
            self.btn_stop.clicked.connect(self.stop)
            self.btn_reset.clicked.connect(self.reset)
            self.btn_connect.clicked.connect(self.connect_server)

            self.btn_quit.clicked.connect(self.quit)

            layout.addWidget(self.btn, 2, 0, 2, 2)
            layout.addWidget(self.btn_reset, 3, 0)
            layout.addWidget(self.btn_stop, 3, 1)
            layout.addWidget(self.btn_connect, 4, 0)
            layout.addWidget(self.btn_quit, 4, 1)

            widget = QWidget()

            widget.setLayout(layout)

            self.setCentralWidget(widget)
        except Exception as e:
            print(f"Mainwindow {e}")


    def start(self):
        global flag
        self.t1 = threading.Thread (target=self.__start, args=[])
        flag = True
        self.t1.start()


    def __start(self):
        global flag, compteur
        compteur = 0
        while flag:
            compteur += 1
            time.sleep(1)
            self.line_edit1.setText(f"{compteur}")
            print(compteur)
            try :
                self.send(compteur)
            except:
                continue
        print("end")
        self.reset()

    def connect_server(self):
        try :
            global client_socket
            client_socket.connect((host,port))
        except ConnectionRefusedError:
            self.dialog()
    
    def send(self, compteur):
        global client_socket
        client_socket.send(compteur.encode())

    def dialog(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Erreur")
        dlg.setText("Impossible de se connecter")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Question)
        dlg.exec()
    
    def stop(self):
        global client_socket
        try:
            global flag
            flag = False
            self.t1.join()
            self.line_edit1.setText("0")
            compteur = "bye"
            self.send(compteur)
        except:
            pass

    def reset(self):
        global compteur
        compteur = 0


    def quit(self):
        #sender pas forrcément nécessaire ici mais je pense plus propre avec 
        sender = self.sender()
        if sender is self.btn_quit:
            self.stop()
            QApplication.exit(0)
        
        
app = QApplication(sys.argv)
window = MainWindow()
window.resize(250, 250)
window.show()

if __name__ == '__main__':
    sys.exit(app.exec_())