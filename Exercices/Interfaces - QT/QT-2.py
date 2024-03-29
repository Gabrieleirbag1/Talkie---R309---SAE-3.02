import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QGridLayout, QPushButton, QComboBox, QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TempException(Exception):
    pass

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Conversion de température")


        self.label1 = QLabel("Température")
        self.line_edit1= QLineEdit(self)
        self.label2 = QLabel("°C")

        self.btn = QPushButton("Convertir")
        self.combobox = QComboBox()
        self.combobox.addItem("°C --> °K")
        self.combobox.addItem("°K --> °C")

        self.label3 = QLabel("Conversion")
        self.line_edit2= QLineEdit(self)
        self.line_edit2.setEnabled(False)
        self.label4 = QLabel("°K")

        self.dialog = QPushButton("?")
        self.btn_quit = QPushButton("Quitter")

        self.btn.clicked.connect(self.onClick)
        self.combobox.activated.connect(self.cork)
        self.dialog.clicked.connect(self.button_clicked)
        self.btn_quit.clicked.connect(self.quit)

        layout = QGridLayout()

        layout.addWidget(self.label1, 0, 0)
        layout.addWidget(self.line_edit1, 0, 1)
        layout.addWidget(self.label2, 0, 2)

        layout.addWidget(self.btn, 1, 1)
        layout.addWidget(self.combobox, 1, 2)
        
        layout.addWidget(self.label3, 2, 0)
        layout.addWidget(self.line_edit2, 2, 1)
        layout.addWidget(self.label4, 2, 2)

        layout.addWidget(self.btn_quit, 3, 1)
        layout.addWidget(self.dialog, 3, 2)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)
    
    def onClick(self):
        text = self.line_edit1.text()
        try:
            text = float(text)
            if self.combobox.currentText() == "°C --> °K":
                text = text + 273.15
                if text < 0:
                    self.line_edit2.setText("Invalid Input : Impossible values.")
                    raise TempException
            else :
                text = text - 273.15
                if text < -273.15:
                    self.line_edit2.setText("Invalid Input : Impossible Values.")
                    raise TempException
                    
                
            self.line_edit2.setText(str(text))
        except ValueError:
            self.line_edit2.setText("Invalid Input : Caracters not allowed.")
            self.errorBox()
    
    def cork(self):
        if self.combobox.currentText() == "°C --> °K":
            self.label2.setText(str("°C"))
            self.label4.setText(str("°K"))
        else:
            self.label2.setText(str("°K"))
            self.label4.setText(str("°C"))
            
        
    def button_clicked(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Aide")
        dlg.setText("Permet de convertir des Celsius en Kelvin et inversement.")
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