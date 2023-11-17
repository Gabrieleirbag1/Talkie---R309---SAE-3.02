import sys, threading, socket, time
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QGridLayout, QPushButton, QComboBox, QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Client")


        self.label1 = QLabel("Messagerie")
        self.line_edit1= QLineEdit(self)
        self.label2 = QLabel("Réponse du Serveur")
        self.line_edit2= QLineEdit(self)

        self.btn = QPushButton("Envoyer")
        self.line_edit2.setEnabled(False)

        self.dialog = QPushButton("?")
        self.btn_quit = QPushButton("Quitter")

        self.btn.clicked.connect(self.onClick)
        self.dialog.clicked.connect(self.button_clicked)
        self.btn_quit.clicked.connect(self.quit)

        layout = QGridLayout()

        layout.addWidget(self.label1, 0, 0)
        layout.addWidget(self.line_edit1, 1, 0)
        layout.addWidget(self.label2, 2, 0)
        layout.addWidget(self.line_edit2, 3, 0)

        layout.addWidget(self.btn, 4, 0)
        layout.addWidget(self.btn_quit, 4, 1)
        layout.addWidget(self.dialog, 4, 2)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)
    
    def onClick(self):
        text = self.line_edit1.text()
            
        
    def button_clicked(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Aide")
        dlg.setText("Envoyer un message pour utiliser la messagerie.")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Question)
        dlg.exec()
    
    def errorBox(self):
        error = QMessageBox(self)
        error.setWindowTitle("Erreur")
        error.setText("La valeur entrée n'est pas valide, la température doit être un réel.")
        error.exec()

    def quit(self):
        #sender pas forrcément nécessaire ici mais je pense plus propre avec 
        sender = self.sender()
        if sender is self.btn_quit: 
            sys.exit(app.exec_())

app = QApplication(sys.argv)
window = MainWindow()
window.resize(450, 450)
window.show()


if __name__ == '__main__':
    sys.exit(app.exec_())