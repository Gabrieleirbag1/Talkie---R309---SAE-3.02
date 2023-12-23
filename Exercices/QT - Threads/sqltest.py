from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import socket, mysql.connector, datetime, sys, re, time, threading

try: #ouverture de la connexion mysql
    conn = mysql.connector.connect(
        host='localhost', #host
        user='gab', #utilisateur
        password='', #mdp assigné (ici aucun)
        database='Skype' #nom de la db
    )
except Exception as e:
    print(e) #impression de l'éventuelle échec de connexion à la bdd mysql

user = "Admin"

def friends():
    friends_query = f"SELECT * FROM friends where friend1 = 'Admin' or friend2 = 'Admin'"

    cursor = conn.cursor()
    cursor.execute(friends_query)
    result = cursor.fetchall()
    cursor.close()

    print(result )
    for i in range(len(result)):
        friend1 = result[i][1]
        friend2 = result[i][2]
        friend = friend1 if user == friend2 else friend2
        reply = f"FRIENDS|{friend}|{user}"
        i+=1
        print(reply)


friends()
