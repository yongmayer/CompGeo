from utility import *

    """
    Acoustic finite-difference modeling
    """

cfile = wDir+"/./COORD/coords_ns1.txt"
freq = 12.0
#############################################################################
def main(args):
    # set up geometry
    ns, sc, ng, gc = setGeom(cfile)
    ## prepare velocity and density
    v = readImage(vtrue,nz,nx)
    d = add(sub(v,v),1.0)
    ##
    sou = FwiUtil.genRicker(nt, 150, freq, dt)
    ##
    Modeling.csg(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir)
    return

def setGeom(coord_file):
    """
    setup geometry

    Args:
        coord_file (name): file name contains the acqusition geometry

    Returns:
        nsrc: number of shots
        sloc: source locations
        nrec: number of receivers
        rloc: receiver locations
    """
    nsrc = Coords.countShots(cfile) 
    sloc = Coords.getSources(cfile, nsrc)
    nrec = Coords.countReceivers(cfile, nsrc)
    rloc = Coords.getReceivers(cfile, nsrc, nrec)
    return nsrc, sloc, nrec, rloc
#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
