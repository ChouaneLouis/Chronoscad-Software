from customtkinter import *
from copy import deepcopy

#ENTRÉES DE LA PARAM BOX
#TEXT
class TextEntry(CTkFrame):
  def __init__(self, master, titre, *, value, functions, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)

    #contenu
    self.titre_label = CTkLabel(self, text=titre)
    self.entree = CTkEntry(self, fg_color="transparent")

    self.entree.insert(0, value)

    self.titre_label.pack(fill=X, padx=3)
    self.entree.pack(fill=X, padx=3)

    #fonction
    self.on_saved = functions[1]
    self.can_save = functions[0]

    #variable
    self.titre = titre
    self.value = value

    #logique
    self.entree.bind("<Return>", self.save)
    self.entree.bind("<FocusOut>", self.save)

  def save(self, event=None):
    new_value = self.entree.get()
    if self.can_save(self, new_value):
      self.on_saved(self, new_value)
      self.value = new_value
      self.master.focus_set()
    else:
      self.entree.delete(0, 'end')
      self.entree.insert(0, self.value)


#TEXT BOX
class TextBoxEntry(CTkFrame):
  def __init__(self, master, titre, *, value, functions, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)

    #contenu
    self.titre_label = CTkLabel(self, text=titre)
    self.entree = CTkTextbox(self, height=103, border_width=2, fg_color="transparent")

    self.entree.insert(0., value)

    self.titre_label.pack(fill=X, padx=3)
    self.entree.pack(fill=X, padx=3)

    #fonction
    self.on_saved = functions[1]

    #variable
    self.titre = titre
    self.value = value

  def save(self, event=None):
    new_value = self.entree.get(0., "end-1c")
    self.on_saved(self, new_value)


#CALENDAR
class CalendarButton(CTkButton):
    def __init__(self, master, *, value, i, j, grid, **kwargs):
      super().__init__(master, command=self.clicked, text="", corner_radius=0, width=30, height=18, **kwargs)

      #variable
      self.colors = [("#090", "#080"), ("#f00", "#e00")]
      self.nb_state = len(self.colors)

      self.state = int(value * (self.nb_state - 1))
      self.grid = grid
      self.i = i
      self.j = j

      #init
      self.setcolor()

    def setcolor(self):
      color_tuple = self.colors[self.state]

      self.configure(fg_color=color_tuple[0], hover_color=color_tuple[1])

    def setvalue(self):
      self.grid[self.i][self.j] = self.state / (self.nb_state - 1)

    def clicked(self):
      self.state = (self.state + 1) % self.nb_state

      self.setcolor()
      self.setvalue()

class CalendarGrid(CTkFrame):
  def __init__(self, master, *, value, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)

    #contenu
    self.bouton_grille = []

    for j in range(len(value[0])):
      bouton_ligne = []
      ligne_frame = CTkFrame(self, fg_color='transparent', corner_radius=0)

      for i, colonne in enumerate(value):
        bouton = CalendarButton(ligne_frame, value=colonne[j], i=i, j=j, grid=value)

        bouton_ligne.append(bouton)
        bouton.pack(side=LEFT)

      self.bouton_grille.append(bouton_ligne)
      ligne_frame.pack()

class CalendarEntry(CTkFrame):
  def __init__(self, master, titre, *, value, functions, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)
    value_c = deepcopy(value)

    #contenu
    self.titre_label = CTkLabel(self, text=titre)
    self.entree = CalendarGrid(self, value=value_c)

    self.titre_label.pack(fill=X, padx=3)
    self.entree.pack(fill=X, padx=3)

    #fonction
    self.on_saved = functions[1]

    #variable
    self.titre = titre
    self.value = value_c

  def save(self):
    new_value = self.value
    self.on_saved(self, new_value)


