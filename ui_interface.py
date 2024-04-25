from module_edt import Prof, Salle, Matiere, Groupe

#OBJET DE L'EDT AFFICHABLE
#PROF
class UIProf(Prof):
  def __init__(self, nom : str):
    super().__init__(nom)
    self.params = {"nom":"text", "commentaire":"textbox", "contrainte_annuel":"calendar"}
    self.week_params = {"contrainte_de_semaine":"calendar"}
    self.default = {"contrainte_de_semaine":"contrainte_annuel"}

    self.commentaire = ""
    self.contrainte_annuel = [[0 for i in range(6)] for j in range(5)] ### A CHANGER ###
    self.contrainte_de_semaine = {}

  def cget(self, param):
    if param == "nom":
      return self.nom
    elif param == "commentaire":
      return self.commentaire
    elif param == "contrainte_annuel":
      return self.contrainte_annuel
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure(self, param, value):
    if param == "nom":
      self.nom = value
    elif param == "commentaire":
      self.commentaire = value
    elif param == "contrainte_annuel":
      self.contrainte_annuel = value
    else:
      raise ValueError(f"parametre {param} invalide")

  def cget_week(self, param, semaine):
    if param == "contrainte_de_semaine":
      ret = self.contrainte_de_semaine.get(semaine)
      if ret is None:
        return self.cget(self.default[param])
      else:
        return ret
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure_week(self, param, value, semaine):
    if param == "contrainte_de_semaine":
      if value == self.cget(self.default[param]):
        if self.contrainte_de_semaine.get(semaine) is not None:
          del self.contrainte_de_semaine[semaine]
      else:
        self.contrainte_de_semaine[semaine] = value
    else:
      raise ValueError(f"parametre {param} invalide")

  def save(self):
    return {"commentaire":self.commentaire, "contrainte_annuel":self.contrainte_annuel}

  def load(self, value, all):
    self.commentaire = value["commentaire"]
    self.contrainte_annuel = value["contrainte_annuel"]

#SALLE
class UISalle(Salle):
  def __init__(self, nom : str):
    super().__init__(nom)
    self.nom = nom
    self.commentaire = ""

    self.params = {"nom":"text", "commentaire":"textbox", "noms_des_salles":"textlist", "capacite":"integer"}
    self.week_params = {}

    self.noms_des_salles = []

  def cget(self, param):
    if param == "nom":
      return self.nom
    elif param == "commentaire":
      return self.commentaire
    elif param == "noms_des_salles":
      return self.noms_des_salles
    elif param == "capacite":
      return self.capacite
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure(self, param, value):
    if param == "nom":
      self.nom = value
    elif param == "commentaire":
      self.commentaire = value
    elif param == "noms_des_salles":
      self.noms_des_salles = value
      self.nombre = len(value)
    elif param == "capacite":
      self.capacite = value
    else:
      raise ValueError(f"parametre {param} invalide")

  def save(self):
    return {"commentaire":self.commentaire, "noms_des_salles":self.noms_des_salles, "capacite":self.capacite}

  def load(self, value, all):
    self.commentaire = value["commentaire"]
    self.noms_des_salles = value["noms_des_salles"]
    self.nombre = len(self.noms_des_salles)
    self.capacite = value["capacite"]

#MATIERE
class UIMatiere(Matiere):
  def __init__(self, nom : str):
    super().__init__(nom)
    self.params = {"nom":"text", "commentaire":"textbox"}
    self.week_params = {"deroulement_peda":"derpeda"}
    self.default = {"deroulement_peda":"deff"}

    self.commentaire = ""
    self.deff = []
    self.deroulement_peda = {}

  def cget(self, param):
    if param == "nom":
      return self.nom
    elif param == "deff":
      return self.deff
    elif param == "commentaire":
      return self.commentaire
    else:
      raise ValueError(f"parametre {param} invalide")

  def configure(self, param, value):
    if param == "nom":
      self.nom = value
    elif param == "commentaire":
      self.commentaire = value
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
    else:
      raise ValueError(f"parametre {param} invalide")

  def save(self):
    deroulement = {}
    for s,l in self.deroulement_peda.items():
      liste = []
      for t in l:
        salle = t[3]
        if salle is not None:
          salle = salle.nom
        liste.append(({p.nom : [g.nom for g in gs] for p, gs in t[0].items()}, t[1], t[2], salle))
      deroulement[s] = liste
    return {"commentaire":self.commentaire, "deroulement_peda":deroulement}

  def load(self, value, all):
    self.deroulement_peda  = {}
    for s,l in value["deroulement_peda"].items():
      liste = []
      for t in l:
        if len(t) == 4:
          salle = t[3]
          if salle is not None:
            salle = all[salle]
          liste.append(({all[p] : [all[g] for g in gs] for p, gs in t[0].items()}, t[1], t[2], salle))
        else: #retro compatibilité
          salle = t[2]
          if salle is not None:
            salle = all[salle]
          liste.append(({all[p] : [all[g] for g in gs] for p, gs in t[0].items()}, t[1], 1, salle))
      self.deroulement_peda[int(s)] = liste
    self.commentaire = value["commentaire"]

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

  def save(self):
    return {"commentaire":self.commentaire, "etudiants":self.etudiants, "effectif":self.effectif}

  def load(self, value, all):
    self.commentaire = value["commentaire"]
    self.etudiants = value["etudiants"]
    self.effectif = value["effectif"]











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
        ret[0][item_nom] = item.save()
      elif isinstance(item, UISalle):
        ret[1][item_nom] = item.save()
      elif isinstance(item, UIGroupe):
        ret[2][item_nom] = item.save()
      elif isinstance(item, UIMatiere):
        ret[3][item_nom] = item.save()

    return ret

  def from_json(self, values):
    self.all = {}
    for item_nom, value in values[0].items():
      self.all[item_nom] = UIProf(item_nom)
      self.all[item_nom].load(value, self.all)
    for item_nom, value in values[1].items():
      self.all[item_nom] = UISalle(item_nom)
      self.all[item_nom].load(value, self.all)
    for item_nom, value in values[2].items():
      self.all[item_nom] = UIGroupe(item_nom)
      self.all[item_nom].load(value, self.all)
    for item_nom, value in values[3].items():
      self.all[item_nom] = UIMatiere(item_nom)
      self.all[item_nom].load(value, self.all)
