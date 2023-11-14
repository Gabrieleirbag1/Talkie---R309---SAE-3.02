import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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

        self.btn_quit = QPushButton("Quitter")

        layout = QVBoxLayout()

        layout.addWidget(self.label1)
        layout.addWidget(self.line_edit1)
        layout.addWidget(self.label2)

        self.btn.clicked.connect(self.onClick)

        self.btn_quit.clicked.connect(self.quit)

        layout.addWidget(self.btn)
        layout.addWidget(self.combobox)

        layout.addWidget(self.label3)
        layout.addWidget(self.line_edit2)
        layout.addWidget(self.label4)

        
        layout.addWidget(self.btn_quit)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)
    
    def onClick(self):
        text = self.line_edit1.text()
        try:
            text = float(text)
            if self.combobox.currentText() == "°C --> °K":
                text = text + 273.15
            else :
                text = text - 273.15
                
            self.line_edit2.setText(str(text))
        except ValueError:
            self.line_edit2.setText("Invalid Input")

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