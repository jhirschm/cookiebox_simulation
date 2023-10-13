#!/usr/bin/python3

import sys
import numpy as np
import h5py
import matplotlib.pyplot as plt

def check_pulse_overlap(new_esase, new_width, new_phase, esase_list, ewidths_list, ephases_list):
    new_pulse_valid = True
    current_num_pulses = len(esase_list)
    # sort lists by esase
    # print(esase_list)
    # print(ewidths_list)
    # print(ephases_list)

    # combined_lists = list(zip(esase_list, ewidths_list, ephases_list))
    # sorted_lists = combined_lists.sort(key=lambda x: x[0])
    # esase_list, ewidths_list, ephases_list = zip(*sorted_lists)

    # print(esase_list)
    # print(ewidths_list)
    # print(ephases_list)

    for p in range(current_num_pulses): 
        # width_1 = ewidths_list[p]
        # width_2 = new_width
        width_1 = 0.5 #Modified for 0.5 ev version
        width_2 = 0.5
        if np.abs(new_esase - esase_list[p]) > (width_1+width_2): #any statment to look thoruhg list simulatneously
            new_pulse_valid = new_pulse_valid
        else:
            if np.abs(new_phase - ephases_list[p]) > np.pi/8:
                new_pulse_valid = new_pulse_valid
            else:
                new_pulse_valid = False
                return new_pulse_valid
    return new_pulse_valid

