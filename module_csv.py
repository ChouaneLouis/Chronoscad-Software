import csv

def from_csv(nom_fichier : str):
  """ retourne le contenu d'un fichier csv sous forme de liste
  :param: nom_fichier : nom du fichier csv"""
  with open(nom_fichier) as fichier:
    return list(csv.reader(fichier, delimiter=','))