#TEXTLIST
class TextListEntry(CTkFrame):
  def __init__(self, master, titre, *, value, functions, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)
    
    #contenu
    self.titre_label = CTkLabel(self, text=titre)
    self.frame = CTkFrame(self, border_width=2, fg_color="transparent")
    self.frame_t = CTkFrame(self.frame, fg_color="transparent")
    self.frame_g = CTkFrame(self.frame_t, fg_color="transparent")
    self.frame_d = CTkFrame(self.frame_t, fg_color="transparent")
    self.entree = CTkEntry(self.frame, border_width=0, fg_color="transparent")

    for texte in value:
      self.ajouter_ligne(texte)

    self.titre_label.pack(fill=X, padx=3)
    self.frame.pack(fill=X, padx=3)
    if value:
      self.ajouter_frames()
    self.entree.pack(side=BOTTOM, fill=X, padx=3, pady=3)

    #fonction
    self.on_saved = functions[1]

    #variable
    self.titre = titre
    self.value = value

    #logique
    self.entree.bind("<Return>", self.ajouter_item)

  def ajouter_frames(self):
    self.frame_t.pack(fill=X, padx=3, pady=(3,0))
    self.frame_g.pack(side=LEFT, fill=X, expand=True, padx=3)
    self.frame_d.pack(side=RIGHT, padx=3)

  def ajouter_ligne(self, texte):
    label = CTkLabel(self.frame_g, text=texte, anchor="w")
    button = CTkLabel(self.frame_d, text="x", anchor="e")

    label.pack(fill=X, expand=True, padx=3)
    button.pack(padx=3)

    button.bind("<Button-1>", lambda _:self.detruire(texte, label, button))

  def detruire(self, nom, label, button):
    self.value.remove(nom)
    label.destroy()
    button.destroy()

  def vider_entree(self):
    self.entree.delete(0, 'end')

  def ajouter_item(self, event=None):
    texte = self.entree.get()
    self.vider_entree()

    if texte == "" or texte in self.value:
      return
    if not self.value:
      self.ajouter_frames()

    self.ajouter_ligne(texte)
    self.value.append(texte)

  def save(self):
    new_value = self.value
    self.on_saved(self, new_value)


#INTEGER
class IntegerEntry(CTkFrame):
  def __init__(self, master, titre, *, value, functions, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)

    #contenu
    self.titre_label = CTkLabel(self, text=titre)
    self.entree = CTkEntry(self, fg_color="transparent")

    self.entree.insert(0, str(value))

    self.titre_label.pack(fill=X, padx=3)
    self.entree.pack(fill=X, padx=3)

    #fonction
    self.on_saved = functions[1]

    #variable
    self.titre = titre
    self.value = value

    #logique
    self.entree.bind("<Return>", self.save)
    self.entree.bind("<FocusOut>", self.save)

  def save(self, event=None):
    try:
      new_value = int(self.entree.get())
      self.on_saved(self, new_value)
      self.value = new_value
      self.master.focus_set()
    except:
      self.entree.delete(0, 'end')
      self.entree.insert(0, str(self.value))

#CLASS
class ClassButton(CTkButton):
  def __init__(self, master, value, inp, ext, tpe, callback, **kwargs):
    if value is None:
      titre = " "
    else:
      titre = value.nom
    super().__init__(master,  text=titre, command=self.input, text_color_disabled="gray25", fg_color="gray85", hover_color="gray83", text_color="black", **kwargs)

    self.inp = inp
    self.ext = ext
    self.callback = callback

    self.value = value
    self.master = master
    self.type = tpe
    self.enabled = True

    self.bind("<FocusOut>", self.exit)
    self.bind("<Escape>", lambda _:master.focus_set())
    self.bind("<Delete>", self.reset)
    self.bind("<BackSpace>", self.reset)

  def input(self):
    if self.enabled:
      self.inp(self)
      self.focus_set()

      self.configure(fg_color="gray80")
      self.configure(state="disabled")

  def exit(self, event=None):
    self.ext(self)

    if self.callback is not None:
      self.callback(self.value)

    self.configure(fg_color="gray85")
    self.configure(state="normal")

  def set(self, item):
    self.value = item
    self.configure(text=item.nom)

    self.master.focus_set()

  def reset(self, event=None):
    self.value = None
    self.configure(text=" ")

    self.master.focus_set()

  def disable(self):
    self.enabled = False

  def enable(self):
    self.enabled = True

