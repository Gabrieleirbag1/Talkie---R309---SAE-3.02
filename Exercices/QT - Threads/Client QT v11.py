from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, socket, time, datetime, os, re


def get_address_ip():
    # utilisation d'un DNS public pour obtenir l'adresse IP externe
    try:
        address_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address_socket.connect(("8.8.8.8", 80))
        address_ip = address_socket.getsockname()[0]
        address_socket.close()
        print(address_ip)
        return address_ip
    except socket.error:
        return None


host, port = (str(get_address_ip()), 11111) #l'adresse est récupéré sur le réseau
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

flag = False #variable globale pour fermer le thread de réception du client

receiver_thread = None #variable globale permettant de récupérer les signaux de l'instance du thread de réception

#variables servant à ouvrir les autres fenêtres
MainWindow = None
username = None
password = None
signup_window = None
photo_window = None
Courrierwindow = None
Profilwindow = None
Userprofilwindow = None

#les variables mois servent pour afficher la date dans les chats
mois= None
mois2 = None
mois3 = None
mois4 = None
mois5 = None

users_list = []#liste des utilisateurs lors de la connexion du client

#dictionnaire contenant les emojis servant d'image de profil correspondant aux noms dans la bdd
photo_dico = {"Nom": ["bear", "christmas", "demon", "nerd", "skull", "caca", "grenouille", "chien", "bomb", "clown", "fleur", "tortue"], "Photo": ["🐻", "🎅", "👿", "🤓", "💀", "💩", "🐸", "🐶", "💣", "🤡", "🌸", "🐢"]}

all_private = {"Private" : [], "User": [], "Mois": []} #dictionnaire contenant tous les msg privés

class SenderThread(QThread):
    """Cette classe est un Thread qui gère l'envoi de messages vers le serveur.

    Attributes:
        message (str): Variable string, récupère le message qui va être envoyé au client.

    Methods:
        run(): La méthode run permet de lancer le QThread d'envoi de message.  
    """
    error_connected = pyqtSignal(str, str)#envoi le signal d'erreur de connexion lorsque le serveur n'est pas joignable
    def __init__(self, message):
        """Initialise une nouvelle instance de la classe SenderThread.

        Args:
            message: La valeur initiale provient de différentes classe.
        
        """
        super().__init__()
        self.message = message

    def run(self):
        """
        run(): La méthode run permet de lancer le QThread d'envoi de message.
        """
        global flag, client_socket
        print("SenderThread up")
        print(self.message)
        try:
            client_socket.send(self.message.encode())

            if self.message == "/bye":
                print("Arret du serveur")
                flag = True
                self.quitter()

        except ConnectionRefusedError as error:
            print(error)

        except ConnectionResetError as error:
            print(error)

        except BrokenPipeError:
            print("Serveur non accessible")
            self.error_connected.emit("16", None)
        print("SenderThread ends")
                    

class ReceptionThread(QThread): #cette classe est un thread
    """Cette classe est un Thread qui gère la reception de messages du serveur.

    Methods:
        run(): La méthode run permet de lancer le QThread de reception de message.

        ajouter_private(all_private, user, code): Ajoute au dictionnaire des message privés le message, privé, le contenu des messages, le date. 
        Ecas de nouvel utilisateur, nouvel élément dans les listes dictionnaires, sinon rajoute juste au contenu actuel à l'index de l'utilisateur déjà enregistré.

        quitter(): Permet de quitter l'instance du script.

    """
    message_received = pyqtSignal(str) #signal lors de la reception d'un message du serveur
    success_connected = pyqtSignal(str) #signal lors du succès de connexion
    users_sended = pyqtSignal(str) #signal lors de la réception de la liste utilisateur
    demande_received = pyqtSignal(str) #signal lors de la réception d'une nouvelle demande côté réception
    demandeliste_received = pyqtSignal(str) #signal lors de la réception d'une nouvelle demande côté envoi
    info_profil = pyqtSignal(str) #signal contenant les info du profil du client
    msg_private = pyqtSignal(str) #signal contenant les messages privés et avec qui
    new_user = pyqtSignal(str) #signal ajoutant un nouveau user à la liste du client lors de la création de celui-ci
    user_profil = pyqtSignal(str) #signal envoyant le profil d'un autre utilisateur 
    friends = pyqtSignal(str) #signal envoyant la liste d'amis
    delete_friend = pyqtSignal(str) #signal lors de la suppression d'un ami
    new_friend = pyqtSignal(str) #signal lors de l'ajout d'un ami
    def __init__(self):
        """Initialise une instance de la classe ReceptionThread"""
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
                    self.success_connected.emit(code[1])
                    #print(f'Reception de : {reply}')

                elif code[0] == "USERS":
                    users = f"{code[1]}|{code[2]}|{code[3]}"
                    self.users_sended.emit(users)
                    resultat = re.search(r'@([^| 👑]+)', code[2])
                    if resultat:
                        resultat_user = resultat.group(1)
                    users_list.append(resultat_user)
                    #print(f'Reception de : {users}')
                
                elif code[0] == "DEMANDE":
                    try:# dans le cas d'un autre format de demande ou y a pas le code 6
                        demande = f"{code[1]}|{code[2]}|{code[3]}|{code[4]}|{code[5]}|{code[6]}"
                    except:
                        demande = f"{code[1]}|{code[2]}|{code[3]}|{code[4]}|{code[5]}"
                    #print(f'Reception de : {reply} filtré en {demande}')
                    self.demande_received.emit(demande)

                elif code[0] == "DEMANDELISTE":
                    demande = f"{code[1]}|{code[2]}|{code[3]}|{code[4]}" #demandeur, type, concerne, date
                    #print(f'Reception de : {reply} filtré en {demande}')
                    self.demandeliste_received.emit(demande)

                elif code[0] == "PROFIL":
                    profil = f"{code[1]}|{code[2]}|{code[3]}|{code[4]}|{code[5]}|{code[6]}|{code[7]}"
                    print(f'Reception de : {reply} filtré en {profil}')
                    self.info_profil.emit(profil)

                elif code[0] == "PRIVATE":
                    #print(code)
                    #print(f"Reception de : {reply}")
                    if code[1] == code[5]:
                        user = code[2]
                    else:
                        user = code[1]

                    self.ajouter_private(all_private, user, code)

                elif code[0] == "USER_PROFIL":
                    profil = f"{code[1]}|{code[2]}|{code[3]}|{code[4]}|{code[5]}|{code[6]}|{code[7]}"
                    self.user_profil.emit(profil)

                elif code[0] == "NEW_USER":
                    reply = f"{code[1]}|{code[2]}"
                    #print(f"Reception de : {code} filtré en {reply}")
                    self.new_user.emit(reply)

                elif code[0] == "MSG_PRIVATE":
                    reply = f"{code[1]}|{code[2]}|{code[3]}|{code[4]}"
                    self.msg_private.emit(reply)

                elif code[0] == "FRIENDS":
                    reply = f"{code[1]}|{code[2]}"
                    print(reply)
                    self.friends.emit(reply)

                elif code[0] == "DELETE_FRIEND":
                    reply = f"{code[2]}"
                    #print(reply)
                    self.delete_friend.emit(reply)

                elif code[0] == "NEW_FRIEND":
                    reply = f"{code[1]}|{code[2]}"
                    #print(reply)
                    self.new_friend.emit(reply)

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

    def ajouter_private(self, all_private, user, code):
        """
        ajouter_private(all_private, user, code): Ajoute au dictionnaire des message privés le message, privé, le contenu des messages, le date. 
        Ecas de nouvel utilisateur, nouvel élément dans les listes dictionnaires, sinon rajoute juste au contenu actuel à l'index de l'utilisateur déjà enregistré."""
        date = code[4].split(" ")
        private = f"{date[1]} - {code[1]} ~~ {code[3]}"
        for index, existing_user in enumerate(all_private["User"]):
            if existing_user == user:
                if date[0] != all_private["Mois"][index]:
                    print(date[0])
                    print(all_private["Mois"][index])
                    all_private["Private"][index] = f'{all_private["Private"][index]}<br>───────────────────────{date[0]}──────────────────────'
                    all_private["Mois"][index] = date[0]
                all_private["Private"][index] = f'{all_private["Private"][index]}<br>{private}'
                return

        # Si l'utilisateur n'existe pas, ajouter une nouvelle entrée
        all_private["Private"].append(f"───────────────────────{date[0]}──────────────────────<br>{private}")
        all_private["User"].append(user)
        all_private["Mois"].append(date[0])

    def quitter(self):
        """
        quitter(): Permet de quitter l'instance du script.
        """
        QCoreApplication.instance().quit()

