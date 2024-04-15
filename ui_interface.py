from module_edt import Prof, Salle, Matiere, Groupe

#OBJET DE L'EDT AFFICHABLE
#PROF
class UIProf(Prof):
  def __init__(self, nom : str, value = None):
    super().__init__(nom)
    self.commentaire = ""
    self.contrainte = [[0 for i in range(6)] for j in range(5)] ### A CHANGER ###

    self.params = {"nom":"text", "commentaire":"textbox", "contrainte":"calendar"}
    self.week_params = {}

    if value is not None:
      self.load(value)

  def cget(self, param):
    if param == "nom":
      return self.nom
    elif param == "commentaire":
      return self.commentaire
    elif param == "contrainte":
      return self.contrainte
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure(self, param, value):
    if param == "nom":
      self.nom = value
    elif param == "commentaire":
      self.commentaire = value
    elif param == "contrainte":
      self.contrainte = value
    else:
      raise ValueError(f"parametre {param} invalide")

  def save(self):
    return {"commentaire":self.commentaire, "contrainte":self.contrainte}

  def load(self, value):
    pass

#SALLE
class UISalle(Salle):
  def __init__(self, nom : str):
    super().__init__(nom)
    self.nom = nom
    self.commentaire = ""

    self.params = {"nom":"text", "commentaire":"textbox", "noms":"textlist", "capacite":"integer"}
    self.week_params = {}

    self.noms = []

  def cget(self, param):
    if param == "nom":
      return self.nom
    elif param == "commentaire":
      return self.commentaire
    elif param == "noms":
      return self.noms
    elif param == "capacite":
      return self.capacite
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure(self, param, value):
    if param == "nom":
      self.nom = value
    elif param == "commentaire":
      self.commentaire = value
    elif param == "noms":
      self.noms = value
      self.nombre = len(value)
    elif param == "capacite":
      self.capacite = value
    else:
      raise ValueError(f"parametre {param} invalide")

#MATIERE
class UIMatiere(Matiere):
  def __init__(self, nom : str):
    super().__init__(nom)
    self.params = {"nom":"text", "commentaire":"textbox", "prof_par_defaut":"prof"}
    self.week_params = {"deroulement_peda":"derpeda"}
    self.default = {"deroulement_peda":"deff"}

    self.commentaire = ""
    self.deff = []
    self.prof_par_defaut = None
    self.deroulement_peda = {}

  def cget(self, param):
    if param == "nom":
      return self.nom
    elif param == "deff":
      return self.deff
    elif param == "commentaire":
      return self.commentaire
    elif param == "prof_par_defaut":
      return self.prof_par_defaut
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure(self, param, value):
    if param == "nom":
      self.nom = value
    elif param == "commentaire":
      self.commentaire = value
    elif param == "prof_par_defaut":
      self.prof_par_defaut = value
    else:
      raise ValueError(f"parametre {param} invalide")

  def cget_week(self, param, semaine):
    if param == "deroulement_peda":
      ret = self.deroulement_peda.get(semaine)
      if ret is None:
        return self.cget(self.default[param])
      else:
        return ret
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure_week(self, param, value, semaine):
    if param == "deroulement_peda":
      if value == self.cget(self.default[param]):
        if self.deroulement_peda.get(semaine) is not None:
          del self.deroulement_peda[semaine]
      else:
        self.deroulement_peda[semaine] = value

      print(self.deroulement_peda)
    else:
      raise ValueError(f"parametre {param} invalide")

#GROUPE
class UIGroupe(Groupe):
  def __init__(self, nom : str):
    super().__init__(nom)
    self.params = {"nom":"text", "commentaire":"textbox", "etudiants":"textlist"}
    self.week_params = {}

    self.commentaire = ""

  def cget(self, param):
    if param == "nom":
      return self.nom
    elif param == "commentaire":
      return self.commentaire
    elif param == "etudiants":
      return self.etudiants
    elif param == "effectif":
      return self.effectif
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure(self, param, value):
    if param == "nom":
      self.nom = value
    elif param == "commentaire":
      self.commentaire = value
    elif param == "etudiants":
      self.etudiants = value
      self.effectif = len(value)
    elif param == "effectif":
      self.effectif = value
    else:
      raise ValueError(f"parametre {param} invalide")











#GESTIONAIRE DE DONNÉE
#CLASSE PRINCIPALE
class DataManager():
  """classe de donnée dynamique"""
  def __init__(self):
    self.all = {}

  def existe(self, item_nom):
    return item_nom in self.all

  def append(self, item):
    self.all[item.nom] = item

  def configure(self, item_nom, param, value):
    self.all[item_nom].configure(param, value)

  def configure_week(self, item_nom, param, value, semaine):
    self.all[item_nom].configure_week(param, value, semaine)

  def rename(self, nom, nouv_nom):
    self.all[nouv_nom] = self.all[nom]
    self.all[nouv_nom].configure("nom", nouv_nom)
    self.all.pop(nom)

  def to_json(self):
    ret = [{}, {}, {}, {}]
    for item_nom, item in self.all.items():
      if isinstance(item, UIProf):
        ret[0][item_nom] = {}