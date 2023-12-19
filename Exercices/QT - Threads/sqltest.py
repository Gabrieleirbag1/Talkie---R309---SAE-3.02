import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QTextEdit

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Création de la liste widget à gauche
        self.button_list = QListWidget()

        # Création du layout principal
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Layout pour les boutons à gauche
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Layout pour les text edits à droite
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        # Bouton "Ajouter"
        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.addNewButton)
        left_layout.addWidget(add_button)

        # Ajout d'un bouton initial à la liste
        self.addButton("Bouton 1")

        # Événement de clic sur les boutons
        self.button_list.itemClicked.connect(self.showTextEdit)

        self.show()

    def addButton(self, button_text):
        # Ajout d'un bouton à la liste
        button = QPushButton(button_text)
        self.button_list.addItem(button)

    def showTextEdit(self, item):
        # Récupération du texte du bouton
        button_text = item.text()

        # Création d'un nouvel objet QTextEdit
        text_edit = QTextEdit(f"Contenu du {button_text}")

        # Ajout du QTextEdit au layout de droite
        self.layout().itemAt(1).layout().addWidget(text_edit)

    def addNewButton(self):
        # Récupération du nombre actuel de boutons dans la liste
        button_count = self.button_list.count()

        # Ajout d'un nouveau bouton à la liste
        self.addButton(f"Bouton {button_count + 1}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    sys.exit(app.exec_())
