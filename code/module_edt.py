#Copyright (C) 2024  see AUTHORS.txt
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.


from math import exp
from typing import List
from random import choice, random


class Prof:
  def __init__(self, nom : str):
    """ un professeur
    :param: nom : nom du prof """
    self.nom = nom
    self.contrainte = None

    self.cours = [0 for i in range(6)]


class Salle:
  def __init__(self, nom : str, *, capacite : int = 0):
    """ groupe de salles de même capacité
    :param: nom : nom de la salle
    :param: capacite : capacite de la salle """
    self.noms = [nom]
    self.nombre = 1
    self.capacite = capacite

  def append(self, nom : str):
    """ ajoute une salle au groupe
    :param: nom : nom de la salle """
    self.noms.append(nom)
    self.nombre += 1

    return self


class Matiere:
  def __init__(self, nom : str, *, couleur : str = ""):
    """ une matiere
    :param: nom : nom de la matiere
    :param: couleur : couleur de la matiere lors de l'affichage (methode 'show') """
    self.nom = nom
    self.deroulement_ped = [] ### c'est quoi cq ?
    if couleur == "":
      couleur = "bgrcmy"[ord(nom[0]) % 6]
    self.couleur = couleur


class Groupe:
  def __init__(self, nom : str):
    """ un groupe d'etudiants
    :param: nom : nom du groupe
    :param: etudiants : liste des étudiants """
    self.nom = nom
    self.etudiants = []
    self.effectif = 0

    self.exclusion = {self} #set des groupes qui ont des etudiants commun à self

  def __contains__(self, etudiant : str):
    """ operateur in
    verifie que 'etudiant' est dans le groupe """
    return etudiant in self.etudiants

  def __iadd__(self, groupe):
    """ operateur +=
    ajouter une liste d'étudiants au groupe
    :param: etudiants : liste des étudiants à ajouter """
    self.etudiants = list(set(self.etudiants + groupe.etudiants))
    self.effectif = len(self.etudiants)

    self.exclusion.add(groupe)
    groupe.exclusion.add(self)

    return self

  def add(self, etudiant : str):
    """ ajouter un étudiants au groupe
    :param: etudiant : étudiant à ajouter """
    self.etudiants.append(etudiant)
    self.effectif = len(self.etudiants)

  def exlure(self, groupes):
    for groupe in groupes:
      if groupe in self.exclusion:
        continue
      if list(set(self.etudiants).intersection(set(groupe.etudiants))):
        self.exclusion.add(groupe)
        groupe.exclusion.add(self)


class Element:
  """ simple structure de donnée pour les éléments de l'EDT """
  def __init__(self, groupe_salle : Salle, groupe : Groupe, prof : Prof, matiere : Matiere, *, creneau = None):
    self.groupe_salle = groupe_salle
    self.groupe = groupe
    self.prof = prof
    self.matiere = matiere
    self.creneau = creneau
    
    self.autre = [] #list(Element) : liste des cours adjacents a celui ci (crenneau multiple)
    
    self.avant = [] #list(Element) : liste des cours directement avant (déroulement péda)
    self.apres = [] #list(Element) : liste des cours directement apres (déroulement péda)

  def __str__(self):
    return f"{self.groupe.nom} avec {self.prof.nom} en {self.matiere.nom}"
    

