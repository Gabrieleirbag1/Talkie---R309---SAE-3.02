import os

def replace_text_in_file(file_path, username, new_username):
  
    with open(file_path, 'r') as file:
        file_content = file.read()

    new_content = file_content.replace(username, new_username)

    with open(file_path, 'w') as file:
        file.write(new_content)


if __name__ == "__main__":

    server_file_path = os.path.join(os.path.dirname(__file__), "Server.py")

    username = "root"
    mdp = "toor"

    new_username = input("Nouvel identifiant : ")


    if os.path.exists(server_file_path):
        # Remplacer le texte dans le fichier
        replace_text_in_file(server_file_path, username, new_username)
        
        print(f"Le remplacement dans {server_file_path} a été effectué.")
    else:
        print(f"Le fichier {server_file_path} n'existe pas.")

    new_mdp = input("Nouvel identifiant : ")

    if os.path.exists(server_file_path):
        # Remplacer le texte dans le fichier
        replace_text_in_file(server_file_path, mdp, new_mdp)
        
        print(f"Le remplacement dans {server_file_path} a été effectué.")
    else:
        print(f"Le fichier {server_file_path} n'existe pas.")
