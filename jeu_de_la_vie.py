# coding: utf-8
'''
Une simulation du jeu de la vie
'''

#TODO (si on veut)
# - des boutons pour créer aléatoirement, RAZ, pause
# pourvoir dessiner/effacer à la main
# changer la couleur des cellules immobiles
# gerer autrement taille_x et taille_y
# ajouter compteur de tours, temps/tour
# multithread (un regle 1 , l'autre regle 2)
# Afficher en couleur différentes les naissances et morts (et rafraichir avant maj)

import time
import os
import random
from tkinter import *


class Plateau(object):
    '''Le plateau de jeu
    '''
    def __init__(self, largeur=400, hauteur=400, taille_x = 5, taille_y = 5):
        self.largeur = largeur
        self.hauteur = hauteur
        self.cellules = {} # {(x,y) : Cellule(), ...}
        self.tour = 0
        self.root = Tk()
        self.root.title('Le jeu de la vie')
        self.aire = Canvas(self.root, height = self.hauteur * taille_y, width = self.largeur * taille_x)
        self.aire.grid()
        Button(self.root, text = "Go!", command = self.run).grid()



    def add(self, positions):
        '''Ajout une cellule ou une liste de cellules
        '''
        if type(positions) != list:
            positions = [positions]
        for position in positions:
            self.cellules[position] = Cellule(self.aire, position,True)

    def __repr__(self):
        '''juste pour mode console
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
        #print(self)
        #input("Press Enter to continue...")
        while True:
            self.un_tour()
            self.root.update()


    def un_tour(self):
        ''' génère un tour complet
        '''
        #debut = time.time()
        self.tour += 1
        #print("Tour n°%s"%self.tour)
        self.regle2()
        self.regle1()
        self.naissances()
        self.clean()

    def print(self):
        txt = str(self)
        os.system('cls')
        print(txt)

    def regle1(self):
        '''Applique la règle n° 1:
            Si cellule morte (ou pas de cellule dans notre cas) a exactement 3 voisines
            Alors est devient vivante.
        '''
        for position_vide in self.positions_vides():
            if self.nb_voisines(position_vide)==3:
                self.cellules[position_vide]= Cellule(self.aire, position_vide)

    def regle2(self):
        '''Applique la règle 2 :
            Une cellule vivante le reste uniqument si elle a 2 ou 3 voisines exactement
        '''
        for position in self.cellules:
            if self.nb_voisines(position) not in [2,3]:
                self.cellules[position].meurt()

    def clean(self):
        '''Supprime les cellules mortes
        '''
        for position in list(self.cellules.keys()):
            if not self.cellules[position].vivante:
                del self.cellules[position]

    def naissances(self):
        '''transforme les cellules en cours de naissance par des cellules vivantes
        '''
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
            position = P(self.largeur-1, position.y) #On sait que l'on n'est qu'a 1 case maxi d'un bord!
        if position.y >= self.hauteur:
            position = P(position.x,0) #On sait que l'on n'est qu'a 1 case maxi d'un bord!
        elif position.y < 0:
            position = P(position.x, self.hauteur-1) #On sait que l'on n'est qu'a 1 case maxi d'un bord!
        return position

    def aleat_polulate(self, taux):
        '''remplit aleatoirement le Plateau
            taux : entre 0 (peu de cellules) et 1 (un max de cellules)
        '''
        for x in range(int(self.largeur / 2)):
            for y in range(int(self.hauteur / 2)):
                if random.random()< taux:
                    self.add(P(int(self.largeur / 4) + x,int(self.hauteur / 4) + y))


class Cellule(object):
    '''une cellule
    Etats possibles :
        -   True : est et reste vivante
        -   False : est vivante, mais va mourrir au tour suivant
        -   None : en cours de naissance
    '''
    def __init__(self, canvas, position, vivante = None):
        self.vivante = vivante
        self.canvas = canvas
        self.marque = self.canvas.create_oval(5*position.x, 5*position.y, 5*position.x+5, 5*position.y+5, fill="khaki")

    def naissance(self):
        self.vivante = True

    def meurt(self):
        self.vivante = False
        self.canvas.delete(self.marque)

    def __repr__(self):
        '''Pour mode console (obsolete)
        '''
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
    plateau = Plateau(300,180)
    #n=24
    #for i in range(n):
        #plateau.add(P(int(plateau.largeur/2 - n/2 )+i,int(plateau.hauteur / 2)))
    #Un planeur
    plateau.add([P(3,11),P(1,12),P(3,12),P(2,13),P(3,13)])
    plateau.aleat_polulate(0.2)
    plateau.root.mainloop()
