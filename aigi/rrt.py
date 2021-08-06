"""
Interpolates scattered data, such as data from well logs.
"""
from utils import *

setupForSubset()
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count

tpDir = "/Users/yma/work/data/tp/"
sfile = tpDir+"tpsts" # seismic image (e.g., gradient) to be operated by RR^T
efile = "./tpet" # eigen-tensors (structure tensors)
esfile = "./tpets" # eigen-tensors scaled by semblances
gfile = "./tpg" # known sample locations, null for unknown samples
tfile = "./times" # times to nearest known samples
mfile = "./marks" # marks to nearest known samples
agfile = "./tpag" # result of applying R^T
pfile = "./tpp" # nearest-neighbor interpolation
qfile = "./tpq" # image-guided blendend interpolation (result of applying R)

rrtDir = "./"

pnull = -99.9

def main(args):
  goTimeMarkers() # computing time and markers 
  goAdjointIGI()  # apply R^T
  goIGI()         # apply R
  display(sfile)
  display(pfile)
  display(qfile)

def goTimeMarkers():
  e = getEigenTensors()
  g = goSamples()
  writeImage(gfile,g)
  igi = IGI3(e,rrtDir)
  igi.saveTimeMarker(pnull,g)

def goSamples():
  # Generate known sample locations, marked with 0.0 values, and
  # others(unknown) are marked with pnull.
  # In this test, I simply use a set of uniform sample locations, and
  # you can use more advanced methods to generate sample locations. 
  s = readImage(sfile,n1,n2,n3)
  g = zerofloat(n1,n2,n3)
  g = add(g,pnull)
  k1,k2,k3 = 20,9,2
  j1,j2,j3 = 24,20,20
  f1,f2,f3 = 10,10,5
  for i3 in range(k3):
    for i2 in range(k2):
      for i1 in range(k1):
        g[f3+i3*j3][f2+i2*j2][f1+i1*j1] = 0.0
  return g  

def goAdjointIGI():
  e = getEigenTensors()
  aigi = AdjointIGI3(e,rrtDir)
  g = readImage(gfile,n1,n2,n3)
  x = readImage(sfile,n1,n2,n3)
  ax = zerofloat(n1,n2,n3)
  aigi.gridBlended(x,ax)
  ag = aigi.adjointNearest(pnull,g,ax)
  writeImage(agfile,ag)

def goIGI():
  e = getEigenTensors()
  igi = IGI3(e,rrtDir)
  g = readImage(gfile,n1,n2,n3)
  ag = readImage(agfile,n1,n2,n3)
  p = igi.gridNearest(pnull,g,ag)
  writeImage(pfile,p)
  q = zerofloat(n1,n2,n3)  
  igi.gridBlended(p,q)
  writeImage(qfile,q)  

def getEigenTensors():
  e = readTensors(esfile)
  return e

def display(sfile):
  s = readImage(sfile,n1,n2,n3)
  world = World()
  ipg = addImageToWorld(world,s)
  makeFrame(world)

def display2(sfile,tmfile):
  s = readImage(sfile,n1,n2,n3)
  tm = readImage(tmfile,n1,n2,n3)
  world = World()
  ipg = addImage2ToWorld(world,s,tm)
  makeFrame(world)

#############################################################################
run(main)
