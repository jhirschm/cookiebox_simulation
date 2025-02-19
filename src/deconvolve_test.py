#!/usr/bin/python3.5

import numpy as np
import sys

def gauss(x,c,w):
    return np.exp(-np.power((x-c)/w,int(2)))

def sig(x,c,w,b):
    g = gauss(x,c,w)
    dg = -2*(x-c)/w*gauss(x,c,w)
    ddg = gauss(x,c,w)*4*(x-c)*(x-c)/(w*w) + 4/w*gauss(x,c,w)
    g = np.roll(g,int(-c))
    dg = np.roll(dg,int(-c))
    ddg = np.roll(ddg,int(-c))
    return g +b*dg -0.2*b*ddg

def weiner(X,N):
    return np.power(np.abs(X)/(np.abs(X)+N*np.max(np.abs(X))),int(2))

def main():
    nhits = 10
    ofscale = 20
    ufscale = 75
    if 1<len(sys.argv):
        nhits = int(sys.argv[1])
        if 2< len(sys.argv):
            ofscale = int(sys.argv[2])
            if 3< len(sys.argv):
                ufscale = int(sys.argv[3])
    x = np.arange(667,dtype=int)
    nscale=3e-1
    n = np.random.normal(0,nscale,len(x))
    f = np.fft.fftfreq(x.shape[0])
    F = gauss(f,0,1./5.)
    y = np.zeros(x.shape,dtype=float)
    inds = np.random.choice(x,nhits)
    y[inds] = [np.abs(np.random.normal(1,.5,len(inds)))]
    s = sig(x,20,3,1)
    S = np.fft.fft(s)
    DS = 1j*f*S
    SDS = S+DS
    W = weiner(S,nscale)
    df = f[1]-f[0]
    OF = gauss(f,0,ofscale*df)
    Y = np.fft.fft(y)
    yg = np.fft.ifft(Y*(SDS))+nscale*n
    YG = np.fft.fft(yg.real)
    yd = np.fft.ifft(YG/(SDS))
    yf = np.fft.ifft(YG*W)
    yof = np.fft.ifft(YG*OF)
    yc = np.fft.ifft(YG*(-S))
    ycof = np.fft.ifft(YG*(-S)*OF)
    yfinal = yc*np.abs(ycof)
    boxaverage = np.zeros(len(yfinal),dtype=float)
    boxaverage[-1] = 1.
    boxaverage[0:2] = 1.
    BA=np.fft.fft(boxaverage)
    weightedinds = np.fft.ifft(np.fft.fft(x*yc)*BA)/np.fft.ifft(np.fft.fft(yc)*BA)
    gaussweightedinds = np.fft.ifft(np.fft.fft(x*yc)*gauss(f,0,df*ufscale))/np.fft.ifft(np.fft.fft(yc)*gauss(f,0,df*ufscale))

    np.savetxt('data_fs/processed/deconvolve.out',np.column_stack((x,y,s,yg.real,yd.real,yf.real,yof.real,yc.real,ycof.real,yfinal.real,gaussweightedinds.real,weightedinds.real)),fmt='%.6f')
    np.savetxt('data_fs/processed/deconvolve.fft',np.column_stack((f,np.abs(Y),np.abs(SDS),np.abs(YG),np.abs(YG*W))),fmt='%.6f')
    return

if __name__ == '__main__':
    main()
