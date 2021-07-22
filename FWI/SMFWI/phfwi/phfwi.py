from utility import *

freq = 12.0
cfile = wDir+"/./COORD/coords_ns11.txt"

##############################################################################
niter = 10
vinput= wDir+"/./v.dat"
rrtDir= wDir+"/./RRT/"
ifile = rrtDir+"/./guidance.dat"
sfile = rrtDir+"/./samplesT.dat"

gfile = wDir+"/./g.dat"
gbpfile = wDir+"/./gbp.dat"
goldfile = wDir+"/./gold.dat"
grfile = wDir+"gr.dat"
groldfile = wDir+"/./grold.dat"

s1file = rrtDir+"/./s1.dat"
s2file = rrtDir+"/./s2.dat"
hfile = wDir+"/./h.dat" 

lsf = LocalSmoothingFilter(0.001,1000)

ht = HilbertTrans(nz,15,1.0)
lsf1 = LocalSemblanceFilter(16,1)
lsf2 = LocalSemblanceFilter(1,16)
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
    s = div(1.0,v)
    d = add(sub(v,v),1.0)
##
    sou = FwiUtil.genRicker(nt, 150, freq, dt)
##
    nsample,et = pickByTensor()
    et2 = ttm(et,nsample)
##
    sl = readImage(sfile,nsample,3)
    image = readImage(ifile,nz,nx)
    ph = ProjHessian(image,sl)
    h0 = ph.iniHessian()
    g0 = ph.runGrad(sou, dt, ng, sc, gc, pml, dz, dx, v, d, wDir,0)
    writeImage(wDir+"./Hessian/"+"h_iter0.dat",h0)
##
    for i in range(10):
        iter = i+1
        print "=================="
        print "iteration = ", iter
        print "------------------"
        ## forward modeling synthetic data and gradient calculation
        v1 = ph.runWolfeLS(et,h0,g0,sou,dt,ng,sc,gc,pml,dz,dx,v,d,wDir,iter)
        g1 = ph.runGrad(sou,dt,ng,sc,gc,pml,dz,dx,v1,d,wDir,iter+1)
        ss = div(1.0,v1)
        ds = sub(mul(ss,ss),mul(s,s))
        h1 = ph.runHessian(h0,g0,ds,g1,wDir,iter)
        h0 = h1
        g0 = g1
        v = v1
        s = ss
    return
#####################################################
def ttm(et,nsample):
    print "Go into TensorTimeMark"
    et2 = Tensors.thinTensors2(et,nz,nx)
    i = readImage(ifile,nz,nx)
    i = div(i,max(abs(i)))
    s = readImage(sfile,nsample,3)
    ttm = TensorTimeMark(et,i,s,rrtDir)
    print "Out of TensorTimeMark"
    return et2

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
    et,et2 = getTensors(i)
    s1 = lsf1.semblance(LocalSemblanceFilter.Direction2.V,et,i)
    s2 = lsf2.semblance(LocalSemblanceFilter.Direction2.U,et,i)
    e = div(e,max(abs(e)))
    dt= DistanceTransform(e)
    e = dt.initDT(e,40.0,15,30)
    e = sub(1.0,e)
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
#    plot2Sample(image,sz,sx,zsample,xsample,None,name)
#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain())
