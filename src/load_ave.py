#!/usr/bin/python3

import time

import numpy as np
import h5py
import sys
import random
import math
from sklearn.multioutput import MultiOutputRegressor
from sklearn import preprocessing
from sklearn import linear_model
from sklearn import metrics
from sklearn.feature_selection import mutual_info_regression
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, RationalQuadratic, ExpSineSquared, ConstantKernel, DotProduct, Matern
#from sklearn.externals import joblib
import joblib
import re

# Exploring Kernel Ridge Regression -- https://scikit-learn.org/stable/auto_examples/gaussian_process/plot_compare_gpr_krr.html#sphx-glr-auto-examples-gaussian-process-plot-compare-gpr-krr-py
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import GridSearchCV

from warnings import simplefilter

simplefilter(action='ignore', category=FutureWarning)


def ydetToLorenzo(y):
    '''
    Lorenzo, e.g. Tixel detector, has 48x48 pixels per tile, each pixel is 100 microns square, r is in meters from Ave/Naoufal
    '''
    q = [2.*math.pi*random.random() for i in range(len(y))]
    return (np.array(q),1e4*np.array(r)*np.cos(q),1e4*np.array(r)*np.sin(q))

def katiesplit(x,y):
    sz = x.shape[0] 
    inds = np.arange(x.shape[0])
    np.random.shuffle(inds)
    traininds = inds[:sz//4]
    testinds = inds[sz//4:2*sz//4]
    validateinds = inds[2*sz//4:3*sz//4]
    oobinds = inds[3*sz//4:]
    x_train = x[traininds,:]
    y_train = y[traininds,:]
    x_test = x[testinds,:]
    y_test = y[testinds,:]
    x_validate = x[validateinds,:]
    y_validate = y[validateinds,:]
    x_oob = x[oobinds,:]
    y_oob = y[oobinds,:]
    return (x_train,x_test,x_validate,x_oob,y_train,y_test,y_validate,y_oob)



def loaddata():
    x_all = []
    y_all = []
    if len(sys.argv) < 2:
        print("syntax: %s <datafile>"%(sys.argv[0]) )
        return x_all,y_all

    for fname in sys.argv[1:]:
        f = h5py.File(fname,'r') #  IMORTANT NOTE: it looks like some h5py builds have a resouce lock that prevents easy parallelization... tread lightly and load files sequentially for now.
        for vsetting in list(f.keys())[3:-2]: # restricting to only the closest couple vsettings to optimal... correction, now only the central (optimal) one, but for each 'logos'
            elist = list(f[vsetting]['energy'])
            alist = list(f[vsetting]['angle'])
            amat = np.tile(alist,(len(elist),1)).flatten()
            emat = np.tile(elist,(len(alist),1)).T.flatten()
            tdata = f[vsetting]['t_offset'][()].flatten()
            ydata = f[vsetting]['y_detector'][()].flatten()
            xdata = f[vsetting]['x_detector'][()].flatten()
            xsplat = f[vsetting]['splat']['x'][()].flatten()
            vset = f[vsetting][ list(f[vsetting].keys())[0] ][-1][1] # eventually, extract the whole voltage vector as a feature vector for use in GP inference
            vsetvec = np.ones(xsplat.shape,dtype=float)*vset
            validinds = np.where((abs(xsplat-185)<2) * (emat>0) * (abs(ydata)<.050))
            nfeatures = 3
            ntruths = 2
            featuresvec = np.zeros((len(xsplat[validinds]),nfeatures),dtype=float)
            truthsvec = np.zeros((len(xsplat[validinds]),ntruths),dtype=float)
            featuresvec[:,0] = np.log(-1.*vsetvec[validinds])
            featuresvec[:,1] = np.log(emat[validinds])
            featuresvec[:,2] = amat[validinds]
            truthsvec[:,0] = np.log(tdata[validinds])
            truthsvec[:,1] = ydata[validinds]
            truthsvec[:,1] *= 1e3 # converting to mm
            if len(x_all)<1:
                x_all = np.copy(featuresvec)
                y_all = np.copy(truthsvec)
            else:
                x_all = np.row_stack((x_all,featuresvec))
                y_all = np.row_stack((y_all,truthsvec))
    return x_all,y_all


def featurizeX(X):
    first = X
    second = 1./2*np.power(X,int(2))
    third = 1./(2*3)*np.power(X,int(3))
    fourth = 1./(2*3*4)*np.power(X,int(4))
    return np.column_stack((first,second,third,fourth))

def main():
    X_all = []
    Y_all = []
    X_all,Y_all = loaddata()
    if len(Y_all)<1:
        print("no data loaded")
        return
    print("data loaded\tcontinuing to fitting")
    X_train,X_test,X_valid,X_oob,Y_train,Y_test,Y_valid,Y_oob = katiesplit(X_all,Y_all)



    Xscaler = preprocessing.StandardScaler(copy=False).fit(X_train)
    Yscaler = preprocessing.StandardScaler(copy=False).fit(Y_train)
    #Xscaler = preprocessing.MinMaxScaler((0,64),copy=False).fit(X_train)
    #Yscaler = preprocessing.MinMaxScaler((0,64),copy=False).fit(Y_train)

    X_train = Xscaler.transform(X_train)
    Y_train = Yscaler.transform(Y_train)

    X_test = Xscaler.transform(X_test)
    Y_test = Yscaler.transform(Y_test)

    X_valid = Xscaler.transform(X_valid)
    Y_valid = Yscaler.transform(Y_valid)

    X_oob = Xscaler.transform(X_oob)
    Y_oob = Yscaler.transform(Y_oob)

    mi_tof = mutual_info_regression(X_train,Y_train[:,0])
    mi_tof /= np.max(mi_tof)
    print('mi for tof time\t',mi_tof)
    mi_pos = mutual_info_regression(X_train,Y_train[:,1])
    mi_pos /= np.max(mi_pos)
    print('mi for y_position',mi_pos)


    #./data_ave/ind_25-plate_tune_grid_Range_*/analyzed_data.hdf5
    m = re.match('(.*)(ind.*/)analyzed_data.hdf5',sys.argv[-1])
    if m:
        np.savetxt('%strain_transformed.dat'%(m.group(1)),np.column_stack((X_train,Y_train)))
        np.savetxt('%soob_transformed.dat'%(m.group(1)),np.column_stack((X_oob,Y_oob)))

        c = np.ones((5,5),dtype=float)  
        sz = len(X_train[:,0])
        c[0,1] = c[1,0] = np.correlate(X_train[:,0],X_train[:,1],mode='valid')/sz
        c[1,2] = c[2,1] = np.correlate(X_train[:,1],X_train[:,2],mode='valid')/sz
        c[2,0] = c[0,2] = np.correlate(X_train[:,2],X_train[:,0],mode='valid')/sz

        c[0,3] = c[3,0] = np.correlate(X_train[:,0],Y_train[:,0],mode='valid')/sz
        c[1,3] = c[3,1] = np.correlate(X_train[:,1],Y_train[:,0],mode='valid')/sz
        c[2,3] = c[3,2] = np.correlate(X_train[:,2],Y_train[:,0],mode='valid')/sz
        c[0,4] = c[4,0] = np.correlate(X_train[:,0],Y_train[:,1],mode='valid')/sz
        c[1,4] = c[4,1] = np.correlate(X_train[:,1],Y_train[:,1],mode='valid')/sz
        c[2,4] = c[4,2] = np.correlate(X_train[:,2],Y_train[:,1],mode='valid')/sz
        c[3,4] = c[4,3] = np.correlate(Y_train[:,0],Y_train[:,1],mode='valid')/sz

        np.savetxt('%sX_train_Y_train_featurecorr.dat'%(m.group(1)),c,fmt='%.3f')

    stime = time.time()
    firstmodel = linear_model.LinearRegression().fit(X_oob[:,1].reshape(-1,1), Y_oob[:,0].reshape(-1,1))
    print("Time for initial linear model fitting on out-of-bag samples: %.3f" % (time.time() - stime))
    stime = time.time()
    Y_test_pred = firstmodel.predict(X_test[:,1].reshape(-1,1))
    Y_valid_pred = firstmodel.predict(X_valid[:,1].reshape(-1,1))
    print("Time for initial linear model inference: %.3f" % (time.time() - stime))
    print ("linear model score (test): ", metrics.r2_score(Y_test[:,0], Y_test_pred))
    print ("linear model score (validate): ", metrics.r2_score(Y_valid[:,0], Y_valid_pred))

    if m:
        headstring = 'vsetting\tlog(en)\tangle\tlog(tof)\typos\tpredtof'
        np.savetxt('%stest.dat'%(m.group(1)),np.column_stack((X_test,Y_test,Y_test_pred)),header=headstring)
        np.savetxt('%svalid.dat'%(m.group(1)),np.column_stack((X_valid,Y_valid,Y_valid_pred)),header=headstring)

    print("Now moving to a perturbation linearRegression")
    '''
    print("Skipping PLR")
    '''

    stime = time.time()
    X_featurized = featurizeX(np.copy(X_train)) 
    perturbmodel_tof = linear_model.LinearRegression().fit(X_featurized, Y_train[:,0].reshape(-1,1) - firstmodel.predict(X_train[:,1].reshape(-1,1)))
    perturbmodel_pos = linear_model.LinearRegression().fit(X_featurized, Y_train[:,1].reshape(-1,1) )
    print("Time for pertubative linear model fitting: %.3f" % (time.time() - stime))

    stime = time.time()
    X_test_featurized = featurizeX(np.copy(X_test))
    X_valid_featurized = featurizeX(np.copy(X_valid))
    Y_test_pred_tof = perturbmodel_tof.predict(X_test_featurized)
    Y_test_pred_pos = perturbmodel_pos.predict(X_test_featurized)
    Y_valid_pred_tof = perturbmodel_tof.predict(X_valid_featurized)
    Y_valid_pred_pos = perturbmodel_pos.predict(X_valid_featurized)
    Y_test_pred_tof += firstmodel.predict(X_test_featurized[:,1].reshape(-1,1))
    Y_valid_pred_tof += firstmodel.predict(X_valid_featurized[:,1].reshape(-1,1))
    print("Time for purturbative combination linear model inference: %.3f" % (time.time() - stime))
    print ("Perturbative linear model tof score (test): ", metrics.r2_score(Y_test[:,0], Y_test_pred_tof))
    print ("Perturbative linear model tof score (validate): ", metrics.r2_score(Y_valid[:,0], Y_valid_pred_tof))
    print ("Perturbative linear model pos score (test): ", metrics.r2_score(Y_test[:,1], Y_test_pred_pos))
    print ("Perturbative linear model pos score (validate): ", metrics.r2_score(Y_valid[:,1], Y_valid_pred_pos))

    if m:
        headstring = 'vsetting\tlog(en)\tangle\tlog(tof)\typos\tpredtof\tpredypos'
        np.savetxt('%stest_perturb_linear.dat'%(m.group(1)),np.column_stack((X_test,Y_test,Y_test_pred_tof,Y_test_pred_pos)),header=headstring)
        np.savetxt('%svalid_perturb_linear.dat'%(m.group(1)),np.column_stack((X_valid,Y_valid,Y_valid_pred_tof,Y_valid_pred_pos)),header=headstring)

    print("Skipping KRR")
    '''
    # Fit KernelRidge with parameter selection based on 5-fold cross validation
    param_grid = {"alpha": [1e0, 1e-1, 1e-2, 1e-3],
                  "kernel": [RationalQuadratic(l, a)
                  for l in np.logspace(-2, 2, 10)
                  for a in np.logspace(0, 2, 10)]}
    kr = GridSearchCV(KernelRidge(), param_grid=param_grid)
    stime = time.time()
    kr.fit(X_train[2000:4000,:], Y_train[2000:4000,:])
    print("Time for KRR fitting: %.3f" % (time.time() - stime))
    #print("KRR kernel: %s" % kr.kernel_)
    stime = time.time()
    Y_test_pred = kr.predict(X_test)
    Y_valid_pred = kr.predict(X_valid)
    print("Time for KRR inference: %.3f" % (time.time() - stime))
    print ("KRR model score (test): ", metrics.r2_score(Y_test, Y_test_pred))
    print ("KRR model score (validate): ", metrics.r2_score(Y_valid, Y_valid_pred))
    '''

    print("Moving on to perturbative GP")

    stime = time.time()
    nsamples = 300
    nmodels=5
    k1 = 1.0**2 * RBF(
            length_scale=np.ones(X_train.shape[1],dtype=float)
            ,length_scale_bounds=(1e-5,100)
            ) 
    '''
    k1 = 1.**2 * Matern(
            length_scale=np.ones(X_train.shape[1],dtype=float)
            ,length_scale_bounds=(1e-5,100)
            ,nu=1.5
            )

    k2 = 1.0**2 * DotProduct(sigma_0 = .1
            ) 
    '''
    k2 = 1.0**2 * RationalQuadratic(
            length_scale=1. 
            ,alpha=0.1 
            ,length_scale_bounds=(1e-5,20)
            ) 

    k3 = .5*2 * WhiteKernel(noise_level=0.01**2)  # noise terms
    k4 = ConstantKernel(constant_value = .01 ) # constant shift

    k1p = 0.05**2 * RBF(
            length_scale=np.ones(X_train.shape[1],dtype=float)
            ,length_scale_bounds=(1e-5,20)
            ) 
    '''
    k2p = 1.0**2 * DotProduct(sigma_0 = .1
            )**2
    k2p = 1.0**2 * RationalQuadratic(
            length_scale=1. 
            ,alpha=0.1 
            ,length_scale_bounds=(1e-5,20)
            ) 
            '''
    k2p = 1.**2 * Matern(
            length_scale=np.ones(X_train.shape[1],dtype=float)
            ,length_scale_bounds=(1e-5,20)
            ,nu=1.5
            )
    k3p = .5*2 * WhiteKernel(noise_level=0.01**2)  # noise terms
    k4p = ConstantKernel(constant_value = .01 ) # constant shift

    kernel_gp_tof = k1 + k2 #+ k3 + k4
    kernel_gp_pos = k1p + k2p + k3p + k4p

    Y_zeroth = Y_train[:,0].reshape(-1,1) #### CAREFUL HERE, using the shallow copy intentionally to address single output feature, numbers beyond nsamples will be bogus!!!
    Y_zeroth -= firstmodel.predict(X_train[:,1].reshape(-1,1)) 
    tof_gp = GaussianProcessRegressor(kernel=kernel_gp_tof, alpha=0, normalize_y=True, n_restarts_optimizer = 2)
    pos_gp = GaussianProcessRegressor(kernel=kernel_gp_pos, alpha=0, normalize_y=True, n_restarts_optimizer = 2)
    i=0
    fname_model_tof = []
    fname_model_pos = []
    for i in range(nmodels):
        tof_gp.fit(X_train[i*nsamples:(i+1)*nsamples,:], Y_train[i*nsamples:(i+1)*nsamples,0].reshape(-1,1))
        pos_gp.fit(X_train[i*nsamples:(i+1)*nsamples,:], Y_train[i*nsamples:(i+1)*nsamples,1].reshape(-1,1))
        print("Time for pertubative GP model fitting: %.3f" % (time.time() - stime))
        print("tof kernel = %s"%tof_gp.kernel_)
        print("tof kernel Log-marginal-likelihood: %.3f" % tof_gp.log_marginal_likelihood(tof_gp.kernel_.theta))
        print("pos kernel = %s"%pos_gp.kernel_)
        print("pos kernel Log-marginal-likelihood: %.3f" % pos_gp.log_marginal_likelihood(pos_gp.kernel_.theta))
        if m:
            fname_model_tof += ['%sgp_model_tof_%s_%i.sav'%(m.group(1),time.strftime('%Y.%m.%d.%H.%M'),i)]
            fname_model_pos += ['%sgp_model_pos_%s_%i.sav'%(m.group(1),time.strftime('%Y.%m.%d.%H.%M'),i)]
            joblib.dump(tof_gp,fname_model_tof[-1])
            joblib.dump(pos_gp,fname_model_pos[-1])


    print("Total time for pertubative GP model ensemble fitting: %.3f" % (time.time() - stime))

    if m:
        Y_test_pred_collect = []
        Y_valid_pred_collect = []
        for i in range(nmodels):
            stime = time.time()
            fname_tof = fname_model_tof[i]
            fname_pos = fname_model_pos[i]
            print('repeating for gpr in fname_model list\n%s\n%s'%(fname_tof,fname_pos))
            gpr_tof = joblib.load(fname_tof)
            gpr_pos = joblib.load(fname_pos)
            nsamples = X_test.shape[0]//8
            Y_test_tof_pred = gpr_tof.predict(X_test[:nsamples,:])
            Y_valid_tof_pred = gpr_tof.predict(X_valid[:nsamples,:])
            Y_test_pos_pred = gpr_pos.predict(X_test[:nsamples,:])
            Y_valid_pos_pred = gpr_pos.predict(X_valid[:nsamples,:])
            Y_test_tof_pred += firstmodel.predict(X_test[:nsamples,1].reshape(-1,1))
            Y_valid_tof_pred += firstmodel.predict(X_valid[:nsamples,1].reshape(-1,1))
            print("Time for perturbative GP inference: %.3f" % (time.time() - stime))
            print('GP score tof (test): ',  metrics.r2_score(Y_test[:nsamples,0],Y_test_tof_pred))
            print('GP score tof (validate): ',  metrics.r2_score(Y_valid[:nsamples,0],Y_valid_tof_pred))
            print('GP score pos (test): ',  metrics.r2_score(Y_test[:nsamples,1],Y_test_pos_pred))
            print('GP score pos (validate): ',  metrics.r2_score(Y_valid[:nsamples,1],Y_valid_pos_pred))
            if len(Y_test_pred_collect)<1:
                Y_test_pred_collect = Yscaler.inverse_transform(np.column_stack((Y_test_tof_pred,Y_test_pos_pred)))
                Y_valid_pred_collect = Yscaler.inverse_transform(np.column_stack((Y_valid_tof_pred,Y_valid_pos_pred)))
            else:
                Y_test_pred_collect = np.column_stack( (Y_test_pred_collect,Yscaler.inverse_transform(np.column_stack((Y_test_tof_pred,Y_test_pos_pred)))) )
                Y_valid_pred_collect = np.column_stack( (Y_valid_pred_collect,Yscaler.inverse_transform(np.column_stack((Y_valid_tof_pred,Y_valid_pos_pred)))) )

        headstring = 'log(vsetting)\tlog(en)\tangle\tlog(tof)\typos\tpredlog(tof)\tpredpos\t...'
        np.savetxt('%stest_GPperturb.dat'%(m.group(1)),np.column_stack((Xscaler.inverse_transform(X_test[:nsamples,:]),Yscaler.inverse_transform(Y_test[:nsamples,:]),Y_test_pred_collect)),header=headstring)
        np.savetxt('%svalid_GPperturb.dat'%(m.group(1)),np.column_stack((Xscaler.inverse_transform(X_valid[:nsamples,:]),Yscaler.inverse_transform(Y_valid[:nsamples,:]),Y_valid_pred_collect)),header=headstring)

    return

'''
    features = []
    for v in x:
        features.append((int((v-center)*8) , np.power(int((v-center)*8),int(2))//100 ))
    return features
    '''

if __name__ == '__main__':
    main()

