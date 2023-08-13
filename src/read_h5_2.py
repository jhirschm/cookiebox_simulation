import h5py
import numpy as np
import matplotlib.pyplot as plt

def plot_images(h5file):
    with h5py.File(h5file, 'r') as h5f:
        for img_name in h5f.keys():
            img_group = h5f[img_name]
            hist = img_group['hist'][:]
            energies = img_group['energies'][:]
            angles = np.linspace(0, 2 * np.pi, hist.shape[1])
            
            npulses = img_group.attrs['npulses']
            esase = img_group.attrs['esase']
            streakamp = img_group.attrs['streakamp']
            
            plt.figure(figsize=(10, 6))
            plt.imshow(hist.T, extent=[energies.min(), energies.max(), angles.min(), angles.max()],
                       origin='lower', aspect='auto', cmap='viridis')
            plt.colorbar(label='Counts')
            plt.xlabel('Energy')
            plt.ylabel('Angle (radians)')
            plt.title(f'Image: {img_name}\n' +
                      f'Pulses: {npulses}, ESASE: {esase}, Streak Amp: {streakamp}')
            plt.show()

if __name__ == '__main__':
    h5file_path = 'testing_simdata.h5'  # Update this with the correct path to your HDF5 file
    plot_images(h5file_path)
