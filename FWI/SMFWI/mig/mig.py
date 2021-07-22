from utility import *

freq = 12.0
bp = BandPassFilter(0.022,0.25,0.02,0.01)

#############################################################################
cfile = wDir+"/./COORD/coords_ns1.txt"
#############################################################################
def main(args):
    ns = Coords.countShots(cfile)
    sc = Coords.getSources(cfile, ns)
    ng = Coords.countReceivers(cfile, ns)
    gc = Coords.getReceivers(cfile, ns, ng)
##
    v = readImage(vinit,nz,nx)
    d = add(sub(v,v),1.0)
##
    sou = FwiUtil.genRicker(nt, 150, freq, dt)
##
    image = Modeling.mig(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir)
    writeImage(wDir+"./MIG/image.dat",image)
    bp.apply(image,image)
    image = ArraySegment.cutM(image,20,nz,0,nx)
    writeImage(wDir+"./MIG/imageLowCut.dat",image)
    return

#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