class ProfButton(ClassButton):
  def __init__(self, master, value, inp, ext, callback=None, **kwargs):
    super().__init__(master, value, inp, ext, "PROFESSEUR", callback, **kwargs)

class GroupeButton(ClassButton):
  def __init__(self, master, value, inp, ext, callback=None, **kwargs):
    super().__init__(master, value, inp, ext, "GROUPE D'ETUDIANT", callback, **kwargs)

#PROF
class ProfEntry(CTkFrame):
  def __init__(self, master, titre, *, value, functions, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)

    #contenu
    self.titre_label = CTkLabel(self, text=titre)
    self.entree = ProfButton(self, value,  functions[2], functions[3], border_color="#979DA2", border_width=2)

    self.titre_label.pack(fill=X, padx=3)
    self.entree.pack(fill=X, padx=3)

    #fonction
    self.on_saved = functions[1]

    #variable
    self.titre = titre

  def save(self):
    new_value = self.entree.value
    self.on_saved(self, new_value)

#DEROULÉ PÉDAGOGIQUE
#Prof:[Groupes]
class ProfPed(CTkFrame):
  def __init__(self, master, prof, groupes, inp, ext, create, delete):
    super().__init__(master, fg_color='transparent', corner_radius=0)

    CTkLabel(self, text="PROFESSEUR :").pack(anchor="w", padx=3)
    ProfButton(self, prof, inp, ext, callback=self.set_prof, anchor="w").pack(fill=X, expand=True, padx=3)

    frame = CTkFrame(self, fg_color='transparent', corner_radius=0)
    frame.pack(fill=X)

    self.frame_g = CTkFrame(frame, fg_color='transparent', corner_radius=0)
    self.frame_d = CTkFrame(frame, fg_color='transparent', corner_radius=0)

    CTkLabel(frame, text="GROUPES :").pack(anchor="w", padx=12)
    self.gpe_button = GroupeButton(frame, None, inp, ext, callback=self.set_grpe, anchor="w")
    self.gpe_button.pack(fill=X, expand=True, padx=12, side=BOTTOM)


    self.prof = prof
    self.groupes = groupes


    self.create = create
    self.delete = delete

    for groupe in groupes:
      self.ajouter_ligne(groupe)

    if groupes:
      self.ajouter_frames()

    if prof is None:
      self.gpe_button.disable()

  def ajouter_frames(self):
    self.frame_g.pack(side=LEFT, fill=X, expand=True, padx=12)
    self.frame_d.pack(side=RIGHT, padx=3)

  def ajouter_ligne(self, groupe):
    label = CTkLabel(self.frame_g, text=groupe.nom, anchor="w")
    button = CTkLabel(self.frame_d, text="x", anchor="e")

    label.pack(fill=X, expand=True, padx=7)
    button.pack(padx=3)

    button.bind("<Button-1>", lambda _:self.detruire(groupe, label, button))

  def detruire(self, nom, label, button):
    self.groupes.remove(nom)
    label.destroy()
    button.destroy()

  def set_prof(self, prof):
    if self.prof is None:
      if prof is not None:
        self.gpe_button.enable()
        self.create()
    else:
      if prof is None:
        self.delete(self)
    self.prof = prof

  def set_grpe(self, groupe):
    if groupe is not None and groupe not in self.groupes:
      if not self.groupes:
        self.ajouter_frames()
      self.groupes.append(groupe)
      self.ajouter_ligne(groupe)
    self.gpe_button.reset()

