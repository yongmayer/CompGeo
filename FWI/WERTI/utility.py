import sys
from org.python.util import PythonObjectInputStream
from math import *
from java.awt import *
from java.lang import *
from java.io import *
from java.nio import *
from java.util import *
from javax.swing import *

from edu.mines.jtk.awt import *
from edu.mines.jtk.dsp import *
from edu.mines.jtk.io import *
from edu.mines.jtk.util import *
from edu.mines.jtk.util.ArrayMath import *

from werti import *
from util import *
#from filters import *

freq = 15.0
nz = 251
nx = 501
dx = 0.008
dz = 0.008
nt = 2001
dt = 0.001
pml = 200

#############################################################################
wDir = "./../../anomaly/"

vtrue = wDir+"/./VEL/vtrue.dat"
vinit = wDir+"/./VEL/vinit.dat"
#############################################################################

def readImage(name,n1,n2):
  """ 
  Reads an image from a file with specified name.
  name: base name of image file; e.g., "tpsz"
  """
  fileName = name
  image = zerofloat(n1,n2)
  ais = ArrayInputStream(fileName)
  ais.readFloats(image)
  ais.close()
  return image

def readLittleImage(name,n1,n2):
  fileName = name
  image = zerofloat(n1,n2)
  ais = ArrayInputStream(fileName,ByteOrder.LITTLE_ENDIAN)
  ais.readFloats(image)
  ais.close()
  return image

def readIntImage(name,n1,n2):
  """ 
  Reads an image from a file with specified name.
  name: base name of image file; e.g., "tpsz"
  """
  fileName = name
  image = zeroint(n1,n2)
  ais = ArrayInputStream(fileName)
  ais.readInts(image)
  ais.close()
  return image

def writeImage(name,image):
  """ 
  Writes an image to a file with specified name.
  name: base name of image file; e.g., "tpgp"
  image: the image
  """
  fileName = name
  aos = ArrayOutputStream(fileName)
  aos.writeFloats(image)
  aos.close()
  return image

def readTensors(name):
  """
  Reads tensors from file with specified basename; e.g., "tpet".
  """
  fileName = name
  tensors = zerofloat(3,nz,nx)
  ais = ArrayInputStream(fileName)
  ais.readFloats(tensors)
  ais.close()
  return tensors

def plot(t,cm):
  ipg = ImagePanelGroup(t)
  ipg.setColorModel(cm)
  world = World()
  world.addChild(ipg)
  frame = TestFrame(world)
  frame.setVisible(True)

def display2(s,g=None,cmin=0,cmax=0):
  sp = SimplePlot(SimplePlot.Origin.UPPER_LEFT)
  sp.addColorBar()
  sp.getPlotPanel().setColorBarWidthMinimum(80)
  pv = sp.addPixels(s)
  pv.setInterpolation(PixelsView.Interpolation.NEAREST)
  pv.setColorModel(ColorMap.JET)
  if g!=None:
    pv = sp.addPixels(g)
    pv.setInterpolation(PixelsView.Interpolation.NEAREST)
    pv.setColorModel(ColorMap.getJet(1.0))
    if cmin!=cmax:
      pv.setClips(cmin,cmax)