class ConnectThread(QThread):
    """Cette classe est un thread qui gère la connexion au serveur et qui va activer le thread de réception et d'envoi.
    
    Attributes:
        log (str): Variable string, récupère le text edit du premier onglet "tab" de la classe MainWindow.
        send (str): Variable string, récupère le line edit d'envoi du premier onglet "tab" de la classe MainWindow.
        connect (str): Variable string, récupère le bouton du premier onglet "tab" de la classe MainWindow.
        
        log2 (str): Variable string, récupère le text edit du deuxième onglet "tab" de la classe MainWindow.
        send2 (str): Variable string, récupère le line edit d'envoi du deuxième onglet "tab" de la classe MainWindow.
        connect2 (str): Variable string, récupère le bouton du deuxième onglet "tab" de la classe MainWindow.

        log3 (str): Variable string, récupère le text edit du troisième onglet "tab" de la classe MainWindow.
        send3 (str): Variable string, récupère le line edit d'envoi du troisième onglet "tab" de la classe MainWindow.
        connect3 (str): Variable string, récupère le bouton du troisième onglet "tab" de la classe MainWindow.

        log4 (str): Variable string, récupère le text edit du quatrième onglet "tab" de la classe MainWindow.
        send4 (str): Variable string, récupère le line edit d'envoi du quatrième onglet "tab" de la classe MainWindow.
        connect4 (str): Variable string, récupère le bouton du quatrième onglet "tab" de la classe MainWindow.

        log5 (str): Variable string, récupère le text edit du cinquième onglet "tab" de la classe MainWindow.
        send5 (str): Variable string, récupère le line edit d'envoi du cinquième onglet "tab" de la classe MainWindow.
        connect5 (str): Variable string, récupère le bouton du cinquième onglet "tab" de la classe MainWindow.
    
    Methods:
        run(): La méthode run permet de lancer le QThread de connexion de message.

        update_reply(message): Ajoute en fonction de l'entête le message dans le bon chat via le signal message_received, ou serveur dans tous les chats.
        
        check_date(date): vérifie la date du text edit du premier onglet.

        check_date2(date): vérifie la date du text edit du deuxième onglet.

        check_date3(date): vérifie la date du text edit du troisième onglet.

        check_date4(date): vérifie la date du text edit du quatrième onglet.
        
        check_date5(date): vérifie la date du text edit du cinquième onglet.

        sender(): Envoie le message du client au serveur en précisant le salon Général.

        sender2(): Envoie le message du client au serveur en précisant le salon Blabla.

        sender3(): Envoie le message du client au serveur en précisant le salon Comptabilité.
        
        sender4(): Envoie le message du client au serveur en précisant le salon Informatique.

        sender5(): Envoie le message du client au serveur en précisant le salon Marketing.
        
        quitter(): Envoie le message bye au serveur qui comprend qui comprendra qu'il doit fermer le client.
    """
    def __init__(self, log, send, connect, log2, send2, connect2, log3, send3, connect3, log4, send4, connect4, log5, send5, connect5):
        """Initialise une instance de la classe ConnectThread
        
        Args:
            log: La valeur initiale du text edit vient de la classe MainWindow.
            send: La valeur initiale du line edit vient de la classe MainWindow.
            connect: La valeur initiale du bouton vient de la classe MainWindow.

            log2: La valeur initiale du text edit vient de la classe MainWindow.
            send2: La valeur initiale du line edit  vient de la classe MainWindow.
            connect2: La valeur initiale du bouton vient de la classe MainWindow.
            
            log3: La valeur initiale du text edit vient de la classe MainWindow.
            send3: La valeur initiale du line edit vient de la classe MainWindow.
            connect3: La valeur initiale du bouton vient de la classe MainWindow.

            log4: La valeur initiale du text edit vient de la classe MainWindow.
            send4: La valeur initiale du line edit vient de la classe MainWindow.
            connect4: La valeur initiale du bouton vient de la classe MainWindow.
            
            log5: La valeur initiale du text edit vient de la classe MainWindow.
            send5: La valeur initiale du line edit vient de la classe MainWindow.
            connect5: La valeur initiale du bouton vient de la classe MainWindow.
        """
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
        """
        run(): La méthode run permet de lancer le QThread de connexion de message.
        """
        print("ConnectThread Up")
        global client_socket, receiver_thread
        try:
            client_socket.connect((host, port))
            self.connect.connect(self.sender)
            self.connect2.connect(self.sender2)
            self.connect3.connect(self.sender3)
            self.connect4.connect(self.sender4)
            self.connect5.connect(self.sender5)

            self.send.returnPressed.connect(self.sender)
            self.send2.returnPressed.connect(self.sender2)
            self.send3.returnPressed.connect(self.sender3)
            self.send4.returnPressed.connect(self.sender4)
            self.send5.returnPressed.connect(self.sender5)
            

            receiver_thread.message_received.connect(self.update_reply)    
            receiver_thread.start()

        except Exception as err: #pour retenter de se connecter jusqu'à ce qu'il y arrive
            print(err)
            time.sleep(5)
            self.run()

        
    def update_reply(self, message):
        """
        update_reply(message): Ajoute en fonction de l'entête le message dans le bon chat via le signal message_received, ou serveur dans tous les chats.
        """
        message = message.split("|")
        entete = message[1].split("-")
        date = entete[0].split(" ")

        if message[0] == 'Général':
            if self.check_date(date[0]):
                self.log.append(f'──────────────────────────────────{date[0]}──────────────────────────────────')
            self.log.append(f'{date[1]} -{entete[1]} {message[2]}')

        elif message[0] == 'Blabla':
            if self.check_date2(date[0]):
                self.log2.append(f'──────────────────────────────────{date[0]}──────────────────────────────────')
            self.log2.append(f'{date[1]} -{entete[1]} {message[2]}')
        
        elif message[0] == 'Comptabilité':
            if self.check_date3(date[0]):
                self.log3.append(f'──────────────────────────────────{date[0]}──────────────────────────────────')
            self.log3.append(f'{date[1]} -{entete[1]} {message[2]}') 
        
        elif message[0] == 'Informatique':
            if self.check_date4(date[0]):
                self.log4.append(f'──────────────────────────────────{date[0]}──────────────────────────────────')
            self.log4.append(f'{date[1]} -{entete[1]} {message[2]}')
        
        elif message[0] == 'Marketing':
            if self.check_date5(date[0]):
                self.log5.append(f'──────────────────────────────────{date[0]}──────────────────────────────────')
            self.log5.append(f'{date[1]} -{entete[1]} {message[2]}')

        elif message[0] == 'Serveur':
            self.log.append(f'<b>{date[1]} -{entete[1]} {message[2]}</b>')
            self.log2.append(f'<b>{date[1]} -{entete[1]} {message[2]}</b>')
            self.log3.append(f'<b>{date[1]} -{entete[1]} {message[2]}</b>')
            self.log4.append(f'<b>{date[1]} -{entete[1]} {message[2]}</b>')
            self.log5.append(f'<b>{date[1]} -{entete[1]} {message[2]}</b>')

    def check_date(self, date):
        """
        check_date(date): vérifie la date du text edit du premier onglet.
        """
        global mois
        if date != mois:
            mois = date
            return True
        else:
            return False
        
    def check_date2(self, date):
        """
        check_date2(date): vérifie la date du text edit du deuxième onglet.
        """
        global mois2
        if date != mois2:
            mois2 = date
            return True
        else:
            return False
        
    def check_date3(self, date):
        """
        check_date3(date): vérifie la date du text edit du troisième onglet.
        """
        global mois3
        if date != mois3:
            mois3 = date
            return True
        else:
            return False
        
    def check_date4(self, date):
        """
        check_date4(date): vérifie la date du text edit du quatrième onglet.
        """
        global mois4
        if date != mois4:
            mois4 = date
            return True
        else:
            return False
        
    def check_date5(self, date):
        """
        check_date5(date): vérifie la date du text edit du cinquième onglet.
        """
        global mois5
        if date != mois5:
            mois5 = date
            return True
        else:
            return False

    def sender(self):
        """
        sender(): Envoie le message du client au serveur en précisant le salon Général.
        """
        global client_socket, username, password
        reply = f"Général|{username}/{password}|{self.send.text()}"
        if self.send.text() != "" and not self.send.text().isspace():
            self.send.setText("")
            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()
    
    def sender2(self):
        """
        sender2(): Envoie le message du client au serveur en précisant le salon Blabla.
        """
        global client_socket, username, password
        reply = f"Blabla|{username}/{password}|{self.send2.text()}"
        if self.send2.text() != "" and not self.send2.text().isspace():
            self.send2.setText("")
            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()

    def sender3(self):
        """
        sender3(): Envoie le message du client au serveur en précisant le salon Comptabilité.
        """
        global client_socket, username, password
        reply = f"Comptabilité|{username}/{password}|{self.send3.text()}"
        if self.send3.text() != "" and not self.send3.text().isspace():
            self.send3.setText("")
            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()

    def sender4(self):
        """
        sender4(): Envoie le message du client au serveur en précisant le salon Informatique.
        """
        global client_socket, username, password
        reply = f"Informatique|{username}/{password}|{self.send4.text()}"
        if self.send4.text() != "" and not self.send4.text().isspace():
            self.send4.setText("")
            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()
    
    def sender5(self):
        """
        sender5(): Envoie le message du client au serveur en précisant le salon Marketing.
        """
        global client_socket, username, password
        reply = f"Marketing|{username}/{password}|{self.send5.text()}"
        if self.send5.text() != "" and not self.send5.text().isspace():
            self.send5.setText("")
            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()

    def quitter(self):
        """
        quitter(): Envoie le message bye au serveur qui comprend qui comprendra qu'il doit fermer le client.
        """
        reply = "bye"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

