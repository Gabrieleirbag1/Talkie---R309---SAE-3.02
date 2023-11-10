def main(): 
    try:
        print('\nFichier 1 :')
        with open('/home/frigiel/PROCEDURE-DJANGO.txt', 'r') as f:
            for l in f:
                l = l.strip("\n\r")
                print(l)
            f.close()

    except FileNotFoundError as error:
        print(f"{error} :Le fichier n'a pas été trouvé.")

    try:
        print('\nFichier 2 :')
        with open('existepas.txt', 'r') as f:
            for l in f:
                l = l.strip("\n\r")
                print(l)
            f.close()

    except FileNotFoundError as error:
        print(f"{error} :Le fichier n'a pas été trouvé.")


    try:
        print('\nFichier 3 :')
        with open('/home/frigiel/pasledroit.txt', 'r') as f:
            for l in f:
                l = l.strip("\n\r")
                print(l)
            f.close()
    except PermissionError as error:
        print(f"{error} : Pas la permission")

    try:
        print("\nÉcriture du fichier 4")
        f = open("/home/frigiel/helloworld.txt", "x")
        f.write("Hello world !")
        f.close()

    except FileExistsError as error:
        print(f"{error} : Le fichier existe déjà.")


    try:
        print('\nFichier 4 :')
        with open('/home/frigiel/helloworld.txt', 'r') as f:
            for l in f:
                l = l.strip("\n\r")
                print(l)
            f.close()
    except IOError as error:
        print(f"{error} : Y a une erreur quelconque")

    finally:
        print("\nFin du programme")


if __name__ == "__main__":
    try: 
        main()
    except BaseException as error:
        print(f"{error} : Il y a une erreur quelconque")




