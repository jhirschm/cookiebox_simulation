#!/bin/bash
#SBATCH --partition=lcls
#SBATCH --job-name=lstm
#SBATCH --output=output-%j.txt
#SBATCH --error=output-%j.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10g
#SBATCH --time=0-20:00:00
#SBATCH --gpus geforce_rtx_2080_ti:0
source ~/.bashrc
conda activate pytorch-gpu
export SLURM_EXACT=1
echo starting run 1 at: `date`
python3 generate_sinogram_Jack.py /sdf/group/lcls/ds/scratch/jhirschm/MRCO_Sim_Data/Oct12_2023_simdata 100000
# Print the date again -- when finished
echo Finished at: `date`
