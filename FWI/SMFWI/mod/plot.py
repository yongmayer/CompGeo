"""
Sample script to plot shot gather
"""

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
from edu.mines.jtk.mosaic import *
from edu.mines.jtk.util import *
from edu.mines.jtk.util.ArrayMath import *

from util import *

True = 1
False = 0
nz = 391
nx = 1151
nt = 3501
sz = Sampling(nz,0.008,0.000)
sx = Sampling(nx,0.008,0.000)
st = Sampling(nt,0.0008,0.000)
gray = ColorMap.GRAY
jet = ColorMap.JET
prism = ColorMap.PRISM
#############################################################################
dir = "../../../marmousi/"
pngDir = "./"
#############################################################################
def main(args):
    goData()
    return

def goData():
    for j in range(1):
        dfile = "csg"+"%d" %(j+1)
        d = readDat("./CSG/"+dfile,nt,nx)
        d = div(d,max(abs(d)))
        plot2Data(d,st,sx,None,dfile)
#############################################################################
def readDat(name,n1,n2):
  """ 
  Reads an image from a file with specified name.
  name: base name of image file
  """
  fileName = dir+name+".dat"
  image = zerofloat(n1,n2)
  ais = ArrayInputStream(fileName)
  ais.readFloats(image)
  ais.close()
  return image

def plot2Data(s,s1,s2,title=None,png=None):
  n1 = len(s[0])
  n2 = len(s)
  panel = panel2Data()
  panel.setHInterval(2.0)
  panel.setVInterval(0.5)
  panel.setHLabel("Distance (km)")
  panel.setVLabel("Time (s)")
  panel.addColorBar("Amplitude")
  panel.setColorBarWidthMinimum(125)
  pv = panel.addPixels(s1,s2,s)
  pv.setInterpolation(PixelsView.Interpolation.LINEAR)
  pv.setColorModel(ColorMap.GRAY)
  pv.setClips(-0.1,0.1)
  frame2Data(panel,title,png)

def panel2Data():
  panel = PlotPanel(1,1,
    PlotPanel.Orientation.X1DOWN_X2RIGHT,
    PlotPanel.AxesPlacement.LEFT_TOP)
  return panel

def frame2Data(panel,title=None,png=None):
  frame = PlotFrame(panel)
  frame.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE)
  if title:
    panel.setTitle(title)
    frame.setFontSizeForSlide(1.0,1.0)
    frame.setSize(1240,940)
  else:
    frame.setFontSizeForPrint(8,240)
    frame.setSize(1000,600)
  frame.setVisible(True)
  if png and pngDir:
    frame.paintToPng(720,3.33,pngDir+"/"+png+".png")
  return frame

#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
