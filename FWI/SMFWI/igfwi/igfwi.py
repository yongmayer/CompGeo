from utility import *

freq = 12.0
cfile = wDir+"/./COORD/coords_ns11.txt"

##############################################################################
niter = 10
vinput= wDir+"/./v.dat"
rrtDir= wDir+"/./RRT/"
ifile = rrtDir+"/./guidance.dat"
sfile = rrtDir+"/./samplesT.dat"
dfile = rrtDir+"/./tensors.dat"
tfile = rrtDir+"/./times.dat"
mfile = rrtDir+"/./marks.dat"
qfile = rrtDir+"/./interpolant.dat"
pfile = rrtDir+"/./extrapolant.dat"

gfile = wDir+"/./g.dat"
gbpfile = wDir+"/./gbp.dat"
gbp0file = wDir+"/./gbp0.dat"
goldfile = wDir+"/./gold.dat"
grfile = wDir+"gr.dat"
gr0file = wDir+"gr0.dat"
groldfile = wDir+"/./grold.dat"

s1file = rrtDir+"/./s1.dat"
s2file = rrtDir+"/./s2.dat"

lsf = LocalSmoothingFilter(0.001,1000)
bp = BandPassFilter(0.01,0.45,0.001,0.01)
bp2 = BandPassFilter(0.01,0.45,0.001,0.01)

ht = HilbertTrans(nz,15,1.0)
lsf1 = LocalSemblanceFilter(16,1)
lsf2 = LocalSemblanceFilter(1,16)

#############################################################################
def main(args):
    ## set geometry
    ns = Coords.countShots(cfile)
    sc = Coords.getSources(cfile, ns)
    ng = Coords.countReceivers(cfile, ns)
    gc = Coords.getReceivers(cfile, ns, ng)
    ## initial velocity and constant density
    v = readImage(vinit,nz,nx)
    v = ArraySegment.cutM(v,20,nz,0,nx)
    vt= readImage(vtrue,nz,nx)
    vt= ArraySegment.cutM(vt,0,20,0,nx)
    v = add(v,vt)
    s = div(1.0,v)
    d = add(sub(v,v),1.0)
    ## Ricker wavelet
    sou = FwiUtil.genRicker(nt, 150, freq, dt)
    ##  
    for i in range(niter):
        iter = i+1
        if iter>1:
            v = readImage(vinput,nz,nx)
	## forward modeling synthetic data and gradient calculation
        Inv.partOne(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir, iter)
	## image-guided gradient/FWI
        ## pick sample locations
        nsample,et = pickByTensor()
        ttm(et,nsample)
        ##
        g = readImage(gfile,nz,nx)
        g2 = mul(g,1.0)
        bp.apply(g,g)
        bp2.apply(g2,g2)
        g = ArraySegment.cutM(g,20,nz,0,nx)
        g2 = ArraySegment.cutM(g2,20,nz,0,nx)
        writeImage(gbp0file, g2)
        t = readImage(tfile,nz,nx)
        t2 = mul(t,t)
        gr = aigi(et,g,nsample)
        g2 = applyQ(et,g2)
        writeImage(gbpfile, g2)
        gr = ArraySegment.cutM(gr,20,nz,0,nx)
        writeImage(grfile, gr)
        if iter>1:
            gold = readImage(goldfile,nz,nx)
            bp.apply(gold,gold)
            gold = ArraySegment.cutM(gold,20,nz,0,nx)
            grold = aigi(et,gold,nsample)
            grold = ArraySegment.cutM(grold,20,nz,0,nx)
            writeImage(groldfile, grold)
        ## line-search and update vel
        Inv.partTwo(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir, iter)
    return

#############################################################################
def ttm(et,nsample):
    print "Go into TensorTimeMark"
    et2 = Tensors.thinTensors2(et,nz,nx)
    i = readImage(ifile,nz,nx)
    i = div(i,max(abs(i)))
    s = readImage(sfile,nsample,3)
    ttm = TensorTimeMark(et,i,s,rrtDir)
    print "Out of TensorTimeMark"
    return et2

