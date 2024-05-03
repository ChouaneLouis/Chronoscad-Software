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


from customtkinter import *
import threading

from json import dumps, loads
from customtkinter import filedialog

from ui_interface import *
from ui_widget import *
from module_recuit import *
from ui_sous_fen import *
from module_csv import *


class Empty():
  def __init__(self, nom):
    return


#FENETRE
#CLASSE PRINCIPAL
class Window(CTk):
  def __init__(self):
    super().__init__()
    self.geometry("1100x800")
    self.minsize(850, 600)

    #constante
    self.DICT_ENT_C = {"text":TextEntry, "textbox":TextBoxEntry,
            "calendar":CalendarEntry, "textlist":TextListEntry,
            "integer":IntegerEntry, "prof":ProfEntry,
            "derpeda":DerPedEntry}
    self.DICT_CAT_C = {"PROFESSEURS":UIProf, "GROUPES DE SALLES":UISalle,
            "GROUPES D'ETUDIANTS":UIGroupe, "MATIERES":UIMatiere}

    #contenu
    self.creer_frame()

    frame = CTkFrame(self, fg_color="transparent")
    frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew", columnspan=3)
    self.fichier_bar = MenuBar(frame, titre="Fichier", functions={"Nouveau":self.nouveau, "Enregistrer":self.sauvegarder, "Enregistrer Sous":self.sauvegarder_sous, "Ouvrir":self.charger})
    self.fichier_bar.pack(side=LEFT)
    self.option_bar = MenuBar(frame, titre="Option", functions={"Démarer la résolution":self.recuisson, "Importer une semaine":self.importer_edt})
    self.option_bar.pack(side=LEFT)
    self.aide_bar = MenuBar(frame, titre="Aide", functions={"Guide":self.nothing, "A propos":self.nothing})
    self.aide_bar.pack(side=LEFT)

    # frame gauche
    self.item_boxes = []
    for titre in self.DICT_CAT_C:
      box = ItemBox(self.frame_g, titre, can_add=self.can_add, on_add=self.on_add, on_clic=self.on_clic, on_del=self.on_del)
      self.item_boxes.append(box)
      box.pack(fill=X)

    # frame milieu
    self.gene_param_box = ParamBox(self.frame_c, "PARAMETRES GENERAUX", dict_entree_classe=self.DICT_ENT_C, functions=[self.can_save, self.on_gene_param_saved, self.input_item, self.exit_item])
    self.gene_param_box.pack(fill = BOTH, expand=YES)

    # frame droite
    self.week_param_box = WeekParamBox(self.frame_d, "PARAMETRES DE SEMAINE", dict_entree_classe=self.DICT_ENT_C, semaine=6, functions=[self.nothing, self.on_week_param_saved, self.input_item, self.exit_item])
    self.week_param_box.pack(fill = BOTH, expand=YES)

    #variable
    self.data_manager = DataManager()

    self.selected_item = None
    self.entree = None
    self.mode = "NORMAL"

    self.projet_nom = "nouveau projet"
    self.chemin = None
    self.sauvegarde = False
    self.titrer()


  def creer_frame(self):
    #divise l'app en 2 morceaux
    self.grid_rowconfigure(0, weight=1)
    self.grid_rowconfigure(1, weight=100)
    self.grid_columnconfigure(0, weight=3, uniform="colonne")
    self.grid_columnconfigure(1, weight=3, uniform="colonne")
    self.grid_columnconfigure(2, weight=3, uniform="colonne")

    self.frame_g = CTkScrollableFrame(self, corner_radius=0)
    self.frame_c = CTkScrollableFrame(self, corner_radius=0)
    self.frame_d = CTkScrollableFrame(self, corner_radius=0)

    self.frame_g.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="nsew")
    self.frame_c.grid(row=1, column=1, padx=0, pady=(0, 5), sticky="nsew")
    self.frame_d.grid(row=1, column=2, padx=(0, 5), pady=(0, 5), sticky="nsew")


  def can_add(self, item_nom):
    return item_nom != "" and not self.data_manager.existe(item_nom)

  def on_add(self, item_nom, categorie):
    NewItem = self.DICT_CAT_C[categorie]
    self.data_manager.append(NewItem(item_nom))

    if self.sauvegarde:
      self.sauvegarde = False
      self.titrer()

  def on_clic(self, item_ligne):
    if self.mode == "NORMAL":
      if item_ligne.selectable:
        if self.selected_item is not None:
          self.selected_item.unselect()

        self.gene_param_box.save()
        self.week_param_box.save()

        self.selected_item = item_ligne
        item_ligne.select()
        item = self.data_manager.all[item_ligne.titre]

        self.gene_param_box.set(item)
        self.week_param_box.set(item)
    else:
      if item_ligne.master_titre == self.entree.type:
        self.entree.set(self.data_manager.all[item_ligne.titre])
        self.entree.exit()

  def can_save(self, entree, new_value):
    if entree.titre == "nom":
      return new_value != "" and not self.data_manager.existe(new_value)

  def on_del(self, nom):
    self.data_manager.all.pop(nom)
    self.gene_param_box.reset()
    self.week_param_box.reset()
    self.selected_item = None

  def on_gene_param_saved(self, entree, new_value):
    if entree.titre == "nom":
      self.data_manager.rename(entree.value, new_value)
      self.selected_item.rename(new_value)
    else:
      self.data_manager.configure(self.selected_item.titre, entree.titre, new_value)

    if self.sauvegarde:
      self.sauvegarde = False
      self.titrer()

  def on_week_param_saved(self, entree, new_value):
    self.data_manager.configure_week(self.selected_item.titre, entree.titre, new_value, self.week_param_box.semaine)

    if self.sauvegarde:
      self.sauvegarde = False
      self.titrer()

  def input_item(self, entree):
    self.mode = "INPUT"
    self.entree = entree

  def exit_item(self, entree):
    if entree == self.entree:
      self.mode = "NORMAL"
      self.entree = None

  def sauvegarder_sous(self):
    chemin = filedialog.asksaveasfilename(filetypes=(("Json Files", "*.json"), ("All Files", "*.*")))
    if chemin == tuple() or chemin == "":
      return
    self.chemin = chemin
    if self.chemin[-5:] != ".json":
      self.chemin += ".json"
    self.projet_nom = self.chemin.split("/")[-1].split(".")[0]
    self.sauvegarder()

  def sauvegarder(self):
    if self.chemin is None:
      self.chemin = filedialog.asksaveasfilename(filetypes=(("Json Files", "*.json"), ("All Files", "*.*")))
      if self.chemin == tuple() or self.chemin == "":
        self.chemin = None
        return
      if self.chemin[-5:] != ".json":
        self.chemin += ".json"

      self.projet_nom = self.chemin.split("/")[-1].split("\\")[-1].split(".")[0]

    self.gene_param_box.save()
    self.week_param_box.save()

    json = dumps(self.data_manager.to_json(), indent = 1)
    with open(self.chemin, "w") as file:
      file.write(json)

    self.sauvegarde = True
    self.titrer()

  def charger(self):
    file = filedialog.askopenfilename(filetypes=(("Json Files", "*.json"), ("All Files", "*.*")))
    if file == tuple() or file == "":
      return
    if file[-5:] != ".json":
      file += ".json"

    title = file.split("/")[-1].split(".")[0]

    self.chemin = file
    self.projet_nom = title

    with open(file, "r") as file:
      data = file.read()
    values = loads(data)

    self.gene_param_box.reset()
    self.week_param_box.reset()
    self.selected_item = None
    self.entree = None
    self.mode = "NORMAL"

    self.data_manager.from_json(values)

    for i, item_boxe_i in enumerate(self.item_boxes):
      item_boxe_i.empty()
      item_boxe_i.add(values[i])

    self.sauvegarde = True
    self.titrer()

  def nouveau(self):
    self.chemin = None
    self.projet_nom = "nouveau projet"

    self.gene_param_box.reset()
    self.week_param_box.reset()
    self.selected_item = None
    self.entree = None
    self.mode = "NORMAL"

    self.data_manager.all = {}

    for item_boxe_i in self.item_boxes:
      item_boxe_i.empty()

    self.sauvegarde = False
    self.titrer()

  def titrer(self, ):
    if self.sauvegarde:
      self.title("Chronoscad - " + self.projet_nom)
    else:
      self.title("Chronoscad - " + self.projet_nom + " (unsaved)")

  def nothing(self):
    print("nothing happened")

  def recuisson(self):
    self.gene_param_box.save()
    self.week_param_box.save()

    self.recuisson = Recuisson(self.data_manager.all, self.week_param_box.semaine, [6] * 4 + [5])

    ui = ParamGeneration(self.demarer_recuisson, self.week_param_box.semaine, len(self.recuisson.elements))

  def demarer_recuisson(self, params):
    batch1 = params[0]
    iteration1 = params[1]
    coeff = params[2]
    batch2 = params[3]
    iteration2 = params[4]
    swp_max = params[5]

    self.recuisson.new_batch(batch1)

    t = threading.Thread(target=self.recuisson_thread, args=(iteration1 , coeff, batch2, iteration2, swp_max))
    t.start()

  def recuisson_thread(self, iteration1 , coeff, batch2, iteration2, swp_max):
    coeff2 = 1 / coeff

    last_cout = 0
    echec = 0
    for i in range(iteration1):
      self.recuisson.do_swaps(100)
      if self.recuisson.meilleur_cout < last_cout:
        self.recuisson.temperature = max(0.000000001, self.recuisson.temperature * coeff)
        echec = 0
      elif echec > 4: 
        self.recuisson.temperature = min(10, self.recuisson.temperature * coeff2)
      else:
        echec += 1
      last_cout = self.recuisson.meilleur_cout
      print(i, " : ", self.recuisson.meilleur_cout)

    self.recuisson.selection(batch2)

    last_cout = 0
    echec = 0
    self.recuisson.temperature = 0.000000001
    for i in range(iteration2):
      self.recuisson.do_swaps(100)
      if self.recuisson.meilleur_cout < last_cout:
        echec = 0
      elif echec > swp_max: 
        break
      else:
        echec += 1
      last_cout = self.recuisson.meilleur_cout
      print(i, " : ", self.recuisson.meilleur_cout)

    self.recuisson.get_best(1)[0].verif_final()

    ui = Retour(self.recuisson.get_best(1)[0], self.recuisson.groupe, self.exporter_edt)


  def exporter_edt(self, edt):
    file = filedialog.asksaveasfilename(filetypes=(("Csv Files", "*.csv"), ("All Files", "*.*")))
    if file == tuple() or file == "":
      return
    if file[-4:] != ".csv":
      file += ".csv"

    edt_to_csv(file, edt)

  def importer_edt(self):
    file = filedialog.askopenfilename(filetypes=(("Csv Files", "*.csv"), ("All Files", "*.*")))
    if file == tuple() or file == "":
      return
    if file[-4:] != ".csv":
      file += ".csv"
    
    recuisson = Recuisson(self.data_manager.all, self.week_param_box.semaine, [6] * 4 + [5])
    ui = Retour(csv_to_edt(file, self.data_manager.all), recuisson.groupe, self.exporter_edt)


if __name__ == "__main__":
  set_appearance_mode("light")
  app = Window()
  app.mainloop()
