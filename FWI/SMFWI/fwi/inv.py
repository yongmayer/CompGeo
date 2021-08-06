from utility import *

"""
2D acoustic full-waveform inversion
"""

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
    # set up geometry
    ns, sc, ng, gc = setGeom(cfile)
    # prepare model and density
    v = readImage(vinit,nz,nx)
    v = ArraySegment.cutM(v,20,nz,0,nx)
    vt= readImage(vtrue,nz,nx)
    vt= ArraySegment.cutM(vt,0,20,0,nx)
    v = add(v,vt)
    writeImage(vinput,v)
    s = div(1.0,v)
    d = add(sub(v,v),1.0)
    # prepapre source wavelet
    sou = FwiUtil.genRicker(nt, 150, freq, dt)
    # inversion loop
    for i in range(niter):
        iter = i+1 # iteration number
        ## forward modeling synthetic data and gradient calculation
        if iter>1:
            v = readImage(vinput,nz,nx)
        Inv.partOne(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir, iter)

        ## save gradient for CG
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
