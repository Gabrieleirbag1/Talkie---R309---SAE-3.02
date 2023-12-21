import sys
from PyQt5.QtWidgets import *

class UsersWidget(QWidget):
    def __init__(self, button_name, parent=None):
        super().__init__(parent)
        self.button_name = button_name
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        self.button1 = QPushButton("Bouton 1", self)
        self.button2 = QPushButton("Bouton 2", self)

        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        

class MessagerieWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Layout principal
        layout = QHBoxLayout(self)

        # Liste des boutons (1 tiers gauche)
        button_layout = QVBoxLayout()
        self.button_list = QListWidget(self)
        button_layout.addWidget(self.button_list)

        # Bouton Ajouter
        add_button = QPushButton("Ajouter", self)
        add_button.clicked.connect(self.add_button_clicked)
        button_layout.addWidget(add_button)

        # Ajout du layout des boutons au layout principal
        layout.addLayout(button_layout)

        # Layout du TextEdit (2 tiers droit)
        self.text_edit_layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        self.text_edit_layout.addWidget(self.text_edit)

        # Ajout du QLineEdit
        self.line_edit = QLineEdit(self)
        self.text_edit_layout.addWidget(self.line_edit)

        # Ajout du bouton "Envoyer"
        send_button = QPushButton("Envoyer", self)
        send_button.clicked.connect(self.send_button_clicked)
        self.text_edit_layout.addWidget(send_button)

        # Ajout du layout du TextEdit au layout principal
        layout.addLayout(self.text_edit_layout)

        # Ajustement des proportions (2 tiers - 1 tiers)
        layout.setStretch(0, 1)
        layout.setStretch(1, 2)

        self.setLayout(layout)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Messagerie')

    def send_button_clicked(self):
        # Récupère le texte du QLineEdit et l'ajoute au QTextEdit
        text_to_append = self.line_edit.text()
        if text_to_append:
            current_text = self.text_edit.toPlainText()
            self.text_edit.setPlainText(f"{current_text}\n{text_to_append}")
            self.line_edit.clear()


    def add_button_clicked(self):
        # Ajoute un nouvel élément à la liste
        new_button_name = f"Bouton {self.button_list.count() + 1}"
        button_widget = UsersWidget(new_button_name)
        item = QListWidgetItem(self.button_list)
        item.setSizeHint(button_widget.sizeHint())
        self.button_list.setItemWidget(item, button_widget)

        # Connecte le signal pressed du bouton 2 à l'affichage du TextEdit
        button_widget.button2.clicked.connect(lambda: self.show_text_edit(button_widget))

    def show_text_edit(self, button_widget):
        # Change le contenu du TextEdit en fonction du bouton cliqué
        button_name = button_widget.button_name
        self.text_edit.setPlainText(f"Contenu pour {button_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MessagerieWindow()
    window.show()
    sys.exit(app.exec_())



'''CRÉE UN DICTIONNAIRE POUR STOCKER POUR CHAQUE TEXT EDIT'''