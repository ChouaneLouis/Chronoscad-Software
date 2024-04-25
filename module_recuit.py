from typing import List
from random import choice

from module_edt import Edt, Element
from ui_interface import *
from module_csv import *


class Recuisson:
  def __init__(self, all, semaine, cren_par_jour):
    self.all = all
    self.semaine = semaine
    self.cren_par_jour = cren_par_jour
    self.temperature = 1

    #tri dans des listes separees
    self.prof = []
    self.groupe = []
    self.salle = []
    self.matiere = []
    for item in all.values():
      if isinstance(item, UIProf):
        self.prof.append(item)
      elif isinstance(item, UIGroupe):
        self.groupe.append(item)
      elif isinstance(item, UISalle):
        self.salle.append(item)
      elif isinstance(item, UIMatiere):
        self.matiere.append(item)

    #exclusion groupe
    for groupe in self.groupe:
      groupe.exlure(self.groupe)

    #recupere le deroulement peda
    self.deroulement = {}
    for matiere in self.matiere:
      self.deroulement[matiere] = matiere.cget_week("deroulement_peda", semaine)

    #genere les elements
    self.elements = self.association()

  def chercher_salle_capa(self, capacite : int):
    """cherche et return la plus petite salle de capacité >= à 'capacite'
    :param: capacite : capacité minimal de la salle"""
    meilleur_salle = None
    meilleur_capa = 10000 # A CHANGER

    for salle in self.salle:
      if salle.capacite >= capacite and salle.capacite < meilleur_capa :
        meilleur_salle = salle
        meilleur_capa = salle.capacite

    if meilleur_salle is None:
      raise ValueError("pas de salle de capacité >= à " + str(capacite))
    return meilleur_salle

  def association(self):
    """ creer les objet 'Element' en associant les objets 'Prof', 'Salle', 'Matiere' et 'Groupe' pour correspondre aux contraintes du deroulement pedagogique
    :return: [Element] """
    
    elements = []
    for matiere, liste_cours_parallele in self.deroulement.items(): #{Matiere : [({Prof:(Groupe)}, (j, h), duree, Salle)]}
      
      elements_avant = []
      for tuple_cours_parrallele in liste_cours_parallele: #[({Prof:(Groupe)}, (j, h), duree, Salle)]
        elements_nouveau = []
        dict_prof_groupe = tuple_cours_parrallele[0]
        creneau = tuple_cours_parrallele[1]
        duree = tuple_cours_parrallele[2]
        salle = tuple_cours_parrallele[3]

        for prof, tuple_groupe in dict_prof_groupe.items():
          for groupe in tuple_groupe :
            if salle is None:
              salle = self.chercher_salle_capa(groupe.effectif)
            for i in range(duree):
              #creer l'element
              element = Element(salle, groupe, prof, matiere)
              if creneau is not None:
                element.creneau = (creneau[0], creneau[1] + i)

              #associe les elements avants
              element.avant = elements_avant
              #garde en memoire l'element cree
              elements_nouveau.append(element)

        #associe les elements apres
        for element_avant in elements_avant:
          element_avant.apres = elements_nouveau
  
        #transvase les elements dans les liste
        elements += elements_avant
        elements_avant = elements_nouveau

      elements += elements_avant
              
    return elements

  def new_edt(self):
    """creer un objet 'Edt' et le remplit aleatoirement d'objets 'Element' correspondant a ceux de la semaine """
    edt = Edt(self.cren_par_jour)

    creneaux = [(j, h) for j in range(len(self.cren_par_jour)) for h in range(self.cren_par_jour[j])]
    for element in self.elements:
      jour, heure = choice(creneaux)
      if element.creneau is not None :
        jour, heure = element.creneau

      edt.append(element, jour, heure)
  
    return edt

  def new_batch(self, count):
    """"""
    cout_moyen = 0
    meilleur_cout = 1000000000

    self.count = count
    self.edts = []
    self.couts = []
    for _ in range(count):
      edt = self.new_edt()
      cout = edt.cout_edt_total()

      self.edts.append(edt)
      self.couts.append(cout)

      cout_moyen += cout
      if cout < meilleur_cout:
        meilleur_cout = cout
    cout_moyen /= count

    self.cout_moyen = cout_moyen
    self.meilleur_cout = meilleur_cout

  def do_swaps(self, nb_swaps):
    """"""
    cout_moyen = 0
    meilleur_cout = 1000000000

    for i, edt in enumerate(self.edts):
      for _ in range(nb_swaps):
        edt.saut(self.temperature)
      self.couts[i] = edt.cout

      cout_moyen += edt.cout
      if edt.cout < meilleur_cout:
        meilleur_cout = edt.cout

    self.cout_moyen = cout_moyen
    self.meilleur_cout = meilleur_cout

  def get_best(self, nb):
    meilleurs_cout = [1000000000] * nb
    meilleurs_edt = [None] * nb

    for i, edt in enumerate(self.edts):
      if edt.cout < meilleurs_cout[-1]:
        for j, cout in enumerate(meilleurs_cout):
          if edt.cout < cout:
            meilleurs_edt.insert(j, edt)
            meilleurs_edt.pop()
            meilleurs_cout.insert(j, edt.cout)
            meilleurs_cout.pop()
            break

    return meilleurs_edt

  def selection(self, nb):
    self.edts = self.get_best(nb)