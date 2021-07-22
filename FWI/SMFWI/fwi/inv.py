from utility import *

freq = 12.0
cfile = wDir+"/./COORD/coords_ns11.txt"

##############################################################################
niter = 10
vinput= wDir+"/./v.dat"

gfile = wDir+"/./g.dat"
gbpfile = wDir+"/./gbp.dat"
gbp0file = wDir+"/./gbp0.dat"

goldfile = wDir+"/./gold.dat"
grfile = wDir+"gr.dat"
groldfile = wDir+"/./grold.dat"
#############################################################################
def main(args):
    ns = Coords.countShots(cfile)
    sc = Coords.getSources(cfile, ns)
    ng = Coords.countReceivers(cfile, ns)
    gc = Coords.getReceivers(cfile, ns, ng)
##
    v = readImage(vinit,nz,nx)
    v = ArraySegment.cutM(v,20,nz,0,nx)
    vt= readImage(vtrue,nz,nx)
    vt= ArraySegment.cutM(vt,0,20,0,nx)
    v = add(v,vt)
    writeImage(vinput,v)
    s = div(1.0,v)
    d = add(sub(v,v),1.0)
##
    sou = FwiUtil.genRicker(nt, 150, freq, dt)
##  
    for i in range(niter):
        iter = i+1
        ## forward modeling synthetic data and gradient calculation
        if iter>1:
            v = readImage(vinput,nz,nx)
        Inv.partOne(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir, iter)
        ## 
        g = readImage(gfile,nz,nx)
        g = ArraySegment.cutM(g,20,nz,0,nx)
        writeImage(gbpfile, g)
        writeImage(grfile, g)
        writeImage(gbp0file, g)
        if iter>1:
            gold = readImage(goldfile,nz,nx)
            gold = ArraySegment.cutM(gold,20,nz,0,nx)
            writeImage(groldfile, gold)
        # line-search and update vel
        Inv.partTwo(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir, iter)
    return

#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
