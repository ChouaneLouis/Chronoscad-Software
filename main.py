from module_data import Data

def recuit_simule(data : Data, params, N, coeff):
  '''
  Descend la température au fur et à mesure des changement s dans l'emplois du temps.
  '''
  nb_edt, nb_parent, nb_swap, temperature = params

  indices_meilleur = [0 for i in range(nb_parent)]
  meilleur_cout = 10000000000
  pire_meilleur_cout = 10000000000
  ancien_meilleur_cout = 10000000000
  
  #creation edt
  edts = []
  couts = []
  
  for i in range(nb_edt):
    edt = data.creation_edt()
    edts.append(edt)
    couts.append(edt.cout_edt_total())

  for n in range(N):
    #recuisson
    for i, edt_i in enumerate(edts):
      for s in range(nb_swap):
        edt_i.saut(temperature)
      couts[i] = edt_i.cout
      
    #selection
    for i, cout_i in enumerate(couts):
      if cout_i < pire_meilleur_cout:
        place = False
        prec = 0
        for j, indice_j in enumerate(indices_meilleur):
          if not place and cout_i < couts[indice_j]:
            place = True
            prec = indice_j
            indices_meilleur[j] = i
          elif place:
            indices_meilleur[j], prec = prec, indices_meilleur[j]

        pire_meilleur_cout = indices_meilleur[-1]
    meilleur_cout = indices_meilleur[0]

    #clonage
    for i, edt_i in enumerate(edts):
      j = i % nb_parent
      edt_i.copy(edts[indices_meilleur[j]])
    
    #condition d'arrets
    if meilleur_cout == ancien_meilleur_cout:
      break
      
    ancien_meilleur_cout = meilleur_cout
    temperature *= coeff
