import sys


def divEntier(x: int, y: int) -> int:
    try :
        if y > 0 or x > 0:
            if x < y:
                return 0
            else:
                x = x - y
                return divEntier(x, y) + 1
        else:
            raise ValueError
    except ValueError:
        return (print("Erreur de valeur négative"), main())
            

def main():
    try:
        x = int(input('x = '))
        y = int(input('y = '))

        if y == 0:
            raise ZeroDivisionError

    except ValueError as error:
        return (print("Erreur de valeur caractère"), main())
    
    except ZeroDivisionError as error:
        return (print("Erreur de valeur égale à 0"), main())
    
    else:
        print(divEntier(x, y))
        return main()
        


if __name__ == "__main__":
    main()