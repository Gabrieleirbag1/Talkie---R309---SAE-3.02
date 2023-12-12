user_conn = {'Conn': ["conn1", "conn2", "conn3"],
             'Username': ["user1", "user2", "user1"],
             'Address': ["addr1", "addr2", "addr3"],
             'Port': ["port1", "port2", "port3"]}

user = "user1"  # Remplacez ceci par la valeur que vous recherchez

conn_list = []  # Liste pour stocker les CONN correspondants

# Parcours de chaque index dans la liste 'Username'
for i, username in enumerate(user_conn['Username']):
    if username == user:
        # Si le Username correspond, ajoutez la Conn correspondante à la liste
        conn_list.append(user_conn['Conn'][i])

# Affichage de la liste des CONN correspondants
print(conn_list)