def main():
    print(sys.argv)
    if len(sys.argv)<2:
        print('syntax:\t%s <outputfilehead> <nimages> <streakamp optional> <nelectrons scale optional>'%(sys.argv[0]))
        return
    streakamp = 20.
    nimages = 10
    scale = 10
    if len(sys.argv)>2:
        nimages = int(sys.argv[2])
    if len(sys.argv)>3:
        streakamp = float(sys.argv[3])
    if len(sys.argv)>4:
        scale = int(sys.argv[4])

    outhead = sys.argv[1]
    nangles = 16 
    nenergies = 2048 
    emin = 0
    emax = 512

    etotalwidth = 10.
    ecentral = 535.
    angles = np.linspace(0,np.pi*2.,nangles+1)
    energies = np.linspace(emin,emax,nenergies+1)

    print(outhead)
    h5f = h5py.File('%s_simdata.h5'%(outhead),'w')
    # print(h5f)
    for i in range(nimages):
        img = h5f.create_group('img%05i'%i)

        # Set the desired number of pulses
        num_pulses = int(np.random.uniform(0, 6)) # allowing for 0-5 pulses

        # Initialize lists to store features
        esase_list = []
        ewidths_list = []
        ephases_list = []

        while len(esase_list) < num_pulses:
            valid_pulse = False

            esase = np.random.normal(ecentral, etotalwidth)
            ewidths = np.random.gamma(1.5, 0.125) + 0.5
            ephases = np.random.uniform(0.0, 2.0 * np.pi)


            if len(esase_list) == 0:
                    esase_list.append(esase)
                    ewidths_list.append(ewidths)
                    ephases_list.append(ephases)
                    valid_pulse = True

            while valid_pulse == False:
                valid_pulse = check_pulse_overlap(esase, ewidths, ephases, esase_list, ewidths_list, ephases_list)
                if valid_pulse == True:
                    esase_list.append(esase)
                    ewidths_list.append(ewidths)
                    ephases_list.append(ephases)
                else:
                    esase = np.random.normal(ecentral, etotalwidth)
                    ewidths = np.random.gamma(1.5, 0.125) + 0.5
                    ephases = np.random.uniform(0.0, 2.0 * np.pi)
        # while len(esase_list) < num_pulses: # prevents repeated features
        #     esase = np.random.normal(ecentral, etotalwidth)
        #     ewidths = np.random.gamma(1.5, 0.125) + 0.5
        #     ephases = np.random.uniform(0.0, 2.0 * np.pi)

        #     # Check for duplicates in the lists
        #     if esase not in esase_list and ewidths not in ewidths_list and ephases not in ephases_list:
        #         #make eval on esase and ephases...take mean of ewidths and use that in definition of close (or twice width)
        #         # .1 radians or .25 radians
        #         esase_list.append(esase)
        #         ewidths_list.append(ewidths)
        #         ephases_list.append(ephases)

        img.attrs['npulses'] = num_pulses 
        # print(img.attrs['npulses'])
        img.attrs['esase'] = esase_list
        # print(img.attrs['esase'])
        img.attrs['ewidths'] = ewidths_list
        # print(img.attrs['ewidths'])
        img.attrs['ephases'] = ephases_list
        # rather than this, let's eventually switch to using a dict for the Auger features and then for every ncounts photoelectron, we pick from this distribution an Auger electron.
        naugerfeatures = {365:1.5,369:1.5,372:1.5}
        caugerfeatures = {250.:3.,255.:2.5,260.:2.5}
        oaugerfeatures = {505:2.5,497:1.,492:1.}
        augerfeatures = {**naugerfeatures, **caugerfeatures, **oaugerfeatures}

        img.create_group('augers')
        
        for center in list(augerfeatures.keys()):
            img['augers'].attrs['%.2f'%center] = float(augerfeatures[center])
            #print('%.2f'%center)
            #print(img['augers'].attrs['%.2f'%center])
        # for center, width in zip(img.attrs['esase'], img.attrs['ewidths']):
        #     nitrogencenters = {center-409.9 : width} #changing for observation of width
        #     carboncenters = {center-284.2 : width}
        #     nvalencecenters = {center-37.3 :width}
        #     ovalencecenters = {center-41.6 : width}

        for center, width in zip(img.attrs['esase'], img.attrs['ewidths']):
            nitrogencenters = {center-409.9 : .5} 
            carboncenters = {center-284.2 : .5}
            nvalencecenters = {center-37.3 :.5}
            ovalencecenters = {center-41.6 : .5}

        if num_pulses > 0:
            photofeatures = {**carboncenters,**nitrogencenters}
        else:
            photofeatures = {}
        
        img.create_group('photos')
        for center in list(photofeatures.keys()):
            img['photos'].attrs['%.2f'%center] = float(photofeatures[center])

        if num_pulses > 0:
            valencefeatures = {**nvalencecenters,**ovalencecenters}
        else:
            valencefeatures = {}
        img.create_group('valencephotos')
        for center in list(valencefeatures.keys()):
            img['valencephotos'].attrs['%.2f'%center] = float(valencefeatures[center])

        img.attrs['carrier'] = np.random.uniform(0.,2.*np.pi)
        img.attrs['streakamp'] = streakamp
        img.create_dataset('legcoeffs',shape=(img.attrs['npulses'],5),dtype=float) # only allowing for the 0,2,4 even coeffs for now

        ens = []
        for a in range(nangles):
            ens.append([])

        for p in range(img.attrs['npulses']):
            c0 = 1.
            c2 = np.random.uniform(-1,1)
            c4 = np.random.uniform(-(c0+c2),c0+c2)
            img['legcoeffs'][p,:] = [c0, 0., c2, 0., c4]
            poldist = np.polynomial.legendre.Legendre(img['legcoeffs'][p,:])(np.cos(angles[:-1]))
            for a in range(nangles):
                ncounts = int(poldist[a] * scale)
                augercounts = int(scale)
                if ncounts > 0:
                    streak = img.attrs['streakamp']*np.cos(angles[a]-img.attrs['ephases'][p]+img.attrs['carrier'])
                    centers = list(np.random.choice(list(img['photos'].attrs.keys()),int(np.sqrt(ncounts))))
                    for c in centers:
                        ens[a] += list(np.random.normal(float(c)+float(streak),float(img['photos'].attrs[c]),int(np.sqrt(ncounts))))
                    centers = list(np.random.choice(list(img['augers'].attrs.keys()),int(np.sqrt(augercounts))))
                    for c in centers:
                        ens[a] += list(np.random.normal(float(c)+float(streak),float(img['augers'].attrs[c]),int(np.sqrt(augercounts))))
                    centers = list(np.random.choice(list(img['valencephotos'].attrs.keys()),int(np.sqrt(ncounts//10))))
                    for c in centers:
                        ens[a] += list(np.random.normal(float(c)+float(streak),float(img['valencephotos'].attrs[c]),int(np.sqrt(ncounts//10))))
        h = np.zeros((nenergies,nangles),dtype=int)
        for a in range(nangles):
            h[:,a] = np.histogram(ens[a],energies)[0]
        img.create_dataset('hist',data=h)
        img.create_dataset('energies',data=energies[:-1])

        hits = img.create_group('hits')
        
        # plt.imshow(h.T, extent=[energies.min(), energies.max(), angles.min(), angles.max()],
        #                origin='lower', aspect='auto', cmap='viridis')
        # plt.show()
        for a in range(len(ens)):
            #print(len(ens[a]))
            hits.create_dataset('%i'%a,data=ens[a][:])
    h5f.close()

    return


if __name__ == '__main__':
    main()
