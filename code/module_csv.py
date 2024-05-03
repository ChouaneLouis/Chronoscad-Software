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


import csv
from module_edt import *

def from_csv(nom_fichier : str):
  """ retourne le contenu d'un fichier csv sous forme de liste
  :param: nom_fichier : nom du fichier csv"""
  with open(nom_fichier) as fichier:
    return list(csv.reader(fichier, delimiter=','))

def to_csv(nom_fichier : str, data):
  with open(nom_fichier, 'w', newline="") as file:
    csvwriter = csv.writer(file)
    csvwriter.writerows(data)

def edt_to_csv(nom_fichier, edt):
  data = []
  crens = edt.cren_par_jour
  data.append(crens)
  for jour, nb_cren in enumerate(crens):
    for heure in range(nb_cren):
      row = []
      for cours in edt.get(jour, heure):
        row.append(" § ".join([cours.groupe_salle.nom, cours.groupe.nom, cours.prof.nom, cours.matiere.nom]))
      data.append(row)

  to_csv(nom_fichier, data)


def csv_to_edt(nom_fichier, all):
  data = from_csv(nom_fichier)
  crens = []
  for i in data.pop(0):
    if i == "":
      break
    crens.append(int(i))

  edt = Edt(crens)

  for jour, nb_cren in enumerate(crens):
    for heure in range(nb_cren):
      row = data.pop(0)
      for noms_str in row:
        noms = noms_str.split(" § ")
        element = Element(all[noms[0]], all[noms[1]], all[noms[2]], all[noms[3]])
        edt.append(element, jour, heure)
      data.append(row)

  return edt
