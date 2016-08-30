# cd /Volumes/Transcend/SCAN_PROGRAM3
# python

import os
import os.path as path
import sys
import cv2
import numpy as np

fscene=os.getcwd()

os.chdir('../Utility')
cwd=os.getcwd()
sys.path.append(cwd)
import rtc_util as ut
import tcor_util as tc

os.chdir(fscene)

#----------------------------
#  Initialize
#----------------------------
print "#### Initialize ####"
# parameter input

fold=sys.argv[1]
subf,tdec=fold.split('_')
depth=float(subf[3:5])/100
nmax=int(subf[6:])
itmax=int(sys.argv[2])
dec=float(tdec)/10.0
model=subf[5]
print 'depth:',depth
print 'dec:',dec
print 'nmax:',nmax


f=open(fold +'/aparm.txt')
text=f.readlines()
f.close()
    
el=tc.read_parm(text,'el')[0]
az=tc.read_parm(text,'az')[0]
nband=int(tc.read_parm(text,'nband')[0])
offset=tc.read_parm(text,'offset')
gain=tc.read_parm(text,'gain')
if fscene.find('OLI')==-1: 
  penv=tc.read_parm(text,'penv')
else:
  penv=tc.read_parm(text,'penv') 

depth=tc.read_parm(text,'depth')[0]
wsize=tc.read_parm(text,'wsize')
wsize=[int(x) for x in wsize]
dec=tc.read_parm(text,'dec')[0]
twid=tc.read_parm(text,'twid')
cls_name=text[-1][:-1]
fun_name=text[-2][:-1]
ut.r_set0=float(text[-4][:-1])
ntau,nhigh,nsang=text[-3].split()

ut.t_set=np.array(tc.read_parm(text,'tau'))
#ut.t_set=np.arange(int(ntau))*0.2
#ut.t_set=2.0**np.arange(int(ntau))/20.0
print cls_name
print fun_name
print ut.r_set0
print ut.t_set
os.chdir('DATA')

#------------------------------
#    Main Processing
#------------------------------
#for band in [1]:
if fscene.find('OLI') == -1:
  b_list=[1,2,3]
else:
  b_list=[1,2,3,4]
for band in b_list:
  print "#### Processing of Band"+str(band)+" ####"
  ut.cosb0=np.cos((90.0-el)*np.pi/180); ut.cosb0
  print "--- function list ---"
  f_list=np.load(fun_name+'_'+str(band)+'.npy')
  cls=np.load(cls_name+'.npy')
  tc.jmax,tc.imax=cls.shape
  os.chdir('../'+fold)
  temp=[x for x in os.listdir('.') if x.find('ref'+str(band))==0]
  m=len(temp)
  if band==1:
	tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  eref=penv[band-1]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  if m != 0 :
    for n in range(m):
      print "--- "+str(n)+ " iteration ---"
      t_ref=np.load('ref'+str(band)+str(n)+'.npy')
      temp=np.where(t_ref==1.0)
      cls[temp]=-1
      eref=(1.0-dec)*eref+dec*tc.xmedian(t_ref,wsize[0])
      t_taux=np.load('tau'+str(band)+str(n)+'.npy')
      temp=np.where(t_taux==1.8)
      cls[temp]=-1
      tau=(1.0-dec)*tau+dec*tc.ymedian(t_taux,cls,wsize[1],twid[n])
      temp=np.where(cls==-1)
      print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
  iters=np.arange(itmax-m)+m
  for iter in iters:
    print "--- "+str(iter)+ " iteration ---"
    print " > reflectance "
    ref=ut.mk_ref(tc.jmax,tc.imax,f_list,tau,eref)
    temp=np.where(ref==1.0)
    cls[temp]=-1
    if iter < 3 : 
      cref=tc.aesth(ref,20,cls)
    else:
      if model == 'M' : cref=tc.aestm(ref,cls)
      elif model == 'P' : cref=tc.aesth(ref,20,cls)
      else : cref=tc.aest(ref,cls)
    print " > aerosol "
    eref=(1.0-dec)*eref+dec*tc.xmedian(ref,wsize[0])
    taux=ut.mk_tau(tc.jmax,tc.imax,f_list,eref,cref)
    temp=np.where(taux==1.8)
    cls[temp]=-1
    print " > median filter "
    tau=(1.0-dec)*tau+dec*tc.ymedian(taux,cls,wsize[1],twid[iter])
    temp=np.where(cls==-1) ; print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
    np.save('tau'+str(band)+str(iter),taux)
    np.save('ref'+str(band)+str(iter),ref)
    #temp=np.where(cls == -1)
    #np.save('cls'+str(band)+str(iter),temp)
  os.chdir('../DATA')

if fscene.find('ETM') != -1:
  b_list=[4,5,6]
elif fscene.find('AVN') != -1:
  b_list=[4]
elif fscene.find('OLI') != -1:
  b_list=[5,6,7,8]
else:
  exit()

for band in b_list:
  print "#### Processing of Band"+str(band)+" ####"
  ut.cosb0=np.cos((90.0-el)*np.pi/180); ut.cosb0
  print "--- function list ---"
  f_list=np.load(fun_name+'_'+str(band)+'.npy')
  cls=np.load(cls_name+'.npy')
  tc.jmax,tc.imax=cls.shape
  os.chdir('../'+fold)
  temp=[x for x in os.listdir('.') if x.find('ref'+str(band))==0]
  m=len(temp)
  if band==1:
	tau=depth*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  eref=penv[band-1]*np.ones(tc.imax*tc.jmax).reshape(tc.jmax,tc.imax)
  if m != 0 :
    for n in range(m):
      print "--- "+str(n)+ " iteration ---"
      t_ref=np.load('ref'+str(band)+str(n)+'.npy')
      temp=np.where(t_ref==1.0)
      cls[temp]=-1
      eref=(1.0-dec)*eref+dec*tc.xmedian(t_ref,wsize[0])
      #t_taux=np.load('tau'+str(band)+str(n)+'.npy')
      #temp=np.where(t_taux==1.8)
      #cls[temp]=-1
      #tau=(1.0-dec)*tau+dec*tc.ymedian(t_taux,cls,wsize[1],twid[n])
      temp=np.where(cls==-1)
      print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
  iters=np.arange(itmax-m)+m
  for iter in iters:
    print "--- "+str(iter)+ " iteration ---"
    print " > reflectance "
    ref=ut.mk_ref(tc.jmax,tc.imax,f_list,tau,eref)
    temp=np.where(ref==1.0)
    cls[temp]=-1
    if iter < 3 : 
      cref=tc.aesth(ref,20,cls)
    else:
      if model == 'M' : cref=tc.aestm(ref,cls)
      elif model == 'P' : cref=tc.aesth(ref,20,cls)
      else : cref=tc.aest(ref,cls)
    print " > aerosol "
    eref=(1.0-dec)*eref+dec*tc.xmedian(ref,wsize[0])
    #taux=ut.mk_tau(tc.jmax,tc.imax,f_list,eref,cref)
    #temp=np.where(taux==1.8)
    #cls[temp]=-1
    #print " > median filter "
    #tau=(1.0-dec)*tau+dec*tc.ymedian(taux,cls,wsize[1],twid[iter])
    #temp=np.where(cls==-1) ; print 100.0*len(temp[0])/float(tc.imax*tc.jmax)
    #np.save('tau'+str(band)+str(iter),taux)
    np.save('ref'+str(band)+str(iter),ref)
    #temp=np.where(cls == -1)
    #np.save('cls'+str(band)+str(iter),temp)
  os.chdir('../DATA')



exit()