#{Prof:[Groupes]}
class CreneauPed(CTkFrame):
  def __init__(self, master, values, inp, ext, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, border_width=2, **kwargs)

    self.prof_peds = []

    self.master = master
    self.values = values
    

    self.inp = inp
    self.ext = ext

    for prof, groupes in values.items():
      self.creer_prof_ped(prof, groupes)

    self.create()

  def creer_prof_ped(self, prof, groupes):
    self.prof_peds.append(ProfPed(self, prof, groupes, self.inp, self.ext, self.create, self.delete))

    self.prof_peds[-1].pack(fill=X, pady=(0,3))

  def delete(self, prof_ped):
    prof_ped.destroy()
    self.prof_peds.remove(prof_ped)

    if not self.prof_peds:
      self.create()

  def create(self):
    self.creer_prof_ped(None, [])

  def value(self):
    value = {}
    for prof_ped in self.prof_peds:
      if prof_ped.prof is not None:
        value[prof_ped.prof] = prof_ped.groupes
    return value


#[{Prof:[Groupes]}]
class DerPedEntry(CTkFrame):
  def __init__(self, master, titre, *, value, functions, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)
    #variable
    self.titre = titre
    self.value = value

    self.inp = functions[2]
    self.ext = functions[3]

    self.creneaux = []

    #contenu
    self.titre_label = CTkLabel(self, text=titre)
    self.frame = CTkFrame(self, border_width=2, fg_color="transparent")

    self.bouton_plus = CTkButton(self.frame, text='+', command=self.ajouter_creneau, width=30, height=30)

    self.titre_label.pack(fill=X, padx=3)
    self.frame.pack(fill=X, padx=3)

    for i in value:
      self.ajouter_creneau(i)
    self.bouton_plus.pack(side=BOTTOM, pady=3)

    #fonction
    self.on_saved = functions[1]

  def save(self, event=None):
    self.value = []
    for i, creneau in enumerate(self.creneaux):
      value = creneau.value()
      if value != {}:
        self.value.append(value)

    new_value = self.value
    self.on_saved(self, new_value)

  def ajouter_creneau(self, value = None):
    if value is None:
      value = {}

    creneau = CreneauPed(self.frame, values=value, inp=self.inp, ext=self.ext)
    creneau.pack(padx=2, pady=(3,0), fill=X)

    self.creneaux.append(creneau)













#REGROUPEMENT DES ENTRÉE GENERALE
class ParamBox(CTkFrame):
  def __init__(self, master, titre, *, dict_entree_classe, functions, **kwargs):
    super().__init__(master, corner_radius=0, **kwargs)

    #frame
    self.header = CTkFrame(self)
    self.body = CTkFrame(self, fg_color='transparent')

    self.header.pack(side=TOP, fill=X)
    self.body.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=10)

    #contenu
    self.titre = CTkLabel(self.header, text=titre)

    self.titre.pack(side=LEFT, padx=3)

    #fonction
    self.functions = functions

    #variable
    self.dict_entree_classe = dict_entree_classe

    self.wgt_entrees = []

  def reset(self):
    #suprimme le contenu
    for i in self.wgt_entrees:
      i.destroy()

    self.wgt_entrees = []

  def save(self):
    #sauvegarde les modif de chaque entree
    for wgt_entree in self.wgt_entrees:
      wgt_entree.save()

  def set(self, item):
    #recreer le contenu
    self.reset()
    for nom_param, type_param in item.params.items():
      NewWgtEntree = self.dict_entree_classe[type_param]
      wdg_entree = NewWgtEntree(self.body, nom_param, value=item.cget(nom_param),functions=self.functions)

      self.wgt_entrees.append(wdg_entree)
      wdg_entree.pack(fill=X)


