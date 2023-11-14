import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QPushButton

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Name Finder")


        self.label1 = QLabel("Saisir votre nom")
        self.btn = QPushButton("Ok")
        self.btn_quit = QPushButton("Quitter")
        self.line_edit1= QLineEdit(self)
        self.label2 = QLabel()

        layout = QVBoxLayout()

        layout.addWidget(self.label1)
        layout.addWidget(self.line_edit1)


        self.btn.clicked.connect(self.onClick)

        self.btn_quit.clicked.connect(self.quit)

        layout.addWidget(self.btn)
        layout.addWidget(self.label2)
        layout.addWidget(self.btn_quit)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def onClick(self):
        text = self.line_edit1.text()
        self.label2.setText("Bonjour " + text + " !")

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