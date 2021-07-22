"""
Computes structure eigen-tensors.
"""
from utils import *

setupForSubset()
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count

tpDir = "/scratch/data/seis/tp/"
sfile = tpDir+"tpsts" # seismic image, for computing structure tensors
efile = "./tpet" # eigen-tensors
esfile = "./tpets" # eigen-tensors scaled by semblance
s1file = "./tps1" # semblance w,uv
s2file = "./tps2" # semblance vw,u
s3file = "./tps3" # semblance uvw,

lsf1 = LocalSemblanceFilter(2,2)
lsf2 = LocalSemblanceFilter(2,8)
lsf3 = LocalSemblanceFilter(16,0)

def main(args):
  makeTensors()
  semblence()
  scaleTensors(0.001) # modify eigenvalues with semblences
#  display()

def makeTensors():
  sigma = 8.0
  s = readImage(sfile,n1,n2,n3)
  lof = LocalOrientFilter(sigma)
  e = lof.applyForTensors(s)
  writeTensors(efile,e)

def semblence():
  semblance1()
  semblance2()
  semblance3()
  #display2(sfile,s1file)
  #display2(sfile,s2file)
  #display2(sfile,s3file)

def semblance1():
  e = readTensors(efile)
  s = readImage(sfile,n1,n2,n3)
  s1 = lsf1.semblance(LocalSemblanceFilter.Direction3.W,e,s)
  writeImage(s1file,s1)

def semblance2():
  e = readTensors(efile)
  s = readImage(sfile,n1,n2,n3)
  s2 = lsf2.semblance(LocalSemblanceFilter.Direction3.VW,e,s)
  writeImage(s2file,s2)

def semblance3():
  e = readTensors(efile)
  s = readImage(sfile,n1,n2,n3)
  s3 = lsf3.semblance(LocalSemblanceFilter.Direction3.UVW,e,s)
  writeImage(s3file,s3)

def scaleTensors(eps):
  e = readTensors(efile)
  s1 = readImage(s1file,n1,n2,n3); print "s1 min =",min(s1)," max =",max(s1)
  s2 = readImage(s2file,n1,n2,n3); print "s2 min =",min(s2)," max =",max(s2)
  s3 = readImage(s3file,n1,n2,n3); print "s3 min =",min(s3)," max =",max(s3)
  pow(s1,4.0,s1)
  pow(s2,8.0,s2)
  pow(s3,4.0,s3)
  s1 = clip(eps,1.0,s1)
  s2 = clip(eps,1.0,s2)
  s3 = clip(eps,1.0,s3)
  e.setEigenvalues(s3,s2,s1)
  writeTensors(esfile,e)

def display():
  s = readImage(sfile,n1,n2,n3)
  et = readTensors(esfile)
  world = World()
  ipg = addImageToWorld(world,s)
  ipg.setClips(-5.5,5.5)
  addTensorsInImage(ipg.getImagePanel(Axis.X),et,20)
  addTensorsInImage(ipg.getImagePanel(Axis.Y),et,20)
  addTensorsInImage(ipg.getImagePanel(Axis.Z),et,20)
  frame = makeFrame(world)
  frame.setSize(1460,980)
  frame.orbitView.setAzimuth(-65.0)
  background = Color(254,254,254)
  frame.viewCanvas.setBackground(background)

def display2(sfile,smfile):
  s = readImage(sfile,n1,n2,n3)
  sm = readImage(smfile,n1,n2,n3)
  print "semblance: min =",min(sm)," max =",max(sm)
  world = World()
  ipg = addImage2ToWorld(world,s,sm)
  ipg.setClips2(0,1)
  makeFrame(world)

#############################################################################
run(main)
