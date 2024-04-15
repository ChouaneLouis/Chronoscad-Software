from random import choice
from module_edt import Edt, Salle, Matiere, Prof, Groupe, Element
from module_csv import *


class Data:
  """ centralisation des données necessaires a la génération de l'EDT """

  def __init__(self, cren_par_jour):
    """ créer les objets Etudiant, Matiere, Prof et Salle définie par un csv source
    syntaxe du csv, voir : 'format csv de groupe'
    :param: nom_fichier : nom du fichier csv des groupes, prof, salle et matières """
    self.cren_par_jour = cren_par_jour
    
    self.profs = []
    self.salles = []
    self.matieres = []
    self.groupes = []

    self.all = {} #dictionnaire avec tous les objets 'Prof', 'Salle', 'Matiere' et 'Groupe'
    #permet la recherche d'objet par nom (ou par capacité pour les salles)
    
    self.deroulement = {}
    self.fixe = []
    self.elements = []

  def importer_data(self, nom_fichier : str):
    """ importe les données générales d'un fichier csv """
    data = from_csv(nom_fichier)
    #création des objets 'Prof', 'Salle' et 'Groupe''
    while len(data) != 0:
      intitule = data.pop(0)[0].lower() #contenu de la premiere case de la premiere ligne

      if intitule == "professeurs": #création des objets 'Prof'
        profs = data.pop(0) #recuperation de la liste des noms des professeurs
        for prof in profs:
          if prof == "": #fin de la liste
            break

          self.profs.append(Prof(prof.title()))
          self.all[prof.title()] = self.profs[-1]

      elif intitule == "salles": #création des objets 'Salle'
        salles = data.pop(0) #recuperation de la liste des noms des salles
        capacites = data.pop(0) #recuperation des capacités des salles
        for i, salle_i in enumerate(salles):
          if salle_i == "": #fin de la liste
            break

          capacite_i = capacites[i]
          #s'il existe déjà une salle avec cette capacité, on la récupère
          s = self.all.get('#' + capacite_i)
          if s is not None: #ajout de la salle à la liste de salle trouvé
            s.append(salle_i)
          else: #création d'une nouvelle salle
            s = Salle(salle_i, capacite = int(capacite_i))
            self.salles.append(s)
            self.all['#' + capacite_i] = s

      elif intitule == "matieres": #création des objets 'Matiere'
        matieres = data.pop(0) #recuperation de la liste des noms des matieres
        couleurs = data.pop(0) #recuperation de la liste des couleurs associées
        for i, matiere_i in enumerate(matieres):
          if matiere_i == "": #fin de la liste
            break

          self.matieres.append(Matiere(matiere_i.title(), couleur = couleurs[i]))
          self.all[matiere_i.title()] = self.matieres[-1]

      elif intitule == "groupes": #création des objets 'Groupes'
        groupes = data.pop(0) #recuperation de la liste des noms des groupes
        for i, groupe_i in enumerate(groupes):
          if groupe_i == "": #fin de la liste
            break

          n_groupe = Groupe(groupe_i) #creation du groupe
          self.groupes.append(n_groupe)
          self.all[groupe_i] = n_groupe

          for j, ligne_j in enumerate(data): #ajout des étudiants au groupe
            etudiant = ligne_j[i]
            if etudiant == "":
              break
            elif etudiant[0] == "$": #si le nom commence par '$', c'est le nom d'un groupe deja existant
              self.groupes[-1] += self.all[etudiant[1:]]
            else:
              self.groupes[-1].add(etudiant.title())

        break #la liste des groupe est toujours situé a la fin du fichier
        #une fois que tous les groupes ont été créés, on sort de la boucle

      elif intitule == "":
        continue

      else:
        raise ValueError("intitulé inconnu : " + intitule + ', dans le document : ' + nom_fichier)

  def importer_contrainte(self, nom_fichier : str):
    # a appeler dans import semaine
    """importe les contraintes des professeurs : dispo ou pas
    :param: csv : nom du fichier csv source"""
    data = from_csv(nom_fichier)
    a=int((len(data)-2)/8)
    for i in range(a):
      liste_contrainte=data[1+i*8:9+i*8]
      prof = self.all.get(liste_contrainte[0][0].title())
      if prof is None:
        raise ValueError("professeur inconnue : " + liste_contrainte[0][0] + ', dans le document : ' + nom_fichier)

      prof.contrainte=[[float(liste_contrainte[2 + heure][jour]) for heure in range(6)] for jour in range(5)]

  def importer_der_peda (self, nom_fichier : str) :
    """ traite le deroulement pedagogique a partir du fichier csv
    :param: nom_fichier : nom du fichier csv source
    :return: {matiere : [{prof : (groupe)}]} """

    data = from_csv(nom_fichier)
    self.deroulement = {}
    i = 0
    #Traite toutes les matieres jusqu'a trouver FIN_FICHIER
    while data[i][0] != 'FIN_FICHIER':
      liste_type_cours = data[i+1]
      matiere = data[i][0]
      j = i
      #Traite les donnees pour une matiere jusqu'a trouver une ligne de FIN
      while data[j][0] != 'FIN':
        j = j + 1
      deroulement = data[i+1:j]
      liste_prof_groupe = []
      #Parcours les colonnes de deroulement
      for k in range(len(deroulement[0])):
        dic_prof_groupe = {}
        #Parcours les lignes de deroulement
        for l in range(1, len(deroulement), 2):
          if deroulement[l][k] != '':
            groupe = tuple(deroulement[l][k].split())
            prof = deroulement[l+1][k]
            dic_prof_groupe[prof] = groupe
        liste_prof_groupe.append((liste_type_cours[k], dic_prof_groupe))
      self.deroulement[matiere] = liste_prof_groupe
      #Passe a la matiere suivante
      i = j + 1

  def importer_fixes(self, nom_fichier: str):
    """
    traite les crénaux et salles fixes a partir du fichier csv
    :param nom_fichier: nom du fichier csv source
    :return:
    """
    jours = {"Lundi": 0, "Mardi": 1, "Mercredi": 2, "Jeudi": 3, "Vendredi": 4}
    data = from_csv(nom_fichier)
    self.fixe = []
    j = 0
    # Traite toutes les matieres jusqu'a trouver FIN
    while data[j][0] != 'FIN':
      j = j + 1
      # Parcours les lignes du fichier
      if data[j][0] != '':
        cour = data[j][0]
        liste_data = [cour, 0, 0, False, False]
        if data[j][1] != '':
          prof = data[j][1]
          liste_data[1] = prof
          if data[j][2] != '':
            groupe = data[j][2]
            liste_data[2] = groupe
            if data[j][3] != '':
              crenau = data[j][3]
              if jours.get(crenau.split()[0],None)!=None and len(crenau.split())==2: #error liée à l'appelle d'un fonction dans la classe le dico doit le régler?
                liste_data[3]=(jours.get(crenau.split()[0]),int(crenau.split()[1]) - 1)
                if data[j][4]!='':
                  salle=data[j][4]
                  liste_data[4]=salle
                  self.fixe.append(liste_data)
                else:
                  self.fixe.append(liste_data)

  def chercher_salle_capa(self, capacite : int):
    """cherche et return la plus petite salle de capacité >= à 'capacite'
    :param: capacite : capacité minimal de la salle"""
    meilleur_salle = None
    meilleur_capa = 1000 # A CHANGER

    for salle in self.salles:
      if salle.capacite >= capacite and salle.capacite < meilleur_capa :
        meilleur_salle = salle
        meilleur_capa = salle.capacite

    if meilleur_salle is None:
      raise ValueError("pas de salle de capacité >= à " + str(capacite))
    return meilleur_salle

  def chercher_salle_nom(self, nom : str):
    """cherche et return la salle de nom 'nom'
    :param: nom : nom de la salle"""
    for salle in self.salles:
      if nom in salle.noms:
        return salle
    raise ValueError("pas de salle de nom " + nom)

  def creation_element(self, fichier_data, fichier_contrainte, fichier_der_peda, fichier_fixe) :
    """ creer les objet 'Element' en associant les objets 'Prof',
    'Salle', 'Matiere' et 'Groupe' pour correspondre aux volumes
    horaires d'une semaine
    :return: [Element] """
    self.importer_data(fichier_data)
    self.importer_contrainte(fichier_contrainte)
    self.importer_der_peda(fichier_der_peda)
    self.importer_fixes(fichier_fixe)
    
    for nom_matiere, liste_cours_parallele in self.deroulement.items():
      matiere = self.all.get(nom_matiere.title())
      if matiere is None:
        raise ValueError("matiere inconnue : " + nom_matiere)

      elements_avant = []
      for type_cours, dict_prof_groupe in liste_cours_parallele :
        elements_nouveau = []
        for nom_prof, tuple_groupe in dict_prof_groupe.items():
          prof = self.all.get(nom_prof.title())
          if prof is None:
            raise ValueError("prof inconnue : " + nom_prof)

          for nom_groupe in tuple_groupe :
            groupe = self.all.get(nom_groupe)
            if groupe is None:
              raise ValueError("groupe inconnue : " + nom_groupe)

            salle = self.chercher_salle_capa(groupe.effectif)
            #creer l'element
            element = Element(salle, groupe, prof, matiere, type_cours)
            #associe les elements avants
            element.avant = elements_avant
            #garde en memoire l'element cree
            elements_nouveau.append(element)

        #associe les elements apres
        for element_avant in elements_avant:
          element_avant.apres = elements_nouveau

        #transvase les elements dans les liste
        self.elements += elements_avant
        elements_avant = elements_nouveau

      self.elements += elements_avant

    #recuperation des creneau fixe
    for cours in self.fixe:
      matiere = self.all.get(cours[0].title())
      if matiere is None:
        raise ValueError(f"matiere inconnue : {cours[0]}")
      prof = self.all.get(cours[1].title())
      if Prof is None:
        raise ValueError(f"prof inconnue : {cours[1]}")
      groupe = self.all.get(cours[2])
      if groupe is None:
        raise ValueError(f"groupe inconnue : {cours[2]}")

      if cours[3] is not None:
        if cours[4] is None:
          salle = self.chercher_salle_capa(cours[2].effectif)
        else:
          salle = self.chercher_salle_nom(cours[4])
          if salle is None:
            raise ValueError(f"salle inconnue : {cours[4]}")
        #element = Element(salle, groupe, prof, matiere, type_cours, fixe)
        element = Element(salle, groupe, prof, matiere, creneau = cours[3])
        #Rajouter à liste des créneau de edt
        self.elements.append(element)
      elif cours[3] is None and cours[4] is not None:
        salle = self.chercher_salle_nom(cours[4])
        element = Element(salle, groupe, prof, matiere)
        self.elements.append(element)

    #exclusion groupe
    for groupe in self.groupes:
      groupe.exlure(self.groupes)

  def creation_edt(self):
    """creer un objet 'Edt' et le remplit aleatoirement d'objets 'Element' correspondant a ceux de la semaine"""
    edt = Edt(self.cren_par_jour)
    
    for element in self.elements:
      jour, heure = choice(list(edt.dict_cout_creneau))
      if element.creneau is not None :
        jour, heure = element.creneau

      edt.append(element, jour, heure)

    return edt

