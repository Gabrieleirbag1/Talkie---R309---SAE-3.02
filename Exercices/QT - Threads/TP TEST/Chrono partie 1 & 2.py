import sys
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

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

    def start(self):
        self.line_edit1.setText("+1")
    
    def reset(self):
        self.line_edit1.setText("0")

    def quit(self):
        #sender pas forrcément nécessaire ici mais je pense plus propre avec 
        sender = self.sender()
        if sender is self.btn_quit: 
            sys.exit(app.exec_())
        
        
app = QApplication(sys.argv)
window = MainWindow()
window.resize(250, 250)
window.show()

if __name__ == '__main__':
    sys.exit(app.exec_())