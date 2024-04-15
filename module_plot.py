import matplotlib.pyplot as plt

def setup():
  """creer la zone de dessin et un cadre autour"""
  fig, ax = plt.subplots()
  ax.axis('off')
  ax.plot([0, 2.2, 2.2, 0, 0], [0.2, 0.2, -1.25, -1.25, 0.2], 'k-')
  return ax


def dessin_rectangle(mn, titre, sous_titre="", *, ax, couleur="blue", cercle = False):
  """ dessin un rectangle avec du texte dedans
  :param: mn : tuple de coordonnées entières par rapport au coin supérieur gauche du rectangle"""
  x = mn[0] * 0.45
  y = mn[1] * -0.25
  ax.add_patch(plt.Rectangle((x, y), 0.4, 0.2, color=couleur))
  ax.text(x + 0.005, y + 0.1, titre[:11], fontsize=10)
  ax.text(x + 0.005, y + 0.02, sous_titre[:14], fontsize=8)
  if cercle:
    ax.add_patch(plt.Circle((x + 0.39, y + 0.19), 0.02, color='gray'))

