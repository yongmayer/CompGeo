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
from edu.mines.jtk.ogl.Gl import *
from edu.mines.jtk.sgl import *
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
    goModels()
    return

def goModels():
    vfile = "vtrue"
    v = readDat("./VEL/"+vfile,nz,nx) # read big endian files (.dat)
    # for little endian files (.bin), use readLittleDat() instead
    plot2Model(v,sz,sx,None,vfile) # plot an image and save it as a .png file
    # display2(v) # only plot an image
    ####
    for j in range(10): # plot updated models
        vfile = "v_iter"+"%d" %(j+1)
        v = readDat("./VEL/"+vfile,nz,nx)
        plot2Model(v1,sz,sx,None,vfile)
#############################################################################
def readDat(name,n1,n2):
  """ 
  Reads an image from a file with specified name.
  name: base name of image file; e.g., "tpsz"
  """
  fileName = dir+name+".dat"
  image = zerofloat(n1,n2)
  ais = ArrayInputStream(fileName)
  ais.readFloats(image)
  ais.close()
  return image

def readLittleDat(name,n1,n2):
  """ 
  Reads an image from a file with specified name.
  name: base name of image file; e.g., "tpsz"
  """
  fileName = dir+name+".bin"
  image = zerofloat(n1,n2)
  ais = ArrayInputStream(fileName,ByteOrder.LITTLE_ENDIAN)
  ais.readFloats(image)
  ais.close()
  return image

def readImage(name,n1,n2):
  """ 
  Reads an image from a file with specified name.
  name: base name of image file; e.g., "tpsz"
  """
  fileName = name+".dat"
  image = zerofloat(n1,n2)
  ais = ArrayInputStream(fileName)
  ais.readFloats(image)
  ais.close()
  return image

def display2(s,g=None,cmin=0,cmax=0):
  sp = SimplePlot(SimplePlot.Origin.UPPER_LEFT)
  sp.addColorBar()
  sp.getPlotPanel().setColorBarWidthMinimum(80)
  pv = sp.addPixels(s)
  pv.setInterpolation(PixelsView.Interpolation.NEAREST)
  pv.setColorModel(ColorMap.JET)

def plot2Model(s,s1,s2,title=None,png=None):
  n1 = len(s[0])
  n2 = len(s)
  panel = panel2Data()
  panel.setHInterval(1.0)
  panel.setVInterval(0.5)
  panel.setHLabel("Distance (km)")
  panel.setVLabel("Depth (km)")
  panel.addColorBar("Velocity (km/s)")
  panel.setColorBarWidthMinimum(150)
  pv = panel.addPixels(s1,s2,s)
  pv.setInterpolation(PixelsView.Interpolation.NEAREST)
  pv.setColorModel(ColorMap.JET)
  pv.setClips(1.5,5.5)
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
