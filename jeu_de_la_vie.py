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
# determiner quand terminé
# temps mini pour un tour

import time
import os
import random
from tkinter import *

exec_time_wrappers = []

def exec_time(func):
    def wrapper(*args, **kwargs):
        t_start = time.time()
        r = func(*args, **kwargs)
        t_end = time.time()
        wrapper.total_duration += t_end - t_start
        #print("Execution of " + func.__name__ + " took cumuled " + str(round(wrapper.total_duration)) + " seconds")
        return r
    wrapper.total_duration = 0
    wrapper.exec_time_name = func.__name__
    exec_time_wrappers.append(wrapper)
    return wrapper

def show_exec_time(nb_tours):
    for wrapper in exec_time_wrappers:
        print(f"Execution of {wrapper.exec_time_name} took {wrapper.total_duration/nb_tours:.3f} seconds per turn.")

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
        self.offsets = (P(-1,-1),P(0,-1),P(1,-1),P(-1,0),P(1,0),P(-1,1),P(0,1),P(1,1))



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
            self.update_ui()

    @exec_time
    def update_ui(self):
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
        show_exec_time(self.tour)
        pass

    def print(self):
        txt = str(self)
        os.system('cls')
        print(txt)

    @exec_time
    def regle1(self):
        '''Applique la règle n° 1:
            Si cellule morte (ou pas de cellule dans notre cas) a exactement 3 voisines
            Alors est devient vivante.
        '''
        for position_vide in self.positions_vides():
            if self.nb_voisines(position_vide)==3:
                self.cellules[position_vide]= Cellule(self.aire, position_vide)

    @exec_time
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
    @exec_time
    def positions_vides(self):
        '''Renvoie un dict des positions vides du plateau.
        Solution un peu mieux que la version 0
        '''
        positions_vides = {}
        for position in self.cellules:
            positions_vides.update({pos : True for pos in self.voisines(position) if pos not in self.cellules or self.cellules[pos].vivante != True})
        return positions_vides

    @exec_time
    def nb_voisines(self, position):
        '''Renvoie le nombre de voisines limité à 4 (4 equivaut à (4 ou 5 ou 6 ou 7 ou 8))
        '''
        nb = 0
        for voisine in self.voisines(position):
            cellule = self.cellules.get(voisine)
            if cellule and cellule.vivante is not None:
                nb +=1
                if nb == 4:
                    return 4
        return nb

    def voisines(self, position):
        '''générateur de voisines
        '''
        for offset in self.offsets:
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
    plateau = Plateau(300,100)
    #n=24
    #for i in range(n):
        #plateau.add(P(int(plateau.largeur/2 - n/2 )+i,int(plateau.hauteur / 2)))
    #Un planeur
    plateau.add([P(3,11),P(1,12),P(3,12),P(2,13),P(3,13)])
    plateau.aleat_polulate(0.1)
    plateau.root.mainloop()
