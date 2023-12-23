def ajouter_private(all_private, user, code):
    private = {"User1": code[1], "User2": code[2], "Contenu": f"{code[4]} - {code[3]}"}

    # Vérifier si l'utilisateur existe déjà dans le dictionnaire
    for index, existing_user in enumerate(all_private["User"]):
        if existing_user == user:
            # Remplacer l'ancienne entrée par la nouvelle
            all_private["Private"][index] = private
            return

    # Si l'utilisateur n'existe pas, ajouter une nouvelle entrée
    all_private["Private"].append(private)
    all_private["User"].append(user)


all_private = {"Private": [], "User": []}

# Ajouter un premier élément
ajouter_private(all_private, "Alice", ["PRIVATE", "Alice", "Bob", "2023-01-01 12:34:56", "Message1"])

# Afficher le dictionnaire après l'ajout du premier élément
print(all_private)

# Ajouter un deuxième élément avec le même utilisateur (remplacera le premier)
ajouter_private(all_private, "Alice", ["PRIVATE", "Alice", "Charlie", "2023-01-02 10:45:30", "Message2"])

# Afficher le dictionnaire après l'ajout du deuxième élément (remplacement)
print("zizi")
print(all_private)


class MyClass:
    """Cette classe représente un exemple de classe.

    Attributes:
        attribute1 (int): Une variable d'entier pour stocker une valeur.
        attribute2 (str): Une variable de chaîne pour stocker du texte.

    Methods:
        method1(): Une méthode qui fait quelque chose.
        method2(param): Une méthode avec un paramètre.

    """

    def __init__(self, value):
        """Initialise une nouvelle instance de la classe.

        Args:
            value: La valeur initiale pour attribute1.

        """
        self.attribute1 = value
        self.attribute2 = "Initial Value"

    def method1(self):
        """Une méthode qui fait quelque chose."""
        print("Méthode 1 exécutée.")

    def method2(self, param):
        """Une méthode avec un paramètre.

        Args:
            param: Un paramètre pour la méthode.

        Returns:
            str: Une chaîne de caractères résultante.

        """
        result = f"Le paramètre est {param}."
        return result

# Exemple d'utilisation de la classe et de la documentation
instance = MyClass(42)
instance.method1()
output = instance.method2("Hello")
print(output)

reply="12 12"
print(reply)
import re
if not re.search(r"\s", reply):
    print (reply)