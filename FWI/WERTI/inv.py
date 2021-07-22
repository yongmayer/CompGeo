from utility import *

##############################################################################
# global files
cfile = wDir+"/./COORD/coords_ns24.txt" # source-receiver coordinates
ns = Coords.countShots(cfile)
sc = Coords.getSources(cfile, ns)
ng = Coords.countReceivers(cfile, ns)
gc = Coords.getReceivers(cfile, ns, ng)

v0 = readImage(vtrue,nz,nx) # true model
v1 = readImage(vinit,nz,nx) # initial model
d = add(sub(v1,v1),1.0) # constant density

sou = FwiUtil.genRicker(nt, 150, freq, dt) # source wavelet
##############################################################################
# temp files
vinput= wDir+"/./v.dat"

gfile = wDir+"/./g.dat"
gbpfile = wDir+"/./gbp.dat"
gbp0file = wDir+"/./gbp0.dat"

goldfile = wDir+"/./gold.dat"
grfile = wDir+"gr.dat"
groldfile = wDir+"/./grold.dat"
#############################################################################
def main(args):
  writeImage(wDir+"/./v0.dat",v0)
  writeImage(wDir+"/./v1.dat",v1)
  csg(v0) # simulate recorded data, only for first-time use
#  rtm()
#  werti(1) # WERTI or FWI
  return

def csg(v):
  Modeling.csg(sou, dt, freq, ng, sc, gc, pml, dz, dx, v, d, wDir)

def rtm():
  v0 = readImage(wDir+"/./v0.dat",nz,nx)
  image = Modeling.mig(sou,dt,freq,ng,sc,gc,pml,dz,dx,v0,d,wDir)
  ifile = wDir+"/./MIG/image_"+"vtrue" 
  ifile = ifile+".dat"
  writeImage(ifile,image)
  v1 = readImage(wDir+"/./v1.dat",nz,nx)
  image = Modeling.mig(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,d,wDir)
  ifile = wDir+"/./MIG/image_"+"vinit" 
  ifile = ifile+".dat"
  writeImage(ifile,image)

def werti(flag): # flag = 1 for WERTI, = 0 for FWI
  nOut = 5
  nIn = 2 # alternating 
  for i in range(nOut):
    for j in range(nIn):
      iter = i*nIn+(j+1)
      stage = 0 # begin with conventional FWI
      if j>0:
        stage = flag
      ## forward modeling synthetic data and gradient calculation
      v1 = readImage(wDir+"/./v1.dat",nz,nx)        
      if stage==0:
        Inv.partOne(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,d,wDir,iter,stage)
      if stage==1:
        v2 = readImage(wDir+"/./v2.dat",nz,nx)
        dv = readImage(wDir+"/./dvFWI.dat",nz,nx)
        v1 = sub(v1,dv)
        Inv.partOne(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,v2,d,wDir,iter,stage)
      ## 
      g = readImage(gfile,nz,nx)
      writeImage(gbpfile, g)
      writeImage(grfile, g)
      writeImage(gbp0file, g)
      if iter>1:
        gold = readImage(goldfile,nz,nx)
        writeImage(groldfile, gold)
      # line-search and update vel
      if stage==0:
        Inv.partTwo(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,d,wDir,iter,stage)
        ##
        dvfile = wDir+"/./VEL/dv_iter"+"%d" %(iter)
        dvfile = dvfile+".dat"
        dv = readImage(dvfile,nz,nx)
        writeImage(wDir+"/./dvFWI.dat",dv)
        writeImage(wDir+"/./v2.dat",add(v1,dv))
        writeImage(wDir+"/./v1.dat",add(v1,dv))
#        if iter%4==0:
#          v1 = readImage(wDir+"/./v1.dat",nz,nx)
#          image = Modeling.mig(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,d,wDir)
#          ifile = wDir+"/./MIG/image"+"%d" %(iter)
#          ifile = ifile+".dat"
#          writeImage(ifile,image)
      if stage==1:
        Inv.partTwo(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,v2,d,wDir,iter,stage)
        ##
        dvfile = wDir+"/./VEL/dv_iter"+"%d" %(iter)
        dvfile = dvfile+".dat"
        dv = readImage(dvfile,nz,nx)
        writeImage(wDir+"/./v1.dat",add(v1,dv))
        writeImage(wDir+"/./v2.dat",add(v2,dv))
#        if iter%4==0:
#          v1 = readImage(wDir+"/./v1.dat",nz,nx)
#          image = Modeling.mig(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,d,wDir)
#          ifile = wDir+"/./MIG/image"+"%d" %(iter)
#          ifile = ifile+".dat"
#          writeImage(ifile,image)
      if iter==nOut*nIn:
        v1 = readImage(wDir+"/./v1.dat",nz,nx)
        image = Modeling.mig(sou,dt,freq,ng,sc,gc,pml,dz,dx,v1,d,wDir)
        ifile = wDir+"/./MIG/image"+"%d" %(iter)
        ifile = ifile+".dat"
        writeImage(ifile,image)
#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
