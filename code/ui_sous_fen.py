from customtkinter import *

class cours(CTkFrame):
  def __init__(self, master, **kwargs):
    super().__init__(master, fg_color="#3B8ED0", **kwargs)

class ButtonGroupe(CTkButton):
  def __init__(self, master, groupe, groupes_actifs, reset, **kwargs):
    super().__init__(master, text=groupe.nom, command=self.clic, **kwargs)

    self.reset = reset

    self.groupe = groupe
    self.groupes_actifs = groupes_actifs

  def clic(self):
    if self.groupe in self.groupes_actifs:
      self.groupes_actifs.remove(self.groupe)
      self.configure(fg_color="#3B8ED0")
    else:
      self.groupes_actifs.append(self.groupe)
      self.configure(fg_color="#3980B0")
    self.reset()


class Retour(CTkToplevel):
  def __init__(self, edt, groupes, export):
    super().__init__()
    self.geometry("850x550")
    self.minsize(850, 550)

    self.edt = edt
    self.export = export

    self.creer_frame()
    self.canvas = CTkFrame(self.frame_d, fg_color="transparent")
    self.canvas.pack(fill=BOTH, expand=True)
    self.frame_grid = []
    self.COLORS = ["red", "green", "blue", "gray", "pink", "yellow", "peru", "limegreen", "turquoise", "crimson"]
    self.NB_COLORS = len(self.COLORS)
    for j in range(5):
      jour = []
      self.canvas.grid_columnconfigure(j, weight=1, uniform="jour")
      for c in range(6):
        jour.append(CTkFrame(self.canvas, corner_radius=0, fg_color="transparent"))
        jour[-1].grid(row=c, column=j, sticky="nsew")
      self.frame_grid.append(jour)

    for c in range(6):
      self.canvas.grid_rowconfigure(c, weight=1, uniform="creneau")
    self.canvas.grid_rowconfigure(7, weight=0)

    CTkButton(self.canvas, text="EXPORTER L'EDT", command=self.exporter).grid(row=6, column=4, pady=(5,0))

    self.groupes_actifs = []
    for groupe in groupes:
      ButtonGroupe(self.frame_g, groupe, self.groupes_actifs, self.reset).pack(fill=X, padx=5, pady=2)

    self.set()

  def creer_frame(self):
    #divise l'app en 2 morceaux
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=0, minsize=260)
    self.grid_columnconfigure(1, weight=1)

    self.frame_g = CTkScrollableFrame(self, corner_radius=0)
    self.frame_d = CTkFrame(self, corner_radius=0)

    self.frame_g.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="nsew")
    self.frame_d.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

  def exporter(self):
    self.export(self.edt)

  def set(self):
    for j, jour in enumerate(self.edt._creneau):
      for c, creaneau in enumerate(jour):
        for cours in creaneau:
          if cours.groupe in self.groupes_actifs:
            color = self.COLORS[ord(cours.matiere.nom[0]) % self.NB_COLORS]
            frame = CTkFrame(self.frame_grid[j][c], fg_color=color, corner_radius=0, border_width=2)
            CTkLabel(frame, text=cours.matiere.nom).pack(expand=True, padx=2, pady=2)
            CTkLabel(frame, text=cours.groupe.nom).pack(expand=True, padx=2, pady=2)
            CTkLabel(frame, text=cours.prof.nom).pack(expand=True, padx=2, pady=2)
            frame.pack(side=LEFT, fill=BOTH, expand=True)

  def reset(self):
    for jour in self.frame_grid:
      for creneau in jour:
        for label in creneau.winfo_children():
          label.destroy()

    self.set()

class Entier(CTkEntry):
  def __init__(self, master, value, param, **kwargs):
    super().__init__(master, fg_color='transparent', **kwargs)

    self.insert(0, str(value))

    #variable
    self.value = value
    self.param = param

    #logique
    self.bind("<Return>", self.save)
    self.bind("<FocusOut>", self.save)

  def save(self, event=None):
    try:
      new_value = 0

      if self.param == "int":
        new_value = int(self.get())
      elif self.param == "float":
        new_value = float(self.get())

      self.value = new_value
    except:
      self.delete(0, 'end')
      self.insert(0, str(self.value))

class ParamGeneration(CTkToplevel):
  def __init__(self, ret, semaine, nb_elements):
    super().__init__()
    self.geometry("400x250")
    self.minsize(400, 250)

    self.ret = ret
    entre_1 = {"nb edt":"int", "iteration":"int", "coeff":"float"}
    value_1 = {"nb edt":100, "iteration":1000, "coeff":0.99}
    entre_2 = {"nb edt":"int", "iteration":"int", "nb echec max":"int"}
    value_2 = {"nb edt":10, "iteration":5000, "nb echec max":200}

    self.creer_frame()
    self.entrees = []
    titre = "SEMAINE : " + str(semaine) + ", " + str(nb_elements) + " COURS"
    CTkLabel(self.frame_t, text=titre).pack(fill=X)

    CTkLabel(self.frame_g, text="BATCH 1").pack(fill=X)

    frame1 = CTkFrame(self.frame_g, fg_color="transparent")
    frame1.pack(side=LEFT)
    frame2 = CTkFrame(self.frame_g, fg_color="transparent")
    frame2.pack(side=RIGHT, expand=True, fill=X)
    for nom, param in entre_1.items():
      CTkLabel(frame1, text=nom.replace("_", " ").upper() + " :", anchor="w").pack(padx=3, pady=3, fill=X)
      e = Entier(frame2, value_1[nom], param)
      e.pack(padx=3, pady=3, expand=True, fill=X)
      self.entrees.append(e)

    CTkLabel(self.frame_d, text="BATCH 2").pack(fill=X)

    frame1 = CTkFrame(self.frame_d, fg_color="transparent")
    frame1.pack(side=LEFT)
    frame2 = CTkFrame(self.frame_d, fg_color="transparent")
    frame2.pack(side=RIGHT, expand=True, fill=X)
    for nom, param in entre_2.items():
      CTkLabel(frame1, text=nom.replace("_", " ").upper() + " :", anchor="w").pack(padx=3, pady=3, fill=X)
      e = Entier(frame2, value_2[nom], param)
      e.pack(padx=3, pady=3, expand=True, fill=X)
      self.entrees.append(e)

    CTkButton(self.frame_b, command=self.execution, text="DEMARER").pack()

  def creer_frame(self):
    #divise l'app en 2 morceaux
    self.grid_rowconfigure(0, weight=1)
    self.grid_rowconfigure(1, weight=100)
    self.grid_rowconfigure(2, weight=1)
    self.grid_columnconfigure(0, weight=1, uniform="col")
    self.grid_columnconfigure(1, weight=1, uniform="col")

    self.frame_t = CTkFrame(self, fg_color="transparent", corner_radius=0)
    self.frame_g = CTkFrame(self, corner_radius=0)
    self.frame_d = CTkFrame(self, corner_radius=0)
    self.frame_b = CTkFrame(self, fg_color="transparent", corner_radius=0)

    self.frame_t.grid(row=0, column=0, columnspan=2, sticky="nsew")
    self.frame_g.grid(row=1, column=0, padx=(5, 0), pady=5, sticky="nsew")
    self.frame_d.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
    self.frame_b.grid(row=2, column=0, columnspan=2, sticky="nsew")

  def execution(self):
    params = []

    for entree in self.entrees:
      entree.save()
      params.append(entree.value)

    self.ret(params)
    self.destroy()