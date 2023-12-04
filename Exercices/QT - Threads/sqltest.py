import mysql.connector, datetime

conn = mysql.connector.connect(
    host='localhost',
    user='gab',
    password='',
    database='Skype'
)


def historique():
    c = 10
    for i in range(c +1):
        try:
            msg_query = f"SELECT message.message, user.username FROM message JOIN user ON message.user = user.id_user WHERE message.id_message = 9"
            cursor = conn.cursor()
            cursor.execute(msg_query)
            
            result = cursor.fetchone()
            message = result[0]
            username = result[1]

            print(message)
            print(username)
        except Exception as err:
            continue

#while True:
historique()
print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
print("Normal text \x1B[3mitalic text\x1B[0m normal text")


truc = "caca | zizi"

truc = truc.split("|")

print(truc[1])