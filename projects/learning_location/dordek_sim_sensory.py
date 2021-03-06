# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2018, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""TODO"""

import random

import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import NMF as PCA

from nupic.algorithms.spatial_pooler import SpatialPooler


#def computeCorrelation(history):
#  correlation = np.zeros((625, 625))
#  for active in history:
#    for element in active:
#      for coactive in active:
#        correlation[element][coactive] += 1
#  return correlation


def getNewLocation(x, y, width, viewDistance, wrap):
  options = []
  if x > viewDistance or wrap:
    options.append(((x - 1) % width, y))
  if x < width - viewDistance - 1 or wrap:
    options.append(((x + 1) % width, y))
  if y > viewDistance or wrap:
    options.append((x, (y - 1) % width))
  if y < width - viewDistance - 1 or wrap:
    options.append((x, (y + 1) % width))
  return options[int(random.random() * len(options))]


def getActive(world, worldWidth, x, y, radius):
  #active = set(world[x-2:x+2,y-2:y+2].flatten())
  active = set()
  for i in xrange(x - radius, x + radius + 1):
    for j in xrange(y - radius, y + radius + 1):
      active.add(world[i % worldWidth, j % worldWidth])
  return active


def main():
  x = 10
  y = 10
  steps = 10000
  ww = 50
  wn = ww ** 2
  rr = 3
  rw = rr * 2 + 1
  nCols = 25
  history = []
  world = np.array([i for i in xrange(wn)])
  world.resize((ww, ww))
  binaryWorld = np.zeros((wn,), dtype=np.uint32)
  binaryWorld[:wn/2] = 1
  np.random.shuffle(binaryWorld)
  sp = SpatialPooler(
      inputDimensions=(rw ** 2,),
      columnDimensions=(nCols,),
      potentialRadius=25,
      numActiveColumnsPerInhArea=5,
      synPermActiveInc=0.1,
      synPermInactiveDec=0.02,
      boostStrength=10.0,
  )
  output = np.zeros((nCols,), dtype=np.uint32)
  for _ in xrange(steps):
    active = getActive(world, ww, x, y, rr)
    assert len(active) == (rw) ** 2, "{}, {}: {}".format(x, y, active)
    active = np.array(list(active))
    activeInput = binaryWorld[active]
    sp.compute(activeInput, True, output)
    x, y = getNewLocation(x, y, ww, rr, False)

  firingFields = {}
  for i in xrange(nCols):
    firingFields[i] = np.zeros((ww-rw, ww-rw), dtype=np.uint32)
  for i in xrange(0, ww-rw+1):
    for j in xrange(0, ww-rw+1):
      active = getActive(world, ww, i, j, rr)
      active = np.array(list(active))
      activeInput = binaryWorld[active]
      sp.compute(activeInput, True, output)
      for column in list(output.nonzero()):
        firingFields[column[0]][i:i+rr, j:j+rr] += 1

  for col, ff in firingFields.iteritems():
    plt.imshow(ff, cmap="hot", interpolation="nearest")
    plt.show()

  #for i in xrange(25):
  #  permanence = np.zeros((625,))
  #  sp.getPermanence(i, permanence)
  #  plt.imshow(permanence.reshape((25, 25)), cmap="hot", interpolation="nearest")
  #  plt.show()


if __name__ == "__main__":
  main()
