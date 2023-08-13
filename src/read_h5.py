import h5py
import numpy as np
import matplotlib.pyplot as plt

def read_hdf5_file(filename):
    with h5py.File(filename, 'r') as h5f:
        for img_name in h5f.keys():
            img_group = h5f[img_name]
            print("Image Name:", img_name)
            print("Number of Pulses:", img_group.attrs['npulses'])
            
            # Display image attributes
            print("ESASE:", img_group.attrs['esase'])
            print("EWidths:", img_group.attrs['ewidths'])
            print("EPhases:", img_group.attrs['ephases'])
            print("Carrier:", img_group.attrs['carrier'])
            print("Streak Amplitude:", img_group.attrs['streakamp'])
            
            # Display Auger features
            print("Auger Features:")
            for center, value in img_group['augers'].attrs.items():
                print(f"Center: {center}, Value: {value}")
            
            # Display Photo features
            print("Photo Features:")
            for center, value in img_group['photos'].attrs.items():
                print(f"Center: {center}, Value: {value}")
            
            # Display Valence Photo features
            print("Valence Photo Features:")
            for center, value in img_group['valencephotos'].attrs.items():
                print(f"Center: {center}, Value: {value}")
            
            # Display LEG coefficients
            print("LEG Coefficients:")
            print(img_group['legcoeffs'][:])
            
            # Display energies and histogram
            energies = img_group['energies'][:]
            hist = img_group['hist'][:]
            plt.imshow(hist.T, extent=(energies[0], energies[-1], 0, 2 * np.pi), origin='lower', aspect='auto')
            plt.xlabel('Energy')
            plt.ylabel('Angle')
            plt.title('Histogram')
            plt.colorbar()
            plt.show()

if __name__ == '__main__':
    filename = '/Users/jhirschm/Documents/MRCO/cookiebox_simulation/src/output_simdata.h5'  # Change this to the actual filename
    read_hdf5_file(filename)
