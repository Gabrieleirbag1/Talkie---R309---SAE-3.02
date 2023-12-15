import mysql.connector

conn = mysql.connector.connect(
        host='localhost',
        user='gab',
        password='',
        database='Skype'
    )

def check_demande():


    nb_msg_query = f"SELECT * FROM demande where receveur = 'Emi'"

    cursor = conn.cursor()
    cursor.execute(nb_msg_query)
    
    result = cursor.fetchall()
    print(result)

    conn.close()

    if result[0][7] == 0:
        print("caca")

check_demande()