#REGROUPEMENT DES ENTRÉE POUR UNE SEMAINE
class WeekParamBox(CTkFrame):
  def __init__(self, master, titre, *, dict_entree_classe, functions, semaine, **kwargs):
    super().__init__(master, corner_radius=0, **kwargs)

    #frame
    self.header = CTkFrame(self)
    self.body = CTkFrame(self, fg_color='transparent')

    self.header.pack(side=TOP, fill=X)
    self.body.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=10)

    #contenu
    self.titre = CTkLabel(self.header, text=titre)
    self.frame = CTkFrame(self.header, fg_color="transparent")
    self.semaine_label = CTkLabel(self.frame, text="Semaine " + str(semaine), fg_color="transparent")
    self.next_button = CTkButton(self.frame, text=">", width=30, height=30, command=self.next)
    self.prev_button = CTkButton(self.frame, text="<", width=30, height=30, command=self.prev)

    self.titre.pack(padx=3)
    self.frame.pack(side=BOTTOM, padx=3, fill=X)
    self.prev_button.pack(side=LEFT)
    self.semaine_label.pack(side=LEFT, expand=True)
    self.next_button.pack(side=RIGHT)

    #fonction
    self.functions = functions

    #variable
    self.dict_entree_classe = dict_entree_classe

    self.wgt_entrees = []
    self.semaine = semaine
    self.current_item = None

  def next(self):
    if self.current_item is not None:
      self.save()
    self.semaine = (self.semaine) % 52 + 1
    self.semaine_label.configure(text="Semaine " + str(self.semaine))
    if self.current_item is not None:
      self.set(self.current_item)

  def prev(self):
    if self.current_item is not None:
      self.save()
    self.semaine = (self.semaine - 2) % 52 + 1
    self.semaine_label.configure(text="Semaine " + str(self.semaine))
    if self.current_item is not None:
      self.set(self.current_item)

  def reset(self):
    #suprimme le contenu
    for i in self.wgt_entrees:
      i.destroy()

    self.wgt_entrees = []

  def save(self):
    #sauvegarde les modif de chaque entree
    for wgt_entree in self.wgt_entrees:
      wgt_entree.save()

  def set(self, item):
    self.current_item = item
    #recreer le contenu
    self.reset()
    for nom_param, type_param in item.week_params.items():
      NewWgtEntree = self.dict_entree_classe[type_param]
      wdg_entree = NewWgtEntree(self.body, nom_param, value=item.cget_week(nom_param, self.semaine),functions=self.functions)

      self.wgt_entrees.append(wdg_entree)
      wdg_entree.pack(fill=X)














#BATTERIE D'ITEM DE L'EDT
#LIGNE D'AFFICHAGE D'UN ITEM
class ItemLine(CTkFrame):
  def __init__(self, master, titre, *, master_titre, on_clic, selectable=True, **kwargs):
    super().__init__(master, fg_color='transparent', corner_radius=0, **kwargs)

    #contenu
    self.texte = CTkLabel(self, text=titre, anchor="w")

    self.texte.pack(fill=X, padx=7)

    #fonction
    self.on_clic = on_clic

    #variable
    self.titre = titre
    self.selected = False
    self.selectable = selectable
    self.master_titre = master_titre

    #logique
    self.texte.bind("<Enter>", self.enter)
    self.texte.bind("<Leave>", self.leave)
    self.texte.bind("<Button-1>", self.clicked)

    self.texte.bind("<BackSpace>", self.delete)
    self.texte.bind("<Delete>", self.delete)

  def enter(self, event):
    if not self.selected:
      self.configure(fg_color="gray83")

  def leave(self, event):
    if not self.selected:
      self.configure(fg_color='transparent')

  def clicked(self, event):
    self.on_clic(self)

  def select(self):
    self.configure(fg_color="gray80")
    self.texte.focus_set()

    self.selected = True

  def unselect(self):
    self.configure(fg_color='transparent')
    self.selected = False

  def rename(self, nom):
    self.titre = nom
    self.texte.configure(text=nom)

  def delete(sel, event):
    print("supppr")


