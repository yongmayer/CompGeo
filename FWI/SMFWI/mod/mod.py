from utility import *

cfile = wDir+"/./COORD/coords_ns1.txt"
freq = 12.0
#############################################################################
def main(args):
    ns = Coords.countShots(cfile)
    sc = Coords.getSources(cfile, ns)
    ng = Coords.countReceivers(cfile, ns)
    gc = Coords.getReceivers(cfile, ns, ng)
##
    v = readImage(vtrue,nz,nx)
    d = add(sub(v,v),1.0)
##
    sou = FwiUtil.genRicker(nt, 150, freq, dt)
##
    Modeling.csg(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir)
    return

#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