class Edt:
  def __init__(self, cren_par_jour : List[int], heure_pause : int = 2):
    """ classe principale de l'edt, contient une liste d'objets 'Element' par crenaux
    :param: cren_par_jour : liste du nombre de créneaux par jour """
    self.cren_par_jour = cren_par_jour
    self._nombre_jour = len(cren_par_jour)
    self._creneau = [[[] for j in range(i)] for i in cren_par_jour]
    self._dict_cours = {} #dictionaire {Element : (jour, heure)}
    self._heure_pause = heure_pause
    self._liste_prof = set()

    self.dict_cout_creneau = {(j, h) : (h**2)/50 for j, h_max in enumerate(cren_par_jour) for h in range(h_max)} ##valeur en dure a changer 
    self.cout = 0

  def append(self, element : Element, jour : int, heure : int):
    """ ajoute un element à la liste 'self._creneau'
    et modifie 'self._dict_cours' de maniere adequate
    :param: element : objet 'Element' à ajouter
    :param: jour & heure : jour et heure de l'element """
    self._creneau[jour][heure].append(element)
    self._dict_cours[element] = (jour, heure)

    element.prof.cours[jour] += 1
    if element.prof not in self._liste_prof:
      self._liste_prof.add(element.prof)

  def get(self, jour, heure):
    return self._creneau[jour][heure]

  def deplacer(self, element : Element, cren_dep, cren_arr):
    """ deplace un element dans l'edt
    :param: element : objet 'Element' à deplacer
    :param: cren_dep & cren_arr : (jour, heure) creneau de depart et d'arrivée """
    #retirer le cours
    self._creneau[cren_dep[0]][cren_dep[1]].remove(element)
    #ajoute le cours
    self._creneau[cren_arr[0]][cren_arr[1]].append(element)
    self._dict_cours[element] = (cren_arr[0], cren_arr[1])
    #changement des donnée du prof
    element.prof.cours[cren_dep[0]] -= 1
    element.prof.cours[cren_arr[0]] += 1
  
  """def copy(self, other):
    self.cren_par_jour = other.cren_par_jour
    self._nombre_jour = other._nombre_jour
    self._creneau = 
    self._dict_cours = 
    self._heure_pause = other._heure_pause

    self.dict_cout_creneau = other.dict_cout_creneau
    self.cout = other.cout"""
    
  def cout_horaire(self, cours : Element, creneau):
    """Ajoute un coup extra aux creneaux que l'utilisateur souhaite qui soint vides
     -> cout de cours 'simple' """
    coeff = self.dict_cout_creneau[creneau]
    if cours.prof.contrainte is not None:
      coeff += cours.prof.contrainte[creneau[0]][creneau[1]]
    return 100 * coeff

  def cout_deroulement_peda(self, cours : Element, creneau):
    """ calcul le cout due à la position dans le deroulement péda
     -> cout de cours 'mixte'
    :param: cours : objet 'Element' dont il faut calculer le cout
    :param: creneau : (jour, heure) creneau du cours
    :return: int : 100 par cours mal placé par rapport au cours 'cours' """
    cout = 0

    if cours.creneau is not None:
      return 0
      
    for cours_apres in cours.apres:
      horaires_cours_apres = self._dict_cours[cours_apres]
      #Comparer horaires
      if horaires_cours_apres <= creneau :
        cout += 100
        
    for cours_avant in cours.avant:
      horaires_cours_avant = self._dict_cours[cours_avant]
      #Comparer horaires
      if horaires_cours_avant >= creneau :
        cout += 100
    
    return cout 
    
  def cout_creneau_multiple(self, cours : Element, creneau) :
    """ calcul le coût due aux créneaux multiples d'un cours
     -> coût de cours 'mixte' 
    :param: cours : objet 'Element' dont il faut calculer le cout
    :param: creneau : (jour, heure) creneau du cours
    :return: int : 100 si les cours ne sont pas a côté, + 100 s'ils ne sont pas le meme jour"""
    cout = 0
    jour, heure = creneau
      
    if cours.autre == []:
      return 0
      
    #on recupere la liste des heures des cours de autres qui sont le meme jour que le cours 'cours'
    #pour chaque cours qui ne sont pas le meme jour que le cours 'cours' on ajoute 200 au cout
    liste_heure = [heure]
    for cours_autre in cours.autre:
      jour_autre, heure_autre = self._dict_cours[cours_autre]
      if jour_autre != jour :
        cout += 90 / len(cours.autre)
        continue
      else :
        liste_heure.append(heure_autre)

    #on tri la liste des heures dans l'ordre croissant
    liste_heure.sort()
    dernier = len(liste_heure) - 1 #indice du dernier element
    #on verifie si les cours sont a la suite
    heure_min = liste_heure[0]
    for i, heure_i in enumerate(liste_heure):
      if heure_i == self._heure_pause and i != dernier: #si le cours chevauche le déjeuner on ajoute un coût de 100
        cout += 40 / len(cours.autre)
      if heure_i - heure_min != i:
        cout += 40 / len(cours.autre)
        
    return cout
  
  def cout_prof(self, liste_prof, cours : Element | None, present : bool):
    """ calcul le cout due au prof d'un creneau / cours
     -> coût general
    :param: liste_prof : liste des profs du creneau
    :param: cours : cours à evalué si None evalue le creneau
    :param: present : booléen indiquant si le cours est deja present dans le creneau ou non """
    cout = 0
    if cours is None: #pour le coût d'un creneau entier
      for prof in set(liste_prof): #set() permet de ne garder qu'un seul élément prof
        cout += (liste_prof.count(prof) - 1) * 100
    else: #pour le coût d'un unique cours
      prof = cours.prof
      nb_prof = liste_prof.count(prof)
      if present: #si le cours est deja present dans le créneau le prof du cours ne coute pas
        nb_prof -= 1
      if nb_prof > 0:
        cout = 100
    return cout

  def cout_groupe(self, liste_groupe, cours : Element | None, present : bool):
    """ calcul le cout due au groupe d'élève d'un creneau / cours
     -> coût general
    :param: liste_groupe : liste des groupe du creneau
    :param: cours : cours à evalué si None evalue le creneau
    :param: present : booléen indiquant si le cours est deja present dans le creneau ou non """
    cout = 0
    if cours is None: #pour le coût d'un creneau entier
      for i, groupe_i in enumerate(liste_groupe[:-1]): #on compare les groupes 2 a 2
        for groupe_j in liste_groupe[i+1:]:
          if groupe_j in groupe_i.exclusion:
            cout += 100
    else: #pour le coût d'un unique cours
      groupe_exclusion = cours.groupe.exclusion
      for groupe_i in liste_groupe:
        if groupe_i in groupe_exclusion:
          cout += 100
      if present and cout > 0: #si le cours est deja present dans le créneau le groupe du cours ne coute pas
        cout -= 100
    return cout

  def cout_salle(self, liste_salle, cours : Element | None, present : bool):
    """ calcul le cout due au salle d'un creneau / cours
     -> coût general
    :param: liste_salle : liste des salles du creneau
    :param: cours : cours à evalué si None evalue le creneau
    :param: present : booléen indiquant si le cours est deja present dans le creneau ou non """
    cout = 0
    if cours is None: #pour le coût d'un creneau entier
      for salle in set(liste_salle): #set() permet de ne garder qu'un seul élément salle
        nb_salle = liste_salle.count(salle)
        if nb_salle > salle.nombre:
          cout += (nb_salle - salle.nombre) * 100
    else : #pour le coût d'un unique cours
      salle = cours.groupe_salle
      nb_salle = liste_salle.count(salle)
      if not present: #si Le cours etait présent dans le créneau il occuperait une salle de plus
        nb_salle += 1
      if nb_salle > salle.nombre:
        cout = 100 #le cours creer un cout de 100
    return cout
  
  def cout_creneau(self, creneau, *, cours : Element | None = None, present : bool = True):
    """ une fonction qui evalue le cout d'un unique creneau ou cours, evalue si :
      - Plusieurs fois le même prof
      - Plusieurs fois le même groupe
      - Le même groupe de salle est utiliser trop de fois
      - Les creneau multiple sont à coté
      - Le deroulement pedagogique est respecté
    :param: creneau : (jour, heure) du creneau à evaluer
    :param: cours : cours dont il faut evaluer le cout dans le creneau (si None le creneau entier est évalué)
    :param: present : booléen indiquant si le cours est deja present dans le creneau ou non
    :return: cout du creneau / cours """
    cout = 0
    jour, heure = creneau

    liste_prof, liste_groupe, liste_salle = [], [], []
    for cours_i in self._creneau[jour][heure]:
      #couts de cours : pour un calcul total 
      if cours is None:
        cout += self.cout_deroulement_peda(cours_i, creneau) * 0.5
        cout += self.cout_creneau_multiple(cours_i, creneau) * 0.5

        cout += self.cout_horaire(cours_i, creneau)
      #recupère la liste des prof, groupe et salle
      liste_prof.append(cours_i.prof)
      liste_groupe.append(cours_i.groupe)
      liste_salle.append(cours_i.groupe_salle)

    #couts de cours : pour un deplacement
    if cours is not None:
      cout += self.cout_deroulement_peda(cours, creneau)
      cout += self.cout_creneau_multiple(cours, creneau)
      
      cout += self.cout_horaire(cours, creneau)
    #couts generaux
    cout += self.cout_prof(liste_prof, cours, present)
    cout += self.cout_groupe(liste_groupe, cours, present)
    cout += self.cout_salle(liste_salle , cours, present)
    
    return cout

  def delta_cout_prof_cours(self, cours, cren_dep, cren_arr):
    """"""
    liste_cours = cours.prof.cours[:]
    delta_cout = - self.cout_prof_cours_liste(liste_cours)
    
    liste_cours[cren_dep[0]] -= 1
    liste_cours[cren_arr[0]] += 1

    delta_cout += self.cout_prof_cours_liste(liste_cours)

    return delta_cout
  
  def cout_prof_cours_liste(self, liste_cours):
    """"""
    delta_x = 0
    somme = 0
    for i in liste_cours:
      delta_x += i**2
      somme += i
    return i * 20 / delta_x

  def cout_edt_total(self):
    """ utilise la fonction cout_creneau pour calculer le coût total de l'EDT :
    somme du cout de chaque créneau """
    cout_edt_tot = 0
    for creneau in self.dict_cout_creneau:
      cout_edt_tot += self.cout_creneau(creneau)

    self.cout = cout_edt_tot

    for prof in self._liste_prof:
      cout_edt_tot += self.cout_prof_cours_liste(prof.cours)

    return cout_edt_tot

  def choix_saut(self):
    """ fonction qui choisit un cours à déplacer vers un créneau différent
    :return: (cours (Element),
        creneau_depart : (jour, heure),
        creneau_arrivee : (jour, heure)) 
    Remarque : tourne à l'infini si tous les créneaux sont fixes"""
    cours_initial = choice(list(self._dict_cours.keys()))
    while cours_initial.creneau is not None:
      #choisi un cours parmi tous ceux de l'edt qui sont non fixes
      cours_initial = choice(list(self._dict_cours.keys()))
    #recupère le creneau du cours choisi
    creneau_depart = self._dict_cours[cours_initial]
    #choisi un creneau parmi ceux disponibles different de celui de depart
    creneau_arrivee = creneau_depart
    while creneau_arrivee == creneau_depart:
      creneau_arrivee = choice(list(self.dict_cout_creneau))

    return (cours_initial, creneau_depart, creneau_arrivee)

  def delta_cout(self, cours : Element, creneau_depart, creneau_arrivee):
    """ fonction qui permet de calculer le delta de cout d'un déplacement
    :param: cours : cours à déplacer
    :param: creneau_depart : (jour, heure) du créneau de depart
    :param: creneau_arrivee : (jour, heure) du créneau d'arrivee
    :return: variation du cout causé par ce deplacement """
    
    #Calcul du coût du créneau de départ et de celui d'arrivée
    cout_local_initial = self.cout_creneau(creneau_depart, cours = cours, present = True)
    
    #Calcul du coût du créneau de départ et de celui d'arrivée, avec le deplacement fait virtuellement
    cout_local_final = self.cout_creneau(creneau_arrivee, cours = cours, present = False)

    return cout_local_final - cout_local_initial + self.delta_cout_prof_cours(cours, creneau_depart, creneau_arrivee)
    
  def saut(self, temperature : float):
    """ déplace un cours vers un autre créneaux si ce deplacement  :
      - reduit le cout total de l'edt
      - ou est autorisé a la temperature donnée
    :param: temperature : coefficien pour autoriser les déplacements non rentables au début
    :return: delta_cout : variation du cout causé par ce deplacement """
    #choix et evluation du deplacement
    cours, creneau_dep, creneau_arr = self.choix_saut() 
    delta_cout = self.delta_cout(cours, creneau_dep, creneau_arr)
    #decide si le deplacement est autorisé
    if delta_cout <= 0 or random() < exp(-delta_cout / temperature):
      self.deplacer(cours, creneau_dep, creneau_arr)
      self.cout += delta_cout
      return delta_cout
    else:
      return 0

  def verif_final(self):
    '''Verifie la validité d'un emplois du temps en vérifiant les contarintes obligatoire 
    -créneaux multi et déroulment péda
    -prof indisponible
    -2prof/2salle/2TD sur le même créneau
    :return: probleme liste des problème de la semaine par créneau de la forme [type pb,jour,heure]  '''
    probleme=[]
    for creneau in self.dict_cout_creneau:
      jour,heure=creneau
      liste_prof, liste_groupe, liste_salle = [], [], []
      for cours_i in self._creneau[jour][heure]:
        liste_prof.append(cours_i.prof)
        liste_groupe.append(cours_i.groupe)
        liste_salle.append(cours_i.groupe_salle)
      for cours_i in self._creneau[jour][heure]:
        a=str(jour) + " " + str(heure)
        #couts de cours : pour un calcul total 
        if self.cout_deroulement_peda(cours_i, creneau) !=0:
          print ('error déroulement péda à '+a, cours_i)
          probleme.append(['peda',jour,heure])
        if self.cout_creneau_multiple(cours_i, creneau) !=0:
          print ('cours multiple à'+a)
          probleme.append(['multi',jour,heure])
        if cours_i.prof.contrainte is not None and cours_i.prof.contrainte[jour][heure]==1:
          print ('le prof:',cours_i,'n est pas dispo le '+a)
          probleme.append(['dispo prof',jour,heure])
        present=True
        if self.cout_prof(liste_prof, cours_i, present) !=0:
          print ('error prof 2 fois sur le créneau à '+a, cours_i)
          probleme.append(['2 prof',jour,heure])
        if self.cout_groupe(liste_groupe, cours_i, present) !=0:
          print( 'error groupe 2 fois sur le créneau à '+a,cours_i)
          probleme.append(['2 groupe',jour,heure])
        if self.cout_salle(liste_salle , cours_i, present) !=0:
           print ('error salle 2 fois sur le créneau à '+a,cours_i)
           probleme.append(['2 salle',jour,heure])
    if len(probleme)==0:
      print ('emplois du temps validé')
    return probleme