def aigi(et,g,nsample):
    print "Go into IGInAdjoint"
    s = readImage(sfile,nsample,3)
    m = readIntImage(mfile,nz,nx)
    t = readImage(tfile,nz,nx)
    c = 0.25
    t2 = mul(t,t)
    ai= AdjointIGI(et,c,t2,0.001,10000)
    ai.applyAdjoint(g,m,s)
    IGI(nz,nx,s,et,rrtDir)
    q = readImage(qfile,nz,nx)
    print "Out of IGInAdjoint"
    return q

def dtm():
    print "Go into DipTimeMark"
    i = readImage(ifile,nz,nx)
    i = div(i,max(abs(i)))
    s = readImage(sfile,ns,3)
    DipTimeMark(1.0,1.0,1.0,i,s,rrtDir)
    print "Out of DipTimeMark"

def pickByTensor():
    i = readImage(ifile,nz,nx)
    i = div(i,max(abs(i)))
    et,et2 = getTensors(i)
    s1,s2 = getSemblance(i)
    et2 = sembTensors(et2,s1,s2)
    ed = getMask()
    sp = SamplePicker(i, ed, et2, 77)
    print "total samples picked: ", sp.getNumPicks()
    sc = sp.getCIPCoord2D(0.0,0.0,dz,dx)
    goSamples(sc,i,rrtDir+"/./samplesT")
    return sp.getNumPicks(),et2

def getSemblance(i):
    et,et2 = getTensors(i)
    s1 = lsf1.semblance(LocalSemblanceFilter.Direction2.V,et,i)
    s2 = lsf2.semblance(LocalSemblanceFilter.Direction2.U,et,i)
    s2 = ClipData.clipL(s2,10.0)
    s1 = clip(0.001,1.0,s1)
    s2 = clip(0.0001,1.0,s2)
    writeImage(s1file,s1)
    writeImage(s2file,s2)
    return s1,s2

def sembTensors(e,s1,s2):
    e.setEigenvalues(s2,s1)
    return e

def getTensors(i):
    ttm = Tensors(1.0,1.0,1.0,i)
    et1 = ttm.getTensors()
    et2 = ttm.getThinTensors()
    return et1,et2

def getMask():
    i = readImage(ifile,nz,nx)
    i = div(i,max(abs(i)))
    e = getEnvelope(i)
    e = div(e,max(abs(e)))
    dt= DistanceTransform(e)
    e = dt.initDT(e,40.0,15,30)
    e = sub(1.0,e)
    et,et2 = getTensors(i)
    s1 = lsf1.semblance(LocalSemblanceFilter.Direction2.V,et,i)
    s2 = lsf2.semblance(LocalSemblanceFilter.Direction2.U,et,i)
    s1 = clip(0.0,1.0,s1)
    s2 = clip(0.0,1.0,s2)
    s2 = sub(1.0,s2)
    s2 = dt.initDT(s2,90.0,15,30)
    dt= DistanceTransform(s2)
    d = dt.apply(s2)
    return mul(d,e)

def getEnvelope(i):
    ei = ht.env2(i)
    return ei

def applyQ(et,image):
    t = readImage(tfile,nz,nx)
    c = 0.25
    t2 = mul(t,t)
    ai= AdjointIGI(et,c,t2,0.001,10000)
    q = ai.applyQ(image)
    return q

#############################################################################
def goSamples(sl, image, name):
    sa = ArraySegment(sl)
    zsample = sa.rowSelect(sl,0)
    xsample = sa.rowSelect(sl,1)
    zc = div(zsample, dz)
    xc = div(xsample, dx)
    vc = sub(zc, zc)
    sc = sa.conCols(zc,xc)
    sc = sa.conCols(sc,vc)
    writeImage(name+".dat",sc)
#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