#ENSEMBLE DE LIGNE
class ItemBox(CTkFrame):
  def __init__(self, master, titre, *, can_add, on_add, on_clic, **kwargs):
    super().__init__(master, corner_radius=0, **kwargs)

    #frame
    self.header = CTkFrame(self)
    self.body = CTkFrame(self, fg_color='transparent')

    self.header.pack(side=TOP, fill=X)
    self.body.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=10)

    #contenu
    self.bouton_ouv = CTkButton(self.header, text='v', command=self.toggle, width=30, height=30)
    self.bouton_plus = CTkButton(self.header, text='+', command=self.ajouter_entree, width=30, height=30)
    self.titre_label = CTkLabel(self.header, text=titre)
    italic_font = CTkFont(family="Helvetica", size=12, slant="italic")
    self.texte_vide = CTkLabel(self.body, text='vide', font=italic_font, text_color="gray40")
    self.entree = CTkEntry(self.body, fg_color='transparent', border_width=0)

    self.bouton_ouv.pack(side=LEFT, padx=3, pady=3)
    self.bouton_plus.pack(side=RIGHT, padx=3, pady=3)
    self.titre_label.pack(side=LEFT, padx=3)
    self.texte_vide.pack()

    #fonction
    self.can_add = can_add
    self.on_add = on_add
    self.on_clic = on_clic

    #variable
    self.titre = titre
    self.is_empty = True
    self.is_close = False
    self.is_entree = False
    self.items = []

    #logique
    self.entree.bind("<Return>", self.ajouter_item)
    self.entree.bind("<FocusOut>", self.ajouter_item)
    self.entree.bind("<Escape>", self.retirer_entree)

  def toggle(self):
    if self.body.winfo_ismapped():
      #au cas ou l'utilisateur n'a pas appuyer sur entrée avant de fermer la fenetre
      self.ajouter_item()

      #femer la fenetre
      self.body.pack_forget()
      self.bouton_ouv.configure(text='>')
      self.bouton_plus.configure(state='disable')
      self.is_close = True
    else:
      #ouvrir la fenetre
      self.body.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=10)
      self.bouton_ouv.configure(text='v')
      self.bouton_plus.configure(state='normal')
      self.is_close = False

  def ajouter_entree(self):
      if self.is_close:
          return
      #creer et focus l'entree
      self.entree.pack(side=BOTTOM, fill=X)
      self.entree.focus_set()
      self.is_entree = True

  def vider_entree(self):
    self.entree.delete(0, 'end')

  def retirer_entree(self, event=None):
    #supprime l'entree
    self.entree.pack_forget()
    self.vider_entree()
    self.is_entree = False

  def ajouter_item(self, event=None):
    #verifie que l'entrée est bien afficher
    if not self.is_entree:
      return

    #recupere le resultat
    item_nom = self.entree.get()

    if self.can_add(item_nom):
      #creer la ligne du nouvelle item
      item = ItemLine(self.body, item_nom, master_titre=self.titre, on_clic=self.on_clic)
      self.items.append(item)
      item.pack(fill=X)

      self.on_add(item_nom, self.titre)

      #retire le message 'vide'
      if self.is_empty:
        self.texte_vide.pack_forget()
        self.is_empty = False

    #supprime/vide l'entree
    if event is None or event.keysym != "Return":
      self.retirer_entree()
    else:
      self.vider_entree()
















class MenuBar(CTkFrame):
  def __init__(self, master, *, sauvegarder, **kwargs):
    super().__init__(master, corner_radius=0, fg_color="transparent", **kwargs)

    #contenu
    self.fichier_menu = CTkOptionMenu(self, fg_color="gray93", button_color="gray93", button_hover_color="gray93", text_color="black",
          values=["Sauvegarder"], corner_radius=0, command=self.clicked)
    self.fichier_menu.set("Fichier")

    self.fichier_menu.pack(side=LEFT, padx=0, pady=0)

    #fonction
    self.sauvegarder=sauvegarder

  def clicked(self, value):
    self.fichier_menu.set("Fichier")

    if value == "Sauvegarder":
      self.sauvegarder()