class Window(QObject):
    """Cette classe est la fenêtre principale du programme et est une QMainWindow.
    
    Methods:
        setup_window(MainWindow): Met en place l'interface de la fenêtre principale avec les onglets.
        
        friends_show(): Permet d'afficher la fenêtre de messagerie (où il y a les amis d'où son nom).

        courrier_window(): Permet d'afficher la fenêtre de reception et d'envoi du courrier.

        profil_window(): Permet d'afficher la fenêtre du profil de l'utilisateur.

        main_thread(): Lance le thread de connexion au serveur ConnectThread et lui passe tous les arguments text edit, line edit, bouton d'envoi.

        users_show(users): Affiche les utilisateurs dans le text edit de chaque salon si ils y ont accès, avec la nuance de couleur en fonction de s'ils ont une sanction, ou pas, ou qu'ils ont le grade admin.
    
        history_code(code): Récupère les codes d'erreurs de la fenêtre principale, renvoyant l'accès au salon premièrement, et aux fenêtre de type dialog d'erreur ou de succès.

        succesBox(code200, concerne): Fenêtre de type dialog affichant un succès d'accès salon suite à un code de réussite.

        succesBox2(code): Fenêtre de type dialog affichant un succès d'obtention des droits adminsuite à un code de réussite.

        errorBox(code): Fenêtre de type dialog affichant une erreur suite à un code d'erreur envoyé par le serveur. 

        quitter(): Permet de quitter l'instance du programme en cours.

        translate_window(MainWindow): Permet de donner à noms aux attributs des différents tab via la fonction translate de QT.

    """
    

    courrier_window_signal = pyqtSignal()
    global MainWindow #récupère l'instance de la cette classe qui est globle pour être exploitée partout
    def setup_window(self, MainWindow):
        """
        setup_window(MainWindow): Met en place l'interface de la fenêtre principale avec les onglets
        """
        global receiver_thread

        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_main.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()

        MainWindow.setStyleSheet(stylesheet)
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1000, 700)
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
        self.profil_button = QPushButton(self.tab)
        self.profil_button.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button.setObjectName("profil_button")
        self.profil_button.setFont(QFont('Arial', 40))
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
        self.text_edit2.setObjectName("text_edit2")
        self.text_edit2.setReadOnly(True)
        self.users_text_edit2 = QTextEdit(self.tab_2)
        self.users_text_edit2.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit2.setObjectName("users_text_edit2")
        self.users_text_edit2.setReadOnly(True)
        self.line_edit2 = QLineEdit(self.tab_2)
        self.line_edit2.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit2.setObjectName("lineEdit2")
        self.line_edit2.setMaxLength(255)
        self.label2 = QLabel(self.tab_2)
        self.label2.setGeometry(QRect(20, 510, 271, 41))
        self.label2.setMinimumSize(QSize(271, 21))
        self.label2.setFont(font)
        self.label2.setObjectName("label2")
        self.profil_button2 = QPushButton(self.tab_2)
        self.profil_button2.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button2.setObjectName("profil_button2")
        self.profil_button2.setFont(QFont('Arial', 40))
        self.courrier_button2 = QPushButton(self.tab_2)
        self.courrier_button2.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button2.setObjectName("courrier_button2")
        self.courrier_button2.setFont(QFont('Arial', 40))
        self.send_button2 = QPushButton(self.tab_2)
        self.send_button2.setGeometry(QRect(770, 560, 81, 51))
        self.send_button2.setObjectName("send_button2")
        self.friends_button2 = QPushButton(self.tab_2)
        self.friends_button2.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button2.setObjectName("friends_button2")
        self.tabWidget.addTab(self.tab_2, "Blabla")

        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.text_edit3 = QTextEdit(self.tab_3)
        self.text_edit3.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit3.setObjectName("text_edit3")
        self.text_edit3.setReadOnly(True)
        self.users_text_edit3 = QTextEdit(self.tab_3)
        self.users_text_edit3.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit3.setObjectName("users_text_edit3")
        self.users_text_edit3.setReadOnly(True)
        self.line_edit3 = QLineEdit(self.tab_3)
        self.line_edit3.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit3.setObjectName("lineEdit3")
        self.line_edit3.setMaxLength(255)
        self.label3 = QLabel(self.tab_3)
        self.label3.setGeometry(QRect(20, 510, 271, 41))
        self.label3.setMinimumSize(QSize(271, 21))
        self.label3.setFont(font)
        self.label3.setObjectName("label3")
        self.profil_button3 = QPushButton(self.tab_3)
        self.profil_button3.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button3.setObjectName("profil_button3")
        self.profil_button3.setFont(QFont('Arial', 40))
        self.courrier_button3 = QPushButton(self.tab_3)
        self.courrier_button3.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button3.setObjectName("courrier_button3")
        self.courrier_button3.setFont(QFont('Arial', 40))
        self.send_button3 = QPushButton(self.tab_3)
        self.send_button3.setGeometry(QRect(770, 560, 81, 51))
        self.send_button3.setObjectName("send_button3")
        self.friends_button3 = QPushButton(self.tab_3)
        self.friends_button3.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button3.setObjectName("friends_button3")
        self.tabWidget.addTab(self.tab_3, "Comptabilité")

        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.text_edit4 = QTextEdit(self.tab_4)
        self.text_edit4.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit4.setObjectName("text_edit4")
        self.text_edit4.setReadOnly(True)
        self.users_text_edit4 = QTextEdit(self.tab_4)
        self.users_text_edit4.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit4.setObjectName("users_text_edit4")
        self.users_text_edit4.setReadOnly(True)
        self.line_edit4 = QLineEdit(self.tab_4)
        self.line_edit4.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit4.setObjectName("lineEdit4")
        self.line_edit4.setMaxLength(255)
        self.label4 = QLabel(self.tab_4)
        self.label4.setGeometry(QRect(20, 510, 271, 41))
        self.label4.setMinimumSize(QSize(271, 21))
        self.label4.setFont(font)
        self.label4.setObjectName("label4")
        self.profil_button4 = QPushButton(self.tab_4)
        self.profil_button4.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button4.setObjectName("profil_button4")
        self.profil_button4.setFont(QFont('Arial', 40))
        self.courrier_button4 = QPushButton(self.tab_4)
        self.courrier_button4.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button4.setObjectName("courrier_button4")
        self.courrier_button4.setFont(QFont('Arial', 40))
        self.send_button4 = QPushButton(self.tab_4)
        self.send_button4.setGeometry(QRect(770, 560, 81, 51))
        self.send_button4.setObjectName("send_button4")
        self.friends_button4 = QPushButton(self.tab_4)
        self.friends_button4.setGeometry(QRect(872, 560, 81, 51))
        self.friends_button4.setObjectName("friends_button4")
        self.tabWidget.addTab(self.tab_4, "Informatique")

        self.tab_5 = QWidget()
        self.tab_5.setObjectName("tab_5")
        self.text_edit5 = QTextEdit(self.tab_5)
        self.text_edit5.setGeometry(QRect(20, 20, 721, 481))
        self.text_edit5.setObjectName("text_edit5")
        self.text_edit5.setReadOnly(True)
        self.users_text_edit5 = QTextEdit(self.tab_5)
        self.users_text_edit5.setGeometry(QRect(770, 110, 183, 390))
        self.users_text_edit5.setObjectName("users_text_edit5")
        self.users_text_edit5.setReadOnly(True)
        self.line_edit5 = QLineEdit(self.tab_5)
        self.line_edit5.setGeometry(QRect(20, 560, 721, 51))
        self.line_edit5.setObjectName("lineEdit5")
        self.line_edit5.setMaxLength(255)
        self.label5 = QLabel(self.tab_5)
        self.label5.setGeometry(QRect(20, 510, 271, 41))
        self.label5.setMinimumSize(QSize(271, 21))
        self.label5.setFont(font)
        self.label5.setObjectName("label5")
        self.profil_button5 = QPushButton(self.tab_5)
        self.profil_button5.setGeometry(QRect(770, 20, 81, 71))
        self.profil_button5.setObjectName("profil_button5")
        self.profil_button5.setFont(QFont('Arial', 40))
        self.courrier_button5 = QPushButton(self.tab_5)
        self.courrier_button5.setGeometry(QRect(872, 20, 81, 71))
        self.courrier_button5.setObjectName("courrier_button5")
        self.courrier_button5.setFont(QFont('Arial', 40))
        self.send_button5 = QPushButton(self.tab_5)
        self.send_button5.setGeometry(QRect(770, 560, 81, 51))
        self.send_button5.setObjectName("send_button5")
        self.friends_button5 = QPushButton(self.tab_5)
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

        self.translate_window(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(MainWindow)

        self.mainthread()
        receiver_thread = ReceptionThread()
        
        self.courrier_button.clicked.connect(self.courrier_window)
        self.courrier_button2.clicked.connect(self.courrier_window)
        self.courrier_button3.clicked.connect(self.courrier_window)
        self.courrier_button4.clicked.connect(self.courrier_window)
        self.courrier_button5.clicked.connect(self.courrier_window)

        self.profil_button.clicked.connect(self.profil_window)
        self.profil_button2.clicked.connect(self.profil_window)
        self.profil_button3.clicked.connect(self.profil_window)
        self.profil_button4.clicked.connect(self.profil_window)
        self.profil_button5.clicked.connect(self.profil_window)

        self.friends_button.clicked.connect(self.friends_window)
        self.friends_button2.clicked.connect(self.friends_window)
        self.friends_button3.clicked.connect(self.friends_window)
        self.friends_button4.clicked.connect(self.friends_window)
        self.friends_button5.clicked.connect(self.friends_window)

        try:
            receiver_thread.success_connected.connect(self.history_code)
            receiver_thread.users_sended.connect(self.users_show)
            receiver_thread.new_user.connect(self.users_show)
        except:
            pass
    
    def friends_window(self):
        """
        friends_show(): Permet d'afficher la fenêtre de messagerie (où il y a les amis d'où son nom).
        """
        m.show() #instance de la classe MessagerieWindow
    
    def courrier_window(self):
        """
        courrier_window(): Permet d'afficher la fenêtre de reception et d'envoi du courrier.
        """
        global Courrierwindow
        Courrierwindow.show()

    def profil_window(self):
        """
        profil_window(): Permet d'afficher la fenêtre du profil de l'utilisateur.
        """
        global Profilwindow
        Profilwindow.show()
    
    def mainthread(self):
        """
        main_thread(): Lance le thread de connexion au serveur ConnectThread et lui passe tous les arguments text edit, line edit, bouton d'envoi.
        """
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


    def users_show(self, users):
        """
        users_show(users): Affiche les utilisateurs dans le text edit de chaque salon si ils y ont accès, avec la nuance de couleur en fonction de s'ils ont une sanction, ou pas, ou qu'ils ont le grade admin.
        """
        users = users.split("|")
        print(users)
        color = "green"
        if users[0] == "Général":
            try:
                if users[2] == "ban":
                    color = "red"
                    self.users_text_edit.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                elif users[2] == "kick":
                    color = "orange"
                    self.users_text_edit.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                else:
                    self.users_text_edit.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')
            except IndexError:
                self.users_text_edit.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')

        elif users[0] == "Blabla":
            try:
                if users[2] == "ban":
                    color = "red"
                    self.users_text_edit2.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                elif users[2] == "kick":
                    color = "orange"
                    self.users_text_edit2.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                else:
                    self.users_text_edit2.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')
            except IndexError:
                self.users_text_edit2.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')

        elif users[0] == "Comptabilité":
            try:
                if users[2] == "ban":
                    color = "red"
                    self.users_text_edit3.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                elif users[2] == "kick":
                    color = "orange"
                    self.users_text_edit3.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                else:
                    self.users_text_edit3.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')
        
            except IndexError:
                self.users_text_edit3.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')

        elif users[0] == "Informatique":
            try:
                if users[2] == "ban":
                    color = "red"
                    self.users_text_edit4.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                elif users[2] == "kick":
                    color = "orange"
                    self.users_text_edit4.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                else:
                    self.users_text_edit4.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')
            except IndexError:
                self.users_text_edit4.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')
                
        elif users[0] == "Marketing":
            try:
                if users[2] == "ban":
                    color = "red"
                    self.users_text_edit5.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                elif users[2] == "kick":
                    color = "orange"
                    self.users_text_edit5.append(f'<font color="{color}"><s>{users[1]}</s></font>\n──────────────────')
                else:
                    self.users_text_edit5.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')
            except IndexError:
                self.users_text_edit5.append(f'<font color="{color}">{users[1]}</font>\n──────────────────')
        

    def history_code(self, code):
        """
        history_code(code): Récupère les codes d'erreurs de la fenêtre principale, renvoyant l'accès au salon premièrement, et aux fenêtre de type dialog d'erreur ou de succès.
        """
        try:
            try:
                code20 = code.split("/")
                code200 = code20[0]
            except:
                pass

            try:
                if int(code) > 9:
                    if code == '10':
                        self.tabWidget.setTabEnabled(0, False)
                        self.tabWidget.Colo
                    
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
                    
                    elif code == "31":
                        self.successBox2(code)
            except:
                if int(code200) == 27:
                    if code20[1] == "Blabla":
                        self.tabWidget.setTabEnabled(1, True)
                    elif code20[1] == "Comptabilité":
                        self.tabWidget.setTabEnabled(2, True)
                    elif code20[1] == "Informatique":
                        self.tabWidget.setTabEnabled(3, True)
                    elif code20[1] == "Marketing":
                        self.tabWidget.setTabEnabled(4, True)

                    self.successBox(code200, code20[1])
                else:
                    pass
        except:
            pass

    def successBox(self, code200, concerne):
        """
        succesBox(code200, concerne): Fenêtre de type dialog affichant un succès d'accès salon suite à un code de réussite.
        """
        success = QMessageBox()
        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        success.setStyleSheet(stylesheet)

        success.setWindowTitle("Succès")
        content = f"Vous avez à présent acces au salon {concerne} !"
        success.setIcon(QMessageBox.Information)
        success.setText(content)
        success.exec()
    
    def successBox2(self, code):
        """
        succesBox2(code): Fenêtre de type dialog affichant un succès d'obtention des droits adminsuite à un code de réussite.
        """
        success = QMessageBox()
        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        success.setStyleSheet(stylesheet)

        success.setWindowTitle("Succès")
        content = f"Vous possédez maintenant les droits administrateurs."
        success.setIcon(QMessageBox.Information)
        success.setText(content)
        success.exec()

    def errorbox(self, code):
        """
        errorBox(code): Fenêtre de type dialog affichant une erreur suite à un code d'erreur envoyé par le serveur. 
        """
        error = QMessageBox()
        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        error.setStyleSheet(stylesheet)
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
            self.quitter()

    def quitter(self):
        """
        quitter(): Permet de quitter l'instance du programme en cours.
        """
        QCoreApplication.instance().quit()

    def translate_window(self, MainWindow):
        """
        translate_window(MainWindow): Permet de donner à noms aux attributs des différents tab via la fonction translate de QT.
        """
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Talkie"))
        self.label.setText(_translate("MainWindow", "Messagerie :"))
        self.profil_button.setText(_translate("MainWindow", "👤"))
        self.courrier_button.setText(_translate("MainWindow", "📨"))
        self.friends_button.setText(_translate("MainWindow", "💬"))
        self.send_button.setText(_translate("MainWindow", "↩"))

        self.label2.setText(_translate("MainWindow", "Messagerie :"))
        self.profil_button2.setText(_translate("MainWindow", "👤"))
        self.courrier_button2.setText(_translate("MainWindow", "📨"))
        self.friends_button2.setText(_translate("MainWindow", "💬"))
        self.send_button2.setText(_translate("MainWindow", "↩"))

        self.label3.setText(_translate("MainWindow", "Messagerie :"))
        self.profil_button3.setText(_translate("MainWindow", "👤"))
        self.courrier_button3.setText(_translate("MainWindow", "📨"))
        self.friends_button3.setText(_translate("MainWindow", "💬"))
        self.send_button3.setText(_translate("MainWindow", "↩"))

        self.label4.setText(_translate("MainWindow", "Messagerie :"))
        self.profil_button4.setText(_translate("MainWindow", "👤"))
        self.courrier_button4.setText(_translate("MainWindow", "📨"))
        self.friends_button4.setText(_translate("MainWindow", "💬"))
        self.send_button4.setText(_translate("MainWindow", "↩"))

        self.label5.setText(_translate("MainWindow", "Messagerie :"))
        self.profil_button5.setText(_translate("MainWindow", "👤"))
        self.courrier_button5.setText(_translate("MainWindow", "📨"))
        self.friends_button5.setText(_translate("MainWindow", "💬"))
        self.send_button5.setText(_translate("MainWindow", "↩"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Général"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Blabla"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Comptabilité"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Informatique"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "Marketing"))


class Login(QMainWindow):
    """Cette classe affiche la fenêtre de Login.

    Methods:
        setup_window(): Création des éléments de la fenêtre de Login.

        auth(): Envoie les informations de connexions au serveur avec l'entête LOGIN.

        login(code): Gère les codes d'erreur de la fenêtre de log in.

        signup_window(): Envoie le signal permettant d'ouvrir la fenêtre d'inscription.

        quitter(): Permet de fermer la fenêtre de login.

        errorBox(code): Fenêtre de type dialog affichant une erreur suite à un code d'erreur envoyé par le serveur. 

    """
    signup_window_signal = pyqtSignal() #signal permettant d'afficher la fenêtre d'inscription
    def __init__(self, parent=None):
        """Initialise une instance de la classe Login."""
        super(Login, self).__init__(parent)

        self.setup_window()

    def setup_window(self):
        """
        setup_window(): Création des éléments de la fenêtre de Login.
        """
        global receiver_thread
        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        self.setStyleSheet(stylesheet)

        self.setObjectName("Login")
        self.setFixedSize(400, 300)
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
        """
        auth(): Envoie les informations de connexions au serveur avec l'entête LOGIN.
        """
        global username, password
        username = self.username.text()
        password = self.password.text()
        reply = f"LOGIN|{username}/{password}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.error_connected.connect(self.errorBox)
        self.sender_thread.start()
        self.sender_thread.wait()
    
    def login(self, code):
        """
        login(code): Gère les codes d'erreur de la fenêtre de log in.
        """
        global MainWindow, signup_window
        try:
            code20 = code.split("/")
            code200 = code20[0]
        except:
            code20 = [1, 1]
            code200 = '20'

        try:
            if int(code) <= 3 or int(code) == 19:
                if code == '1':
                    time.sleep(1)
                    MainWindow.show()
                    try:
                        signup_window.close()
                    except:
                        pass
                    self.quitter()
                else:
                    self.errorBox(code, code20)
        except:
            if int(code200) == 20:
                self.errorBox(code, code20)
            else:
                pass

    def signup_window(self):
        """
        signup_window(): Envoie le signal permettant d'ouvrir la fenêtre d'inscription.
        """
        self.signup_window_signal.emit()
        
    def quitter(self):
        """
        quitter(): Permet de fermer la fenêtre de login.
        """
        self.close()

    def errorBox(self, code, code20):
        """
        errorBox(code): Fenêtre de type dialog affichant une erreur suite à un code d'erreur envoyé par le serveur. 
        """
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
    """Cette classe permet d'afficher la fenêtre d'inscription.
    
    Methods:
        setup_window(): Création des éléments de la fenêtre d'inscription.
        
    """
    def __init__(self, parent=None):
        """Initialise une instance de la classe Sign_up()"""
        super(Sign_up, self).__init__(parent)

        self.setup_window()

    def setup_window(self):
        """
        setup_window(): Création des éléments de la fenêtre d'inscription.

        sign_up(): Envoie les informations d'inscription avec l'entête SIGNUP.

        sign_code(code): Renvoie à la fenêtre de succès si l'inscription est réussie.

        errorBox(code): Fenêtre d'erreur en cas d'échec de l'inscription.

        succesbox(code): Fenêtre de succès d'inscription.

        quitter(): Permet de quitter la fenêtre du programme.
        """
        global receiver_thread

        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        self.setStyleSheet(stylesheet)

        self.setObjectName("Sign_up")
        self.setFixedSize(432, 593)
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

        self.line_edit.returnPressed.connect(self.sign_up)
        self.line_edit_2.returnPressed.connect(self.sign_up)
        self.line_edit_3.returnPressed.connect(self.sign_up)
        self.line_edit_4.returnPressed.connect(self.sign_up)
        self.line_edit_5.returnPressed.connect(self.sign_up)

        self.signup_button = QPushButton(self)
        self.signup_button.setGeometry(QRect(150, 520, 140, 41))
        self.signup_button.setFont(font)
        self.signup_button.setObjectName("pushButton")
        self.signup_button.setText("S'inscrire")
        self.signup_button.clicked.connect(self.sign_up)

        receiver_thread.success_connected.connect(self.sign_code)

    def sign_up(self):
        """
        sign_up(): Envoie les informations d'inscription avec l'entête SIGNUP.
        """
        try:
            username = self.line_edit.text()
            alias = self.line_edit_2.text()
            mail = self.line_edit_3.text()
            mdp = self.line_edit_4.text()
            cmdp = self.line_edit_5.text()
            
            reply = f"SIGNUP|{username}/{alias}/{mail}/{mdp}/{cmdp}"
            
            if username != "" and alias != "" and mdp != "":
                self.sender_thread = SenderThread(reply)
                self.sender_thread.start()
                self.sender_thread.wait()

        except Exception as e:
            print(e)

    def sign_code(self, code):
        """
        sign_code(code): Renvoie à la fenêtre de succès si l'inscription est réussie.
        """
        if code == '4':
            self.successBox(code)
        else:
            self.errorBox(code)

    def errorBox(self, code):
        """
        errorBox(code): Renvoie à la fenêtre d'erreur en cas d'échec de l'inscription.
        """
        error = QMessageBox(self)
        error.setWindowTitle("Erreur")

        if code == '5':
            content = "(5) Les mots de passes ne correspondent pas"
        elif code == '6':
            content = "(6) Le mail ne respecte pas le format"
        elif code == '8':
            content = "(8) L'utilisateur existe déjà, votre identifiant doit être unique. Votre nom d'utilisateur est peut-être interdit."
        elif code == '9':
            content = "(9) Les caractères ne sont pas autorisés : %, #, &, ', [espace]"
        else:
            return

        error.setIcon(QMessageBox.Warning)
        error.setText(content)
        error.exec()

    def successBox(self, code):
        """
        succesbox(code): Fenêtre de succès d'inscription.
        """
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
        """
        quitter(): Permet de quitter la fenêtre du programme.
        """
        self.close()

class CourrierWidget(QWidget):
    """Cette classe est un élément de la QListWidget de la classe QCourrierWindow(), côté onglet envoi.

    Attributes:
        text (str): Variable string, récupère le contenu du message de la demande.
        readonly (bool): Variable bool, permet de reconnaître si les éléments Qt seront simplement lisibles ou pas.
        concerne (str): Variable string, permet de savoir quelle est le type de la demande.
    
    Methods:
        setup_window(text): Crée l'interface graphique de l'élément de la QListWidget, avec le texte de la demande, et en vérifiant le type.

        demande(): En vérifiant le type de demande, redirige vers les fonctions qui envoient la requête au serveur et modifie l'état graphique sur le serveur pour la clarté.
    
        demande_salon(username): Envoie la requête de demande de salon au serveur via le SenderThread().

        demande_admin(username): Envoie la requête de demande des droits admin au serveur via le SenderThread().

        demande_amiusername): Envoie la requête de demande d'ami au serveur via le SenderThread().
        
    """
    def __init__(self, text, readonly, concerne):
        """Initialise une instance la classe CourrierWidget
        
        Args:
            text: Valeur initiale récupérée de la fonction add_line_widget qui a obtenu la valeur via un signal du thread de réception, et via add_demandeliste lorsque la demande est ajoutée manuellement depuis le client
            readonly: Valeur initiale obtenue depuis add_demandeliste lors de la connexion du client.
            concerne: Valeur initiale obtenue via add_demandeliste et add_line_widget.
        """
        super().__init__()

        self.text = text
        self.readonly = readonly
        self.concerne = concerne

        self.setup_window(text)

    def setup_window(self, text):
        """
        setup_window(text): Crée l'interface graphique de l'élément de la QListWidget, avec le texte de la demande, et en vérifiant le type.
        """
        global type

        layout = QVBoxLayout(self)
        self.label = QLabel(text, self)

        if type == "Salon":
            self.comboBox = QComboBox(self)
            self.comboBox.addItem("")
            self.comboBox.addItem("Blabla")
            self.comboBox.addItem("Comptabilité")
            self.comboBox.addItem("Informatique")
            self.comboBox.addItem("Marketing")
            layout.addWidget(self.comboBox)


        elif type == "Ami":
            self.line_edit = QLineEdit(self)
            self.line_edit.setMaxLength(45)
            layout.addWidget(self.line_edit)
            self.line_edit.setText(self.concerne)

        layout.addWidget(self.label)

        print(self.readonly)
        if self.readonly:
            print("here")
            self.label.setEnabled(False)
            print("zozo")
            try:
                self.comboBox.setEnabled(False)
                self.comboBox.setCurrentText(self.concerne)
            except AttributeError:
                pass

            try:
                self.line_edit.setEnabled(False)
            except AttributeError:
                pass

        else:
            self.button = QPushButton("Envoyer", self)
            self.button.clicked.connect(self.demande)
            layout.addWidget(self.button)

            try:
                self.line_edit.returnPressed.connect(self.demande)
            except AttributeError:
                pass

    def demande(self):
        """
        demande(): En vérifiant le type de demande, redirige vers les fonctions qui envoient la requête au serveur et modifie l'état graphique sur le serveur pour la clarté.
        """
        global username
        try:
            if type == "Salon":
                self.demande_salon(username)
            elif type == "Admin":
                self.demande_admin(username)
                self.label.setEnabled(False)
                self.button.deleteLater()
            elif type == "Ami":
                if self.line_edit.text() != username and self.line_edit.text() != "" and self.line_edit.text() != " ":
                    self.demande_ami(username)
                    self.label.setEnabled(False)
                    self.line_edit.setEnabled(False)
                    self.button.deleteLater()
        except Exception as e:
            print(e)
        
        try:
            if self.comboBox.currentText() != "":
                self.label.setEnabled(False)
                self.button.deleteLater()
                self.comboBox.setEnabled(False)
        except AttributeError:
            pass
        


    def demande_salon(self, username):
        """
        demande_salon(username): Envoie la requête de demande de salon au serveur via le SenderThread().
        """
        if self.comboBox.currentText() != "":
            if self.comboBox.currentText() == "Blabla":
                reply = f"DEMANDE|{username}|SALON|Blabla"
            elif self.comboBox.currentText() == "Comptabilité":
                reply = f"DEMANDE|{username}|SALON|Comptabilité"
            elif self.comboBox.currentText() == "Informatique":
                reply = f"DEMANDE|{username}|SALON|Informatique"
            elif self.comboBox.currentText() == "Marketing":
                reply = f"DEMANDE|{username}|SALON|Marketing"
            else:
                print("Error demande salon")
                
            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()
        else:
            pass

    def demande_admin(self, username):
        """
        demande_admin(username): Envoie la requête de demande des droits admin au serveur via le SenderThread().
        """
        reply = f"DEMANDE|{username}|ADMIN"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def demande_ami(self, username):
        """
        demande_amiusername): Envoie la requête de demande d'ami au serveur via le SenderThread().
        """
        friend2 = self.line_edit.text()
        reply = f"DEMANDE|{username}|AMI|{friend2}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()


class CourrierReception(QWidget):
    """Cette classe est un élément de la QListWidget de la classe QCourrierWindow(), côté onglet réception.

    Attributes:
        text (str): Variable string, récupère le contenu du message de la demande.
        list_widget2 (str): Variable string, est l'instance de la QListWidget concernant l'onglet réception des demandes.
        item (str): Variable string, est l'élément de la QListWidget où est situé cette classe CourrierReception().

    Methods:
        setup_window(demande): Crée l'interface graphique du QWidget servant d'élément de la liste crée dans CourrierWindow() côté réception.

        accept(): Envoie la réponse de validation accept au serveur destiné au client visé.

        refuse(): Envoie la réponse de validation refuse au serveur destiné au client visé.
        
        delete(): Envoie la supprésion de la réponse de l'onglet réception au serveur.

        remove_from_list_widget(): Grâce à variable contenant de l'item de la liste; on supprime l'élément graphiquement chez le client.
    """
    def __init__(self, demande, text, list_widget2, item):
        """Initialise une instance de la classe CourrierReception().

        Args:
            text: Initialement obtenu depuis add_notifications quand le signal des demande côté réception est réceptionné, contenant cette variable text avant découpage.
            list_widget2: Variable initiale est une instance de QListWidget crée dans CourrierWindow et envoyé depuis add_notifications dans CourrierWindow(). 
            item: Élément de la liste QListWidget instance de la classe QListWidgetitem obtenu depuis add_notifications dans CourrierWindow(). 
        """
        super().__init__()

        self.text = text
        self.list_widget2 = list_widget2
        self.item = item

        self.setup_window(demande)

    def setup_window(self, demande):
        """
        setup_window(demande): Crée l'interface graphique du QWidget servant d'élément de la liste crée dans CourrierWindow() côté réception.
        """
        global type2, username
        layout = QVBoxLayout(self)
        print("setup notif")

        self.label = QLabel(demande, self)

        if type2 != "Reponse":
            self.ok_button = QPushButton("Accepter", self)
            self.ok_icon = QIcon.fromTheme('dialog-ok')  # Icône standard de "Ok"
            self.ok_button.setIcon(self.ok_icon)
            self.ok_button.clicked.connect(self.accept)

            self.not_ok_button = QPushButton("Refuser", self)
            self.not_ok_icon = QIcon.fromTheme('dialog-cancel')  # Icône standard de "Ok"
            self.not_ok_button.setIcon(self.not_ok_icon)
            self.not_ok_button.clicked.connect(self.refuse)

            layout.addWidget(self.label)
            layout.addWidget(self.ok_button)
            layout.addWidget(self.not_ok_button)
        
        else:
            self.delete_button = QPushButton("Supprimer", self)
            self.delete_button_icon = QIcon.fromTheme('dialog-cancel')
            self.delete_button.setIcon(self.delete_button_icon)
            self.delete_button.clicked.connect(self.delete)

            layout.addWidget(self.label)
            layout.addWidget(self.delete_button)

    def accept(self):
        """
        accept(): Envoie la réponse de validation accept au serveur destiné au client visé.
        """
        reply = self.text.split("|")
        reply = f"VALIDATE|{reply[0]}|{reply[1]}|{reply[2]}|{reply[3]}|ACCEPT"#demandeur, type, concerne, date
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
        self.remove_from_list_widget()

    def refuse(self):
        """
        refuse(): Envoie la réponse de validation refuse au serveur destiné au client visé.
        """
        reply = self.text.split("|")
        reply = f"VALIDATE|{reply[0]}|{reply[1]}|{reply[2]}|{reply[3]}|REFUSE"#demandeur, type, concerne, date
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
        self.remove_from_list_widget()

    def delete(self):
        """
        delete(): Envoie la supprésion de la réponse de l'onglet réception au serveur.
        """
        print("delete")
        print(self.text)
        reply = self.text.split("|")
        try:
            type = reply[4].split("/")
        except:
            pass
        reply = f"DELETE_REPONSE|{reply[0]}|{type[1]}|{username}|{reply[2]}|{type[0]}"#demandeur, type, concerne, date
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

        self.remove_from_list_widget()

    def remove_from_list_widget(self):
        """
        remove_from_list_widget(): Grâce à variable contenant de l'item de la liste; on supprime l'élément graphiquement chez le client.
        """
        row = self.list_widget2.row(self.item)
        self.list_widget2.takeItem(row)
        

class CourrierWindow(QObject):
    """Cette classe est la fenêtre de courrier avec un onglet réception, et un onglet envoi.
    
    Methods:
        setup_window(Courrierwindow): Affiche l'interface graphique de la fenêtre courrier avec notamment les onglets et les QlistWidget dedans.

        courrier(code): Renvoie les codes d'erreurs concernant les demandes vers la fonction qui affiche la fenêtre d'erreur.

        errorBox(code): Crée la fenêtre de type dialog contenant le message d'erreur.

        translate_window(Courrierwindow): Permet de donner à noms aux attributs des différents tab via la fonction translate de QT.

        add_line_widget(): Permet au client de créer une demande.

        add_demandeliste(demandeliste): Via le signal du thread de réception ajoute automatiquement toutes les demandes côté envoi faites précedemment par le client concerné lors de sa connexion.

        add_notifications(demande ): Via le signal du thread de réception ajoute automatiquement toutes les demandes côté réception faites précedemment par le client concerné lors de sa connexion.
        """
    global receiver_thread
    def setup_window(self, Courrierwindow):
        """
        setup_window(Courrierwindow): Affiche l'interface graphique de la fenêtre courrier avec notamment les onglets et les QlistWidget dedans.
        """
        Courrierwindow.setObjectName("Courrierwindow")
        Courrierwindow.setFixedSize(400, 300)

        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        Courrierwindow.setStyleSheet(stylesheet)

        self.tabWidget = QTabWidget(Courrierwindow)
        self.tabWidget.setGeometry(QRect(0, 0, 401, 291))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "Reception")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "Demande")

        self.pushButton = QPushButton(self.tab_2)
        self.pushButton.setGeometry(QRect(10, 210, 281, 41))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.add_line_widget)

        self.comboBox = QComboBox(self.tab_2)
        self.comboBox.addItem("")
        self.comboBox.addItem("Salon")
        self.comboBox.addItem("Admin")
        self.comboBox.addItem("Ami")
        self.comboBox.setGeometry(QRect(300, 210, 91, 41))

        self.line_widgets = []
        self.list_widget = QListWidget(self.tab_2)
        self.list_widget.setGeometry(QRect(10, 4, 381, 201))

        self.line_widgets2 = []
        self.list_widget2 = QListWidget(self.tab)
        self.list_widget2.setGeometry(QRect(10, 4, 381, 201))

        self.translate_window(Courrierwindow)
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(Courrierwindow)
        receiver_thread.success_connected.connect(self.courrier)

        receiver_thread.demande_received.connect(self.add_notifications)
        receiver_thread.demandeliste_received.connect(self.add_demandeliste)


    def courrier(self, code):
        """
        courrier(code): Renvoie les codes d'erreurs concernant les demandes vers la fonction qui affiche la fenêtre d'erreur.
        """
        if code == "26":
            self.errorBox(code)
        elif code == "28":
            self.errorBox(code)
        elif code == "29":
            self.errorBox(code)
        elif code == "30":
            self.errorBox(code)
        elif code == "32":
            self.errorBox(code)
        elif code == "33":
            self.errorBox(code)
        elif code == "34":
            self.errorBox(code)

    def errorBox(self, code):
        """
        errorBox(code): Crée la fenêtre de type dialog contenant le message d'erreur.
        """
        error = QMessageBox()
        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        error.setStyleSheet(stylesheet)
        error.setWindowTitle("Erreur")
        if code == '26':
            content = "(26) Vous avez déjà acces à ce salon."
        elif code == '28':
            content = "(28) Vous avez déjà fait cette demande."
        elif code == '29':
            content = "(29) L'utilisateur a déjà accès à ce salon."
        elif code == '30':
            content = "(30) Vous êtes déjà un super utilisateur."
        elif code == "32":
            content = "(32) Vous êtes déjà ami avec cet utilisateur."
        elif code == "33":
            content = "(33) L'utilisateur n'a pas été trouvé."
        elif code == "34":
            content = "(34) Cet utilisateur a déjà les droits administrateur."
        else:
            content = "Erreur inconnue"

        error.setText(content)
        error.setIcon(QMessageBox.Warning)
        error.exec()


    def translate_window(self, Courrierwindow):
        """
        translate_window(Courrierwindow): Permet de donner à noms aux attributs des différents tab via la fonction translate de QT.
        """
        _translate = QCoreApplication.translate
        Courrierwindow.setWindowTitle(_translate("Courrierwindow", "Boite aux lettres"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Courrierwindow", "Rception"))
        self.pushButton.setText(_translate("Courrierwindow", "Ajouter"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Courrierwindow", "Envoi"))

    def add_line_widget(self):
        """
        add_line_widget(): Permet au client de créer une demande.
        """
        global type
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        if self.comboBox.currentText() != "":
            if self.comboBox.currentText() == "Salon":
                text = f"{date}\nDemande d'accès à un salon"
                type = "Salon"
            elif self.comboBox.currentText() == "Admin":
                text = f"{date}\nDemande des droits d'administration"
                type = "Admin"
            elif self.comboBox.currentText() == "Ami":
                text = f"{date}\nDemande d'ami"
                type = "Ami"

            readonly = False
            line_widget = CourrierWidget(text, readonly, concerne = None)

            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(line_widget.sizeHint())  # Définir la hauteur de l'élément
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, line_widget)

            self.line_widgets.append(line_widget)
        else:
            pass

    def add_demandeliste(self, demandeliste):
        """
        add_demandeliste(demandeliste): Via le signal du thread de réception ajoute automatiquement toutes les demandes côté envoi faites précedemment par le client concerné lors de sa connexion.
        """
        global type
        print("add demandeliste")
        print(demandeliste)
        demandeliste = demandeliste.split("|")
        if demandeliste[1] == "Salon":
            text = f"{demandeliste[3]}\nDemande d'accès au salon {demandeliste[2]}."
            concerne = demandeliste[2]
            type = "Salon"

        elif demandeliste[1] == "Admin":
            text = f"{demandeliste[3]}\nDemande des droits d'administration."
            concerne = "Admin"
            type = "Admin"

        elif demandeliste[1] == "Ami":
            text = f"{demandeliste[3]}\nDemande d'ami."
            concerne = demandeliste[2]
            type = "Ami"

        readonly = True
        line_widget = CourrierWidget(text, readonly, concerne)

        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(line_widget.sizeHint())  # Définir la hauteur de l'élément
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, line_widget)
        self.line_widgets.append(line_widget)


    def add_notifications(self, demande):
        """
        add_notifications(demande ): Via le signal du thread de réception ajoute automatiquement toutes les demandes côté réception faites précedemment par le client concerné lors de sa connexion.
        """
        global type2
        text = demande
        demande = demande.split("|")
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        print("notif")
        print(demande)

        try:
            rep = demande[5]
        except:
            rep = 0

        if demande[1] == "Reponse" or rep == "1":
            type2 = "Reponse"
            reponse = demande[4].split("/")
            print(reponse)

            if demande[1] == "Ami":
                if reponse[0] == "0":
                    demande = f"{demande[3]}\n{demande[2]} a refusé votre demande d'ami."
                elif reponse[0] == '1':
                    demande = f"{demande[3]}\n{demande[2]} a accepté votre demande d'ami."
                text = text.split("|")
                text = f"{text[0]}|{text[1]}|{text[2]}|{text[3]}|{reponse[0]}/Ami|{text[5]}"
                print(text)

            elif reponse[1] == "Ami":
                if reponse[0] == "0":
                    demande = f"{demande[3]}\n{demande[2]} a refusé votre demande d'ami."
                elif reponse[0] == '1':
                    demande = f"{demande[3]}\n{demande[2]} a accepté votre demande d'ami."

            elif demande[2] == "Admin":
                if reponse[0] == "0":
                    demande = f"{demande[3]}\nLes droits administrateur vous ont été refusé."
                elif reponse[0] == '1':
                    demande = f"{demande[3]}\nLes droits administrateur vous ont été accordé."

            elif reponse[1] == "Salon":
                if reponse[0] == "0":
                    demande = f"{demande[3]}\nL'accès au salon {demande[2]} vous est refusé."
                elif reponse[0] == '1':
                    demande = f"{demande[3]}\nL'accès au salon {demande[2]} vous est accordé."

                    
        elif demande[1] == "Salon":   
            demande = f"{date}\n{demande[0]} demande l'accès au salon {demande[2]}."
            type2 = "Salon"

        elif demande[1] == "Admin":
            demande = f"{date}\n{demande[0]} demande les droits administrateur."
            type2 = "Admin"

        elif demande[1] == "Ami":
            demande = f"{date}\n{demande[0]} vous demande en ami"
            type2 = "Ami"

        item = QListWidgetItem(self.list_widget2)
        line_widget2 = CourrierReception(demande, text, self.list_widget2, item)
        item.setSizeHint(line_widget2.sizeHint())  # Définir la hauteur de l'élément
        self.list_widget2.addItem(item)
        self.list_widget2.setItemWidget(item, line_widget2)
        self.line_widgets2.append(line_widget2)

class ProfilWindow(QObject):
    """Cette classe est la fenêtre affichant la page de profil propre à l'utilisateur.
    
    Methods:
        setup_window(Profilwindow): Affiche l'interface graphique du profil de l'utilisateur.

        profil(info_profil): Via le signal depuis le thread de réception, obtient toutes les informations pour remplir les champs du profil. Cherche également dans le dictionnaire des photos pour trouver l'image correspondante.

        limit_text_length(): Permet de limiter la longueur de caractère maximum d'un text edit pour la description (qui n'a pas de fonction assignées par défaut.)
        
        description_update(): Permet d'envoyer la nouvelle description du client au serveur qui l'ajoute à la BDD. 
    
        photo_update(photo): Modifie la photo de profil (qui est un emoji).

        photo_show(): Permet d'afficher la fenêtre de choix de photo de profil.
    """
    global receiver_thread, photo_window
    def setup_window(self, Profilwindow):
        """setup_window(Profilwindow): Affiche l'interface graphique du profil de l'utilisateur."""
        Profilwindow.setObjectName("Profilwindow")
        Profilwindow.setWindowTitle("Profil")
        Profilwindow.setFixedSize(393, 326)

        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        Profilwindow.setStyleSheet(stylesheet)

        font = QFont()
        font.setPointSize(14)

        fontbold = QFont()
        fontbold.setPointSize(14)
        fontbold.setBold(True)

        fontunderline = QFont()
        fontunderline.setPointSize(14)
        fontunderline.setUnderline(True)

        self.username = QLabel(Profilwindow)
        self.username.setGeometry(QRect(20, 10, 190, 41))
        self.username.setFont(fontbold)
        self.username.setObjectName("username")

        self.alias = QLabel(Profilwindow)
        self.alias.setGeometry(QRect(20, 40, 171, 41))
        self.alias.setFont(font)
        self.alias.setObjectName("alias")

        self.mail = QLabel(Profilwindow)
        self.mail.setGeometry(QRect(20, 70, 171, 41))
        self.mail.setFont(fontunderline)
        self.mail.setObjectName("mail")

        self.description = QLabel(Profilwindow)
        self.description.setGeometry(QRect(20, 120, 171, 21))
        self.description.setFont(font)
        self.description.setObjectName("description")
        self.description.setText("Description :")

        self.description_text_edit = QTextEdit(Profilwindow)
        self.description_text_edit.setGeometry(QRect(20, 150, 351, 121))
        self.description_text_edit.setObjectName("description_text_edit")

        self.enregistrer_button = QPushButton(Profilwindow)
        self.enregistrer_button.setGeometry(QRect(280, 280, 89, 25))
        self.enregistrer_button.setObjectName("enregistrer_button")
        self.enregistrer_button.setText("Enregistrer")
        self.enregistrer_button.clicked.connect(self.description_update)

        self.photo = QPushButton(Profilwindow)
        self.photo.setGeometry(QRect(230, 0, 141, 151))
        font2 = QFont()
        font2.setPointSize(100)
        self.photo.setFont(font2)
        self.photo.setObjectName("photo")
        self.photo.setStyleSheet('''
            QPushButton {
                border: none;
                background-color: transparent; /* Couleur de fond */
            }
        ''')
        self.photo.clicked.connect(self.photo_show)

        font3 = QFont()
        font3.setPointSize(10)
        font3.setItalic(True)
        self.date_profil = QLabel(Profilwindow)
        self.date_profil.setGeometry(QRect(20, 280, 231, 21))
        self.date_profil.setFont(font3)
        self.date_profil.setObjectName("date_profil")

        self.description_text_edit.textChanged.connect(self.limit_text_length)
        receiver_thread.info_profil.connect(self.profil)
        photo_window.photo_change.connect(self.photo_update)
    
    def profil(self, info_profil):
        """
        profil(info_profil): Via le signal depuis le thread de réception, obtient toutes les informations pour remplir les champs du profil. Cherche également dans le dictionnaire des photos pour trouver l'image correspondante.
        """
        info_profil = info_profil.split("|")

        if info_profil[3] == "1":
            admin_icon = "👑"
        else:
            admin_icon = ""

        index_nom = photo_dico['Nom'].index(info_profil[6])
        photo = photo_dico['Photo'][index_nom]

        desc = None if info_profil[4] == "None" else info_profil[4]

        date = info_profil[5].split(" ")

        self.username.setText(f"@{info_profil[0]}{admin_icon}")
        self.alias.setText(info_profil[1])
        self.mail.setText(info_profil[2])
        self.photo.setText(photo)
        self.description_text_edit.setText(desc)
        self.date_profil.setText(f"Compte créé le {date[0]} à {date[1]}")

    def limit_text_length(self):
        """limit_text_length(): Permet de limiter la longueur de caractère maximum d'un text edit pour la description (qui n'a pas de fonction assignées par défaut.)"""
        max_length = 300
        current_length = len(self.description_text_edit.toPlainText())

        if current_length > max_length:
            cursor = self.description_text_edit.textCursor()
            cursor.deletePreviousChar()  # Supprimer le dernier caractère si la limite est dépassée

    def description_update(self):
        """
        description_update(): Permet d'envoyer la nouvelle description du client au serveur qui l'ajoute à la BDD. 
        """
        reply = f"PROFIL|Description|{self.description_text_edit.toPlainText()}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def photo_update(self, photo):
        """
        photo_update(photo): Modifie la photo de profil (qui est un emoji).
        """
        self.photo.setText(photo)

    def photo_show(self):
        """
        photo_show(): Permet d'afficher la fenêtre de choix de photo de profil.
        """
        photo_window.show()
    

class UserProfilWindow(QObject):
    """Cette classe est la fenêtre affichant la page de profil d'un autre utilisateur.
    
    Methods:
        setup_window(Userprofilwindow): Affiche l'interface graphique du profil de l'utilisateur.

        set_user_profil(profil): Via le signal depuis le thread de réception, obtient toutes les informations pour remplir les champs du profil. Cherche également dans le dictionnaire des photos pour trouver l'image correspondante.
        
    """
    global receiver_thread, photo_window
    def setup_window(self, Userprofilwindow):
        """
        setup_window(Userprofilwindow): Affiche l'interface graphique du profil de l'utilisateur.
        """
        Userprofilwindow.setObjectName("Profilwindow")
        Userprofilwindow.setWindowTitle("Profil")
        Userprofilwindow.setFixedSize(393, 326)

        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        Userprofilwindow.setStyleSheet(stylesheet)

        font = QFont()
        font.setPointSize(14)

        fontbold = QFont()
        fontbold.setPointSize(14)
        fontbold.setBold(True)

        fontunderline = QFont()
        fontunderline.setPointSize(14)
        fontunderline.setUnderline(True)

        self.username = QLabel(Userprofilwindow)
        self.username.setGeometry(QRect(20, 10, 171, 41))
        self.username.setFont(fontbold)
        self.username.setObjectName("username")

        self.alias = QLabel(Userprofilwindow)
        self.alias.setGeometry(QRect(20, 40, 171, 41))
        self.alias.setFont(font)
        self.alias.setObjectName("alias")

        self.mail = QLabel(Userprofilwindow)
        self.mail.setGeometry(QRect(20, 70, 171, 41))
        self.mail.setFont(fontunderline)
        self.mail.setObjectName("mail")

        self.description = QLabel(Userprofilwindow)
        self.description.setGeometry(QRect(20, 120, 171, 21))
        self.description.setFont(font)
        self.description.setObjectName("description")
        self.description.setText("Description :")

        self.description_text_edit = QTextEdit(Userprofilwindow)
        self.description_text_edit.setGeometry(QRect(20, 150, 351, 121))
        self.description_text_edit.setObjectName("description_text_edit")
        self.description_text_edit.setReadOnly(True)

        self.photo = QPushButton(Userprofilwindow)
        self.photo.setGeometry(QRect(230, 0, 141, 151))
        font2 = QFont()
        font2.setPointSize(100)
        self.photo.setFont(font2)
        self.photo.setObjectName("photo")
        self.photo.setStyleSheet('''
            QPushButton {
                border: none;
                background-color: transparent; /* Couleur de fond */
            }
        ''')

        font3 = QFont()
        font3.setPointSize(10)
        font3.setItalic(True)
        self.date_profil = QLabel(Userprofilwindow)
        self.date_profil.setGeometry(QRect(20, 280, 231, 21))
        self.date_profil.setFont(font3)
        self.date_profil.setObjectName("date_profil")

        receiver_thread.user_profil.connect(self.set_user_profil)

    def set_user_profil(self, profil):
        """
        set_user_profil(profil): Via le signal depuis le thread de réception, obtient toutes les informations pour remplir les champs du profil. Cherche également dans le dictionnaire des photos pour trouver l'image correspondante.
        """
        info_profil = profil.split("|")

        if info_profil[3] == "1":
            admin_icon = "👑"
        else:
            admin_icon = ""

        index_nom = photo_dico['Nom'].index(info_profil[6])
        photo = photo_dico['Photo'][index_nom]

        desc = None if info_profil[4] == "None" else info_profil[4]

        date = info_profil[5].split(" ")

        self.username.setText(f"@{info_profil[0]}{admin_icon}")
        self.alias.setText(info_profil[1])
        self.mail.setText(info_profil[2])
        self.photo.setText(photo)
        self.description_text_edit.setText(desc)
        self.date_profil.setText(f"Compte créé le {date[0]} à {date[1]}")

class PhotoWindow(QMainWindow):
    """Cette classe est la fenêtre permettant de sélectionner son image de profil.
    
    Methods:
        setup_window(): Permet l'affichage de la sélection d'images de profil.
        
        photo_update(photo): Modifie la photo de profil en utilisant le dictionnaire pour trouver le nom correspondant à l'image et l'envoyer à la BDD.

    """
    photo_change = pyqtSignal(str)
    def __init__(self, parent = None):
        super(PhotoWindow, self).__init__(parent)

        self.setup_window()

    def setup_window(self):
        """
        setup_window(): Permet l'affichage de la sélection d'images de profil.
        """
        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        self.setStyleSheet(stylesheet)

        self.setWindowTitle("Choisir une image")
        self.setFixedSize(400, 300)
        self.bear = QPushButton("🐻")
        self.christmas = QPushButton("🎅")
        self.demon = QPushButton("👿")
        self.nerd = QPushButton("🤓")
        self.skull = QPushButton("💀")
        self.caca = QPushButton("💩")
        self.grenouille = QPushButton("🐸")
        self.chien = QPushButton("🐶")
        self.bomb = QPushButton("💣")
        self.clown = QPushButton("🤡")
        self.fleur = QPushButton("🌸")
        self.tortue = QPushButton("🐢")

        font = QFont()
        font.setPointSize(40)  # Définir la taille de police à 40

        # Appliquer la police à tous les boutons
        self.bear.setFont(font)
        self.christmas.setFont(font)
        self.demon.setFont(font)
        self.nerd.setFont(font)
        self.skull.setFont(font)
        self.caca.setFont(font)
        self.grenouille.setFont(font)
        self.chien.setFont(font)
        self.bomb.setFont(font)
        self.clown.setFont(font)
        self.fleur.setFont(font)
        self.tortue.setFont(font)
        layout = QGridLayout()

        layout.addWidget(self.bear, 0, 0)
        layout.addWidget(self.christmas, 0, 1)
        layout.addWidget(self.demon, 0, 2)
        layout.addWidget(self.nerd, 1, 0)
        layout.addWidget(self.skull, 1, 1)
        layout.addWidget(self.caca, 1, 2)
        layout.addWidget(self.grenouille, 2, 0)
        layout.addWidget(self.chien, 2, 1)
        layout.addWidget(self.bomb, 2, 2)
        layout.addWidget(self.clown, 3, 0)
        layout.addWidget(self.fleur, 3, 1)
        layout.addWidget(self.tortue, 3, 2)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.bear.clicked.connect(lambda: self.photo_update("🐻"))
        self.christmas.clicked.connect(lambda: self.photo_update("🎅"))
        self.demon.clicked.connect(lambda: self.photo_update("👿"))
        self.nerd.clicked.connect(lambda: self.photo_update("🤓"))
        self.skull.clicked.connect(lambda: self.photo_update("💀"))
        self.caca.clicked.connect(lambda: self.photo_update("💩"))
        self.grenouille.clicked.connect(lambda: self.photo_update("🐸"))
        self.chien.clicked.connect(lambda: self.photo_update("🐶"))
        self.bomb.clicked.connect(lambda: self.photo_update("💣"))
        self.clown.clicked.connect(lambda: self.photo_update("🤡"))
        self.fleur.clicked.connect(lambda: self.photo_update("🌸"))
        self.tortue.clicked.connect(lambda: self.photo_update("🐢"))

    def photo_update(self, photo):
        """
        photo_update(photo): Modifie la photo de profil en utilisant le dictionnaire pour trouver le nom correspondant à l'image et l'envoyer à la BDD.
        """
        self.photo_change.emit(photo)

        index_photo = photo_dico['Photo'].index(photo)
        nom_photo = photo_dico['Nom'][index_photo]

        reply = f"PROFIL|Photo|{nom_photo}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()
        self.close()

class UsersWidget(QWidget):
    """Cette classe représente la liste des utilisateurs dans la fenêtre messagerie qui est un élément d'un QListWidget de la classe MessagerieWindow().

    Attributes:
        button_name (str): Variable string, contient le nom de l'utilisateur, qui est le texte du bouton pour accéder aux messages privés avec ce dernier.
    Methods:
        setup_window(): Affiche un bouton de profil et un bouton permet d'accéder au chat privé avec un utilisateur.
    """
    def __init__(self, button_name, parent=None):
        """Initialise une instance de la classe UsersWidget
        
        Args:
            button_name: Valeur initalement obtenue depuis la classe MessagerieWindow qui reçoit un signal contenant le nom d'utilisateur qui correspond à cette valeur."""
        super().__init__(parent)
        self.button_name = button_name
        self.setup_window()

    def setup_window(self):
        """
        setup_window(): Affiche un bouton de profil et un bouton permet d'accéder au chat privé avec un utilisateur.
        """
        layout = QGridLayout(self)
        self.button1 = QPushButton("👤", self)
        self.button2 = QPushButton(self.button_name, self)

        layout.addWidget(self.button1, 0, 0)
        layout.addWidget(self.button2, 0, 1, 1, 3)


class MessagerieWindow(QWidget):
    """Cette classe est une fenêtre affichant les messages privés avec tous les utilisateurs existants, et les amis du client.

    Methods:
        setup_window(): Affiche les chats privés et les utilisateurs, ainsi qu'un bouton Amis.
        Il y a un seul text edit, juste il récupère les valeurs du dictionnaire correspondant au nom d'utilisateur sur le bouton pour un affichage correct des messages.

        send_button_clicked(): Permet d'ajouter les messages privés au text edit. 
        Ajoute au dictionnaire le contenu des messages à l'utilisateur associé et véifie les dates pour un affichage logique de la temporalité.

        add_msg_private(msg): Ajoute aux dictionnaires les messages privés nouveaux obtenu durant la connexion, et si l'utilisateur à sélectionné l'utilisateur au niveau de l'élmément de la QListWidget, les messages s'affichent en temps réel dans le text_edit.

        add_button_clicked(users): Permet d'ajouter au QListWidget le nouvel élément contenant l'utilisateur pour poouvoir converser avec lui, via le signal du thread de réception.

        show_text_edit(button_widget): Cherche le nom d'utilisateur qui est assigné au bouton qui est cliqué et affiche dans le text edit la partie contenu au niveau de l'index de l'utilisateur associé, dans le dictionnaire.
        Pour rappel tous les messages sont stockés dans le dictionnaire au même index que l'utilisateur.

        send_profil(button_widget): Envoie une requête serveur pour obtenir le profil utilisateur demandé, en le récupérant via l'objet de la liste.

        show_profil(profil): Permet lors de la réception du signal avec les données du profil de l'utilisateur concerné d'afficher la fenêtre avec les données.

        show(friend): Permet d'afficher la fenêtre avec les amis du client;
    """
    global receiver_thread
    def __init__(self):
        """Initialise une instance de la classe MessagerieWindow()"""
        super().__init__()

        self.setup_window()

    def setup_window(self):
        """
        setup_window(): Affiche les chats privés et les utilisateurs, ainsi qu'un bouton Amis.
        Il y a un seul text edit, juste il récupère les valeurs du dictionnaire correspondant au nom d'utilisateur sur le bouton pour un affichage correct des messages.
        """

        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        self.setStyleSheet(stylesheet)

        layout = QHBoxLayout(self)


        button_layout = QVBoxLayout()
        self.button_list = QListWidget(self)
        
        button_layout.addWidget(self.button_list)

        friends_button = QPushButton("Amis", self)
        button_layout.addWidget(friends_button)
        friends_button.clicked.connect(self.show_friends)
        # Ajout du layout des boutons au layout principal
        layout.addLayout(button_layout)

        # Layout du TextEdit (2 tiers droit)
        self.text_edit_layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit_layout.addWidget(self.text_edit)

        # Ajout du QLineEdit
        self.line_edit = QLineEdit(self)
        self.line_edit.returnPressed.connect(self.send_button_clicked)
        self.text_edit_layout.addWidget(self.line_edit)
        self.line_edit.setMaxLength(255)

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
        self.setObjectName('Messagerie')

        receiver_thread.users_sended.connect(self.add_button_clicked)
        receiver_thread.msg_private.connect(self.add_msg_private)
        receiver_thread.new_user.connect(self.add_button_clicked)
        receiver_thread.user_profil.connect(self.show_profil)
        
        self.setFixedSize(800, 600)

    def send_button_clicked(self):
        """
        send_button_clicked(): Permet d'ajouter les messages privés au text edit. 
        Ajoute au dictionnaire le contenu des messages à l'utilisateur associé et véifie les dates pour un affichage logique de la temporalité.
        """
        global username
        # Récupère le texte du QLineEdit et l'ajoute au QTextEdit
        text_to_append = self.line_edit.text()
        self.line_edit.clear()
        date = datetime.datetime.now().strftime("%H:%M")
        mois = datetime.datetime.now().strftime("%d/%m/%Y")
        if text_to_append:
            selected_item = self.button_list.currentItem()
            selected_widget = self.button_list.itemWidget(selected_item)
            user2 = selected_widget.button2.text()

            private = f"{date} - {username} ~~ {text_to_append}"
            print("user2")

            try:
                index_user = all_private['User'].index(user2)
                if mois != all_private["Mois"][index_user]:
                    all_private["Private"][index_user] = f'{all_private["Private"][index_user]}<br>───────────────────────{mois}──────────────────────'
                    all_private["Mois"][index_user] = mois
                    self.text_edit.append(f"───────────────────────{mois}──────────────────────")
                all_private["Private"][index_user] = f'{all_private["Private"][index_user]}<br>{private}'
                print("added to dico")
            
            except ValueError:
                all_private["Private"].append(f"───────────────────────{mois}──────────────────────<br>{private}")
                all_private["User"].append(user2)
                all_private["Mois"].append(mois)
                self.text_edit.append(f"───────────────────────{mois}──────────────────────")
            
            except IndexError:
                all_private["Private"].append(f"───────────────────────{mois}──────────────────────<br>{private}")
                all_private["User"].append(user2)
                all_private["Mois"].append(mois)
                self.text_edit.append(f"───────────────────────{mois}──────────────────────")


            self.text_edit.append(f"{date} - {username} ~~ {text_to_append}")
            
            #print(all_private)
            reply = f"PRIVATE|{username}|{user2}|{text_to_append}"
            self.sender_thread = SenderThread(reply)
            self.sender_thread.start()
            self.sender_thread.wait()

            print("ended")

    def add_msg_private(self, msg):
        """
        add_msg_private(msg): Ajoute aux dictionnaires les messages privés nouveaux obtenu durant la connexion, et si l'utilisateur à sélectionné l'utilisateur au niveau de l'élmément de la QListWidget, les messages s'affichent en temps réel dans le text_edit.
        """
        print("add_msg_private")
        print(msg)
        msg_private = msg.split("|")
        date = datetime.datetime.now().strftime("%H:%M")
        mois = datetime.datetime.now().strftime("%d/%m/%Y")
        user1 = msg_private[0]
        user2 = msg_private[1]
        contenu = msg_private[2]

        private = f"{date} - {user1} ~~ {contenu}"
        user = user1 if msg_private[3] == "user1" else user2
        try:
            index_user = all_private['User'].index(user)
            if mois != all_private["Mois"][index_user]:
                all_private["Private"][index_user] = f'{all_private["Private"][index_user]}<br>───────────────────────{mois}──────────────────────'
                all_private["Mois"][index_user] = mois
                selected_item = self.button_list.currentItem()
                if selected_item:
                    selected_widget = self.button_list.itemWidget(selected_item)
                    chat = selected_widget.button2.text()
                    if user == chat:
                        self.text_edit.append(f"───────────────────────{mois}──────────────────────")

            all_private["Private"][index_user] = f'{all_private["Private"][index_user]}<br>{private}'
            print("added to dico2")
            print(all_private)
        
        except ValueError:
            all_private["Private"].append(f"───────────────────────{mois}──────────────────────<br>{private}")
            all_private["User"].append(user)
            all_private["Mois"].append(mois)
            selected_item = self.button_list.currentItem()
            if selected_item:
                selected_widget = self.button_list.itemWidget(selected_item)
                chat = selected_widget.button2.text()
                if user == chat:
                    self.text_edit.append(f"───────────────────────{mois}──────────────────────")
        
        except IndexError:
            all_private["Private"].append(f"───────────────────────{mois}──────────────────────<br>{private}")
            all_private["User"].append(user)
            all_private["Mois"].append(mois)
            selected_item = self.button_list.currentItem()
            if selected_item:
                selected_widget = self.button_list.itemWidget(selected_item)
                chat = selected_widget.button2.text()
                if user == chat:
                    self.text_edit.append(f"───────────────────────{mois}──────────────────────")
        #print(all_private)

        try:
            selected_item = self.button_list.currentItem()
            if selected_item:
                selected_widget = self.button_list.itemWidget(selected_item)
                chat = selected_widget.button2.text()

                if user == chat:
                    print("append !")
                    self.text_edit.append(private)

        except AttributeError:
            pass
    
    def add_button_clicked(self, users):
        """
        add_button_clicked(users): Permet d'ajouter au QListWidget le nouvel élément contenant l'utilisateur pour poouvoir converser avec lui, via le signal du thread de réception.
        """
        global username
        group = users.split("|")
        if group[0] == "Général":
            resultat = re.search(r'@([^| 👑]+)', users)
            if resultat:
                resultat_user = resultat.group(1)
                print(resultat_user)
                if resultat_user == username:
                    return
        else:
            return
        
        #print(all_private)
        # Ajoute un nouvel élément à la liste
        button_widget = UsersWidget(resultat_user)
        item = QListWidgetItem(self.button_list)
        item.setSizeHint(button_widget.sizeHint())
        self.button_list.setItemWidget(item, button_widget)

        if resultat_user in users_list:
            self.show_text_edit(button_widget)

        # Connecte le signal pressed du bouton 2 à l'affichage du TextEdit
        button_widget.button2.clicked.connect(lambda: self.show_text_edit(button_widget))
        self.button_list.clicked.connect(lambda: self.show_text_edit(button_widget))
        button_widget.button1.clicked.connect(lambda: self.send_profil(button_widget))

    def show_text_edit(self, button_widget):
        """
        show_text_edit(button_widget): Cherche le nom d'utilisateur qui est assigné au bouton qui est cliqué et affiche dans le text edit la partie contenu au niveau de l'index de l'utilisateur associé, dans le dictionnaire.
        Pour rappel tous les messages sont stockés dans le dictionnaire au même index que l'utilisateur.
        """
        button_name = button_widget.button_name
        try:
            # Trouver l'élément correspondant dans la liste
            for index in range(self.button_list.count()):
                item = self.button_list.item(index)
                widget = self.button_list.itemWidget(item)
                if widget.button_name == button_name:
                    # Sélectionner l'élément dans le QListWidget
                    self.button_list.setCurrentItem(item)
                    break

            index_user = all_private['User'].index(button_name)
            content = all_private['Private'][index_user]
            self.text_edit.setHtml(f"<b>Conversation avec {button_name}</b> <br><br>{content}")

        except ValueError:
            self.text_edit.setHtml(f"<b>Conversation avec {button_name}</b> <br><br>Engagez la conversation avec {button_name} !")

    def send_profil(self, button_widget):
        """
        send_profil(button_widget): Envoie une requête serveur pour obtenir le profil utilisateur demandé, en le récupérant via l'objet de la liste.
        """
        global Userprofilwindow
        button_name = button_widget.button_name #le nom de l'utilisateur est associé au bouton
        print(button_name)

        reply = f"USER_PROFIL|{button_name}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def show_profil(self, profil):
        """
        show_profil(profil): Permet lors de la réception du signal avec les données du profil de l'utilisateur concerné d'afficher la fenêtre avec les données.
        """
        try:
            Userprofilwindow.close()
        except:
            pass
        Userprofilwindow.show()

    def show_friends(self):
        """
        show(friend): Permet d'afficher la fenêtre avec les amis du client;
        """
        f.show()


class Friends(QWidget):
    """Cette classe est une fenêtre permettant d'afficher la liste d'ami.

    Mathods:
        add_friends(friends): Ajoute les amis au QListWidget avec l'interface graphique du QWidget.
        
        box(user, item): Fenêtre de dialog lors de la supression d'un ami qui demande confirmation.

        delete_friend(user, item): Envoie via le thread d'envoi un message au serveur de l'ami à retirer, et supprime l'élément graphiquement.

        auto_del_friend(user): Reçoit du serveur le nom de l'ami à supprimer pour enelever automatiquement du côté des deux users plus amis l'élément QWidget en cherchant dans la liste.
    
        send_profil(item): Envoie la requête de l'utilisateur pour lequel on veut afficher le profil en récupérant via le nom du bouton.

        show_profil(profil): Permet lors de la réception du signal avec les données du profil de l'utilisateur concerné d'afficher la fenêtre avec les données.
    """
    global receiver_thread
    def __init__(self):
        """Initialise une nouvelle instance de la classe Friends()."""
        super().__init__()

        #Récupération des styles qss comme à chaque fois
        styles_file_path = os.path.join(os.path.dirname(__file__), "styles/styles_login.qss")
        style_file = QFile(styles_file_path)
        style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        stylesheet = QTextStream(style_file).readAll()
        self.setStyleSheet(stylesheet)

        self.setObjectName("Friends")

        # Créer la QListWidget
        self.setFixedSize(400, 400)
        self.setWindowTitle("Amis")
        self.list_widget = QListWidget(self)

        # Créer la mise en page principale
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.list_widget)

        # Définir la mise en page principale
        receiver_thread.friends.connect(self.add_friends)
        receiver_thread.new_friend.connect(self.add_friends)
        receiver_thread.delete_friend.connect(self.auto_del_friend)
        self.setLayout(main_layout)

    def add_friends(self, friends):
        """
        add_friends(friends): Ajoute les amis au QListWidget avec l'interface graphique du QWidget.
        """
        info_friends = friends.split("|")
        user = info_friends[0]
        alias = info_friends[1]
        # Créer un nouvel élément QListWidgetItem
        item = QListWidgetItem()

        item_widget = QWidget()
        item_layout = QGridLayout(item_widget)
        
        self.label = QLabel(f"{alias} @{user}")
        self.label.setObjectName(user)
        self.button1 = QPushButton("👤")
        self.button1.setObjectName(user)
        self.button2 = QPushButton("Supprimer l'ami")
        self.not_ok_icon = QIcon.fromTheme('dialog-cancel')  # Icône standard de "Ok"
        self.button2.setIcon(self.not_ok_icon)

    
        item_layout.addWidget(self.button1, 0, 0)
        item_layout.addWidget(self.label, 0, 1, 1, 3)
        item_layout.addWidget(self.button2, 1, 0, 1, 4)

        item_widget.setLayout(item_layout)

        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)

        self.button2.clicked.connect(lambda: self.box(user, item))
        self.button1.clicked.connect(lambda: self.send_profil(item))

        receiver_thread.user_profil.connect(self.show_profil)

    def box(self, user, item):
        """
        box(user, item): Fenêtre de dialog lors de la supression d'un ami qui demande confirmation.
        """
        error = QMessageBox(self)
        error.setWindowTitle("Supprimer un ami")
        content = f"Êtes vous sûr de vouloir retirer {user} de votre liste d'amis ?"
        error.setText(content)
        ok_button = error.addButton(QMessageBox.Ok)
        ok_button.clicked.connect(lambda: self.delete_friend(user, item))
        cancel_button = error.addButton(QMessageBox.Cancel)
        error.setIcon(QMessageBox.Warning)
        error.exec()

    def delete_friend(self, user, item):
        """
        delete_friend(user, item): Envoie via le thread d'envoi un message au serveur de l'ami à retirer, et supprime l'élément graphiquement.
        """
        global username
        reply = f"DELETE_FRIEND|{user}|{username}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)

    def auto_del_friend(self, user):
        """
        auto_del_friend(user): Reçoit du serveur le nom de l'ami à supprimer pour enelever automatiquement du côté des deux users plus amis l'élément QWidget en cherchant dans la liste.
        """
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            label = self.list_widget.itemWidget(item).findChild(QLabel)
            #print(label.objectName())
            if label.objectName() == user:
                #print("test")
                # Supprimer l'élément de la liste
                row = self.list_widget.row(item)
                self.list_widget.takeItem(row)
                break
    
    def send_profil(self, item):
        """
        send_profil(item): Envoie la requête de l'utilisateur pour lequel on veut afficher le profil en récupérant via le nom du bouton.
        """
        global Userprofilwindow
        button1 = self.list_widget.itemWidget(item).findChild(QPushButton)
        button_name = button1.objectName()
        print(button_name)

        reply = f"USER_PROFIL|{button_name}"
        self.sender_thread = SenderThread(reply)
        self.sender_thread.start()
        self.sender_thread.wait()

    def show_profil(self, profil):
        """
        show_profil(profil): Permet lors de la réception du signal avec les données du profil de l'utilisateur concerné d'afficher la fenêtre avec les données.
        """
        try:
            Userprofilwindow.close()
        except:
            pass
        Userprofilwindow.show()

def show_signup_window():
    """
    show_signup_window(): Permet l'affichage de la fenêtre d'inscription via un signal émit depuis la classe Login().
    """
    global signup_window
    signup_window = Sign_up()
    signup_window.show()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        MainWindow = QMainWindow()
        ui = Window()
        ui.setup_window(MainWindow)
        w = Login()
        w.show()
        m = MessagerieWindow()
        f = Friends()

        #instances des classes
        photo_window = PhotoWindow()
        Courrierwindow = QMainWindow()
        courrier_window = CourrierWindow()
        Profilwindow = QMainWindow()
        profil_window = ProfilWindow()
        Userprofilwindow = QMainWindow()
        userprofil_window = UserProfilWindow()
        
        #run de la fonction d'affichage via l'instance de la classe concerné
        courrier_window.setup_window(Courrierwindow)
        profil_window.setup_window(Profilwindow)
        userprofil_window.setup_window(Userprofilwindow)

        # Connecter le signal show_self_signal à la fonction d'affichage de l'inscription
        w.signup_window_signal.connect(show_signup_window)
        

        sys.exit(app.exec_())
    finally:
        print("Arrêt client")
        #end()


