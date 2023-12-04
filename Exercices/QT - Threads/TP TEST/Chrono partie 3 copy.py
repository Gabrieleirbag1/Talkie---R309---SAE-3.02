import sys, time, threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



flag = True

class StartThread(QThread):
    reset = pyqtSignal(str)
    def __init__(self, line):
        super().__init__()
        self.line = line

    def run(self):
        global flag, compteur
        compteur = 0
        while flag:
            compteur += 1
            time.sleep(1)
            self.line.setText(f"{compteur}")
            print(compteur)
        try :
            self.line.setText("0")
            self.reset.emit(compteur)
        except Exception as e:
            print(e)
        print("end")


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
        line = self.line_edit1
        global flag
        self.startthread = StartThread(line)
        self.startthread.start()
        self.startthread.reset.connect(self.reset)
    
    def stop(self):
        try :
            global flag
            flag = False
            self.startthread.wait()
        except Exception as e:
            print(f"bug :{e}")

    def reset(self):
        global compteur
        compteur = 0

    def quit(self):
        #sender pas forrcément nécessaire ici mais je pense plus propre avec 
        sender = self.sender()
        if sender is self.btn_quit: 
            self.stop()
            sys.exit(app.exec_())
        
        
app = QApplication(sys.argv)
window = MainWindow()
window.resize(250, 250)
window.show()

if __name__ == '__main__':
    sys.exit(app.exec_())