#!/bin/bash 
#SBATCH -J PL-PBp1
#Output and error
#SBATCH -o slurm.%j.out 
#SBATCH -e slurm.%j.err 
#Initial working directory 
#SBATCH -D ./
# Wall clock limit: 
#SBATCH --time=48:00:00
#SBATCH --no-requeue
#SBATCH --exclude=i01r01c01s02,i01r01c01s01,i01r01c01s03
#Setup of execution environment
#SBATCH --export=NONE 
#SBATCH --get-user-env
#SBATCH --nodes=24
#SBATCH --ntasks-per-node=48
#SBATCH --account=pn52ci
#SBATCH --partition=general
#SBATCH --mail-type=ALL
#SBATCH --mail-user=chanaprom.cholsuk@tum.de

export WORK_DIR="$(pwd)"

module load slurm_setup
module load vasp/6.4


for i in {1..182};
do
        cd "$WORK_DIR/$i"
        vasp6 -n $SLURM_NTASKS
done
exit 0
