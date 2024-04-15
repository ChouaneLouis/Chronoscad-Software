from time import time
TIME = [0]

def init(text):
  global TIME
  print(f'== {text} ==')
  TIME[0] = time()

def phase(text):
  global TIME
  print(round(time() - TIME[0], 4), ' sec écoulées')
  print(f'== {text} ==')
  TIME[0] = time()