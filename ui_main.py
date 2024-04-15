from customtkinter import *
import tkinter as tk
from ui_interface import *
from ui_widget import *


class Empty():
  def __init__(self, nom):
    return


#FENETRE
#CLASSE PRINCIPAL
class Window(CTk):
  def __init__(self):
    super().__init__()
    self.geometry("1100x800")
    self.minsize(width=800, height=100)
    self.title("Horarium - nouveau projet (unsaved)")

    #constante
    self.DICT_ENT_C = {"text":TextEntry, "textbox":TextBoxEntry,
            "calendar":CalendarEntry, "textlist":TextListEntry,
            "integer":IntegerEntry, "prof":ProfEntry,
            "derpeda":DerPedEntry}
    self.DICT_CAT_C = {"PROFESSEUR":UIProf, "GROUPE DE SALLE":UISalle,
            "GROUPE D'ETUDIANT":UIGroupe, "MATIERE":UIMatiere}

    #contenu
    self.creer_frame()
    self.menu_bar = MenuBar(self, sauvegarder=self.nothing)
    self.menu_bar.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    # frame gauche
    self.item_boxes = []
    for titre in self.DICT_CAT_C:
      box = ItemBox(self.frame_g, titre, can_add=self.can_add, on_add=self.on_add, on_clic=self.on_clic)
      self.item_boxes.append(box)
      box.pack(fill=X)

    # frame milieu
    self.gene_param_box = ParamBox(self.frame_c, "PARAMETRES GENERAUX", dict_entree_classe=self.DICT_ENT_C, functions=[self.can_save, self.on_gene_param_saved, self.input_item, self.exit_item])
    self.gene_param_box.pack(fill = BOTH, expand=YES)

    # frame droite
    self.week_param_box = WeekParamBox(self.frame_d, "PARAMETRES DE SEMAINE", dict_entree_classe=self.DICT_ENT_C, semaine=38, functions=[self.nothing, self.on_week_param_saved, self.input_item, self.exit_item])
    self.week_param_box.pack(fill = BOTH, expand=YES)

    #variable
    self.data_manager = DataManager()

    self.selected_item = None
    self.entree = None
    self.mode = "NORMAL"


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

  def can_save(self, entree, new_value):
    if entree.titre == "nom":
      return new_value != "" and not self.data_manager.existe(new_value)

  def on_gene_param_saved(self, entree, new_value):
    if entree.titre == "nom":
      self.data_manager.rename(entree.value, new_value)
      self.selected_item.rename(new_value)
    else:
      self.data_manager.configure(self.selected_item.titre, entree.titre, new_value)

  def on_week_param_saved(self, entree, new_value):
    self.data_manager.configure_week(self.selected_item.titre, entree.titre, new_value, self.week_param_box.semaine)

  def input_item(self, entree):
    self.mode = "INPUT"
    self.entree = entree

  def exit_item(self, entree):
    if entree == self.entree:
      self.mode = "NORMAL"
      self.entree = None

  def nothing(self):
    print("nothing happened")


if __name__ == "__main__":
  app = Window()
  app.mainloop()