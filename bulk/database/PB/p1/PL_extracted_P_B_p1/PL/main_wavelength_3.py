from pyphotonics.photoluminescence import Photoluminescence
import numpy as np
import matplotlib.pyplot as plt
from pymatgen.core.structure import Structure
from pymatgen.io.vasp.inputs import Poscar, Kpoints

class ConfigurationCoordinate:
	def read_poscar(self,i_path, l_get_sorted_symbols=False):
        	poscar = Poscar.from_file("{}".format(i_path))
        	struct = poscar.structure
        	if l_get_sorted_symbols:
            		return struct, poscar.site_symbols
        	else:
            		return struct

#m = np.zeros(287)
#for i in range(144):
#    m[i] = 14.0067 * 1.660539040e-27
#for k in range(144,287):
#    m[k] = 10.811 * 1.660539040e-27

cc = ConfigurationCoordinate()
struct_i, sorted_symbols = cc.read_poscar("./CONTCAR_GS", True)
m = np.array([spc.atomic_mass for spc in struct_i.species])* 1.660539040e-27
#print(masses)

path = "./"
path_phonopy = "phonopy/"
p = Photoluminescence(path_phonopy,
                        path + "CONTCAR_GS",
                        path + "CONTCAR_ES",
                        864, "phonopy", m, 1000, shift_vector=[0.0, 0, 0.1])


print("Delta_R=", p.Delta_R)
print("Delta_Q=", p.Delta_Q)
print("HuangRhyes=", p.HuangRhyes)
#######################################
fig, ax = plt.subplots(figsize=(6, 4))
##s_k = list(p.S)
##s_k_rev = []
#for i in reversed(s_k):
#	s_k_rev.append(i)

ax.plot(p.S_omega,linewidth=4,color='tab:orange')
ax.set_ylabel('$S(\hbar\omega)$', fontsize=12)
ax.set_xlabel('Phonon energy (meV)', fontsize=12)
plt.xlim(0, 200)
ax2 = ax.twinx()
ax2.plot(p.S[100:200],'.')
ax2.set_ylabel("S$_k$",color='tab:blue',fontsize=12)
# Set tick font size
for label in (ax.get_xticklabels() + ax.get_yticklabels() + ax2.get_yticklabels()):
	label.set_fontsize(12)
#####plt.savefig('S_omega_k.png', bbox_inches='tight')

p.write_S('S')

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(p.S,'.')
ax.set_ylabel('S$_k$', fontsize=12)
ax.set_xlabel('Phonon modes', fontsize=12)
ax2 = ax.twinx()
ax2.plot(p.IPR,'r.')
ax2.set_ylabel("IPR",color='red',fontsize=12)
plt.savefig('S_IPR.png', bbox_inches='tight')

max_s = max(p.S)
index_max_s = p.S.index(max_s)
print(max_s,index_max_s,p.IPR[index_max_s])

####################
np.savetxt("phonon.csv",np.c_[p.S,p.IPR],fmt='%.3f',delimiter=',',header='partial HR')
#####################

A, I = p.PL(1, p.HuangRhyes, 2.9406)
#######################################
fig, ax = plt.subplots(figsize=(10, 10))
spectrum = I.__abs__()/max(I.__abs__())
#print(len(spectrum))
ax.plot(spectrum,linewidth=3)
ax.set_xlabel('Photon energy (eV)', fontsize=16)
ax.set_ylabel('PL intensity (arb. units)', fontsize=16)
plt.xlim(500, 2500)
x_values, labels = plt.xticks()
labels = [float(x)/p.resolution for x in x_values]
plt.xticks(x_values, labels)
#plt.xlim(1800, 2200)
# Set tick font size
for label in (ax.get_xticklabels() + ax.get_yticklabels()):
	label.set_fontsize(16)
#plt.savefig('I_CNVN.pdf', bbox_inches='tight')
#print(labels)
#######################################

intensity = I.__abs__()/max(I.__abs__())
energy = np.divide(range(1001,5001),1000)
lambda_convert = np.flip(np.divide(1240,energy))
intensity_selected = intensity[1000:5001]

np.savetxt("PL.txt",np.c_[lambda_convert,np.flip(intensity_selected)],fmt='%.3f',delimiter=' ')

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(lambda_convert,np.flip(intensity_selected),linewidth=3,color='tab:orange')
ax.set_xlabel('Wavelength (nm)', fontsize=12)
ax.set_ylabel('PL intensity (arb. units)', fontsize=12)
plt.title('P$_B^{+1}$')
#plt.xlim(300, 600)

plt.savefig('I-wavelength-2.png', bbox_inches='tight',dpi=300)

