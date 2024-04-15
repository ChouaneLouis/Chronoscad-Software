from typing import List
from random import choice
from module_edt import Edt, Salle, Matiere, Prof, Groupe, Element
from module_csv import *


class Data:
  """ centralisation les données necessaires a la génération de l'EDT """
  
  def __init__(self, nom_fichier : str):
    """ créer les objets Etudiant, Matiere, Prof et Salle définie par un csv source
    syntaxe du csv, voir : 'format csv de groupe'
    :param: nom_fichier : nom du fichier csv des groupes, prof, salle et matières """
    self.profs = []
    self.salles = []
    self.matieres = []
    self.deroulement = {}
    self.groupes = []
    
    self.all = {} #dictionnaire avec tous les objets 'Prof', 'Salle', 'Matiere' et 'Groupe'
    #permet la recherche d'objet par nom (ou par capacité pour les salles)

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

  def contrainte_prof(self, csv : str):
    # a appeler dans import semaine
    """importe les contraintes des professeurs : dispo ou pas
    :param: csv : nom du fichier csv source"""
    data = from_csv(csv)
    a=int((len(data)-2)/8)
    for i in range(a):
      liste_contrainte=data[1+i*8:9+i*8]
      prof = self.all.get(liste_contrainte[0][0].title())

      prof.contrainte=[[float(liste_contrainte[2 + heure][jour]) for heure in range(6)] for jour in range(5)]

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
  
  def importe_semaine(self, nom_fichier : str):
    """ importe les données d'une semaine : volume horaires, ordre td/cm etc
    syntaxe du csv, voir : 'format csv de semaine'
    :param: nom_fichier : nom du fichier csv source
    :return: ({(prof : Prof, type : str (TD, CM, TP), cours : Matiere) : nb d'heure},
    {(td : Groupe, type : str (TD, CM, TP), cours : Matiere) : nb d'heure}) """
    data = from_csv(nom_fichier)
    dic_prof={}
    dic_groupe = {}

    i=0
    while data[i][0] !='FIN': #cherche la place de 'fin' dans la liste 
      i=i+1
      
    liste_prof=data[1:i]
    for j, nom_prof_j in enumerate(liste_prof[0]): #parcours en largueur
      for k in range(1,len(liste_prof),2): #parcours en hauteur une case sur deux
        if liste_prof[k][j] != '':
          type, nom_matiere = liste_prof[k][j].split(maxsplit=1) #sépare le type et nom de la matière
          prof = self.all.get(nom_prof_j.title()) #récupère l'objet 'Prof' correspondant au prof
          matiere = self.all.get(nom_matiere.title()) #récupère l'objet 'Matiere' correspondant à la matiere
          cle_prof = (prof, type, matiere) #créer la clé prof,type,matière
          dic_prof[cle_prof] = int(liste_prof[k+1][j]) #ajoute la clé et le nombre d'heure à la liste

    liste_groupe = data [i+2:-1]
    for j, nom_groupe_j in enumerate(liste_groupe[0]):
      for k in range(1,len(liste_groupe),2):
        if liste_groupe[k][j] != '':
          type, nom_matiere = liste_groupe[k][j].split(maxsplit=1)
          groupe = self.all.get(nom_groupe_j)
          matiere = self.all.get(nom_matiere.title())
          cle_eleve = (groupe, type, matiere)
          dic_groupe[cle_eleve] = int(liste_groupe[k+1][j])
    
    return (dic_prof,dic_groupe)
  
  def association(self, nom_fichier : int):
    """creer les objet 'Element' en associant les objets 'Prof', 'Salle', 'Matiere' et 'Groupe' pour correspondre aux volumes horaires d'une semaine
    :param: volume_horaire : return de la fonction importe_semaine """
    dict_prof, dict_eleve = self.importe_semaine(nom_fichier)
    elements = []
    
    for tuple_groupe, heure_groupe in dict_eleve.items():
      groupe = tuple_groupe[0]
      type = tuple_groupe[1]
      matiere = tuple_groupe[2]
      salle = self.chercher_salle_capa(groupe.effectif)
      
      matiere_id = tuple_groupe[1:]
      heure = heure_groupe
      for tuple_prof, heure_prof in dict_prof.items():
        if tuple_prof[1:] == matiere_id:
          prof = tuple_prof[0]
          if heure <= heure_prof:
            dict_prof[tuple_prof] -= heure
            elements += [Element(salle, groupe, prof, matiere, type) for _ in range(heure)]
            break
          elif heure > heure_prof:
            dict_prof[tuple_prof] = 0
            elements += [Element(salle, groupe, prof, matiere, type) for _ in range(heure_prof)]
            heure -= heure_prof
      
    return elements


  def creation_edt(self, nom_fichier, cren_par_jour : List[int],csv_cont_prof: str):
    """creer un objet 'Edt' et le remplit aleatoirement d'objets 'Element' correspondant a ceux de la semaine
    :param: volume_horaire : return de la fonction importe_semaine
    :param: cren_par_jour : liste du nombre de créneaux par jour
    :param: csv_cont_prof : csv des contraintes des profs
    (necessaire pour la creation de l'edt, voir 'module_edt.py') """
    edt = Edt(cren_par_jour)
    elements = self.association(nom_fichier)
    self.contrainte_prof(csv_cont_prof)
    for element in elements:
      jour, heure = choice(list(edt.dict_cout_creneau))

      edt.append(element, jour, heure)

    return edt
  
  def deroulement_ped (self, nom_fichier : str) :
    """ traite le deroulement pedagogique a partir du fichier csv
    :param: nom_fichier : nom du fichier csv source
    :return: {matiere : [{prof : (groupe)}]} """
  
    data = from_csv(nom_fichier)
    dic_dped = {}
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
      dic_dped[matiere] = liste_prof_groupe
      #Passe a la matiere suivante
      i = j + 1

    return dic_dped

  def jour(jour):
    print(jour)
    if jour=="Lundi":
        return 0
    elif jour=="Mardi":
        return 1
    elif jour=="Mercredi":
        return 2
    elif jour=="Jeudi":
        return 3
    elif jour=="Vendredi":
        return 4
    else:
        return None

  def fixes(self, nom_fichier: str):
    """
    traite les crénaux et salles fixes a partir du fichier csv
    :param nom_fichier: nom du fichier csv source
    :return:
    """
    jours = {"Lundi": 0, "Mardi": 1, "Mercredi": 2, "Jeudi": 3, "Vendredi": 4}
    data = from_csv(nom_fichier)
    liste_global = []
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
                  liste_global.append(liste_data)
                else:
                  liste_global.append(liste_data)

    return liste_global

  def association_2 (self, nom_fichier_deroulement_peda : str, nom_fichier_fixe : str) :
    """ creer les objet 'Element' en associant les objets 'Prof',
    'Salle', 'Matiere' et 'Groupe' pour correspondre aux volumes
    horaires d'une semaine
    :param: nom_fichier_deroulement_peda : nom du fichier csv source
    :return: [Element] """
    #recuperation du deroulement pedagogique 
    #{matiere : [{prof : (groupe)}]}
    self.deroulement = self.deroulement_ped(nom_fichier_deroulement_peda)
    self.fixe = self.fixes(nom_fichier_fixe)
    
    elements = []
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
        elements += elements_avant
        elements_avant = elements_nouveau

      elements += elements_avant

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
        elements.append(element)
      elif cours[3] is None and cours[4] is not None:
        salle = self.chercher_salle_nom(cours[4])
        element = Element(salle, groupe, prof, matiere)
        elements.append(element)

    #exclusion groupe
    for groupe in self.groupes:
      groupe.exlure(self.groupes)
              
    return elements

  def creation_edt_2(self, nom_fichier, cren_par_jour : List[int],csv_cont_prof: str, csv_cren_fixe: str):
    """creer un objet 'Edt' et le remplit aleatoirement d'objets 'Element' correspondant a ceux de la semaine
    :param: volume_horaire : return de la fonction importe_semaine
    :param: cren_par_jour : liste du nombre de créneaux par jour
    :param: csv_cont_prof : csv des contraintes des profs
    :param: csv_cren_fixe : csv des creaneau fixe de l'edt
    (necessaire pour la creation de l'edt, voir 'module_edt.py') """
    edt = Edt(cren_par_jour)
    elements = self.association_2(nom_fichier,csv_cren_fixe)
    self.contrainte_prof(csv_cont_prof)
    for element in elements:
      jour, heure = choice(list(edt.dict_cout_creneau))
      if element.creneau is not None :
        jour, heure = element.creneau

      edt.append(element, jour, heure)
  
    return edt

  