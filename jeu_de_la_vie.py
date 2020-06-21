# coding: utf-8
import time
import os
import random


class Plateau(object):
    '''Le plateau de jeu
    '''
    def __init__(self, largeur=400, hauteur=400):
        self.largeur = largeur
        self.hauteur = hauteur
        self.cellules = {} # {(x,y) : Cellule(), ...}
        self.tour = 0

    def add(self, positions):
        '''Ajout une cellule ou une liste de cellules
        '''
        if type(positions) != list:
            positions = [positions]
        for position in positions:
            self.cellules[position] = Cellule(True)

    def __repr__(self):
        '''On perd ici l'interet du dict pour les cellules!!!
        '''
        txt = ""
        for y in range(self.hauteur):
            ligne = ""
            for x in range(self.largeur):
                if P(x,y) in self.cellules:
                    ligne += str(self.cellules[P(x,y)])
                else:
                    ligne += " "
            txt += ligne + "\n"
        return txt

    def run(self):
        '''Loop forever
        '''
        print(self)
        input("Press Enter to continue...")
        while True:
            self.un_tour()
            #time.sleep(1)
            #input("Press Enter to continue...")

    def un_tour(self):
        ''' génère un tour complet
        '''
        #debut = time.time()
        self.tour += 1
        print("Tour n°%s"%self.tour)
        self.regle2()
        #temps_regle2 = time.time() - debut
        #print(self)
        self.regle1()
        #temps_regle1 = time.time() - debut - temps_regle2
        #print(self)
        self.naissances()
        #temps_naissance = time.time() - debut - temps_regle2 - temps_regle1
        #print(self)
        self.clean()
        #temps_clean = time.time() - debut - temps_regle2 - temps_regle1 - temps_naissance
        self.print()
        #temps_print = time.time() - debut - temps_regle2 - temps_regle1 - temps_naissance - temps_clean
        #with open("temps.txt", 'a') as file:
        #    file.write(f"{self.tour};{temps_regle2};{temps_regle1};{temps_naissance};{temps_clean};{temps_print}\n")

    def print(self):
        txt = str(self)
        os.system('cls')
        print(txt)

    def regle1(self):
        '''Applique la règle n° 1:
            Si cellule morte (ou pas de cellule dans notre cas) a exactement 3 voisines
            Alors est devient vivante.
        '''
        #print("règle n° 1...")
        for position_vide in self.positions_vides():
            if self.nb_voisines(position_vide)==3:
                self.cellules[position_vide]= Cellule()

    def regle2(self):
        '''Applique la règle 2 :
            Une cellule vivante le reste uniqument si elle a 2 ou 3 voisines exactement
        '''
        #print("règle n° 2...")
        for position in self.cellules:
            if self.nb_voisines(position) not in [2,3]:
                self.cellules[position].meurt()

    def clean(self):
        '''Supprime les cellules mortes
        '''
        #print("Clean...")
        for position in list(self.cellules.keys()):
            if not self.cellules[position].vivante:
                del self.cellules[position]

    def naissances(self):
        '''transforme les cellules en cours de naissance par des cellules vivantes
        '''
        #print("naissances...")
        for cellule in [cellule for cellule in self.cellules.values() if cellule.vivante is None]:
            cellule.vivante = True

    def positions_vides0(self):
        '''Renvoie un générateur des positions vides du plateau.
        Solution (obsolete) bourin
        '''
        for x in range(self.largeur):
            for y in range(self.hauteur):
                position = P(x,y)
                if position not in self.cellules:
                    yield position

    def positions_vides(self):
        '''Renvoie un dict des positions vides du plateau.
        Solution un peu mieux que la version 0
        '''
        positions_vides = {}
        for position in self.cellules:
            positions_vides.update({pos : True for pos in self.voisines(position) if pos not in self.cellules or self.cellules[pos].vivante != True})
        return positions_vides


    def nb_voisines(self, position):
        '''Renvoie le nombre de voisines limité à 4 (4 equivaut à (4 ou 5 ou 6 ou 7 ou 8))
        '''
        nb = 0
        for voisine in self.voisines(position):
            if voisine in self.cellules and self.cellules[voisine].vivante is not None:
                nb +=1
                if nb > 3:
                    break
        return nb

    def voisines(self, position):
        '''générateur de voisines
        '''
        for offset in [P(-1,-1),P(0,-1),P(1,-1),P(-1,0),P(1,0),P(-1,1),P(0,1),P(1,1)]:
            yield self.espace_infini(position + offset)

    def espace_infini(self, position):
        '''Si la position sort du plateau alors on renvoie la position de l'autre coté (x trop grand => x= 0)
        '''
        if position.x >= self.largeur:
            position = P(0, position.y) #On sait que l'on n'est qu'a 1 case maxi d'un bord!
        elif position.x < 0:
            position = P(self.largeur, position.y) #On sait que l'on n'est qu'a 1 case maxi d'un bord!
        if position.y >= self.hauteur:
            position = P(position.x,0) #On sait que l'on n'est qu'a 1 case maxi d'un bord!
        elif position.y < 0:
            position = P(position.x, self.hauteur) #On sait que l'on n'est qu'a 1 case maxi d'un bord!
        return position

    def aleat_polulate(self, taux):
        '''remplit aleatoirement le Plateau
            taux : entre 0 (peu de cellules) et 1 (un max de cellules)
        '''
        for x in range(self.largeur):
            for y in range(self.hauteur):
                if random.random()< taux:
                    self.add(P(x,y))


class Cellule(object):
    '''une cellule
    Etats possibles :
        -   True : est et reste vivante
        -   False : est vivante, mais va mourrir au tour suivant
        -   None : en cours de naissance
    '''
    def __init__(self, vivante = None):
        self.vivante = vivante

    def naissance(self):
        self.vivante = True

    def meurt(self):
        self.vivante = False

    def __repr__(self):
        if self.vivante is None:
            #return "😨"
            return "O"
        elif self.vivante:
            return "■"
            #return "😃"
            #return "\u1F601"
        else:
            return "X"
            #return "😡"

class P(tuple):
    '''Une position (coordonnés)
    '''
    def __new__(cls, *args):
        return tuple.__new__(cls, args)
    def __add__(self, other):
        return P(*([sum(x) for x in zip(self, other)]))
    def __sub__(self, other):
        return self.__add__(-i for i in other)
    @property
    def x(self):
        return self[0]
    @property
    def y(self):
        return self[1]

if __name__ == "__main__":
    plateau = Plateau(200,78)
    #n=24
    #for i in range(n):
        #plateau.add(P(int(plateau.largeur/2 - n/2 )+i,int(plateau.hauteur / 2)))
    #Un planeur
    #plateau.add([P(3,11),P(1,12),P(3,12),P(2,13),P(3,13)])
    plateau.aleat_polulate(0.3)
    plateau.run()
