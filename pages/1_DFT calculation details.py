import streamlit as st

#https://katex.org/docs/supported.html
#https://emojidb.org/scales-emojis?utm_source=user_search

st.set_page_config(page_title="Parameter Description",layout="wide")
## Add background image
st.markdown(
    """
    <div class="banner">
        <img src="https://raw.githubusercontent.com/QCS-Theory/hBN-database/25122f09557a7d320d9172225926082c3d0e7163/icon/banner_file_size_3.svg" alt="Banner Image">
    </div>
    <style>
        .banner {
            width: 100%;
            height: 200px;
            overflow: hidden;
        }
        .banner img {
            width: 100%;
            object-fit: cover;
        }
    </style>
    """,  unsafe_allow_html=True,
)

css = '''
<style>
    [data-testid="stSidebar"]{
        min-width: 0px;
        max-width: 0px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

with st.container(border=True):
    colp11, colp0, colp1,colp2,colp21, colp3,colp4,colp5,colp6 = st.columns(9, gap="small")
    with colp11:
        st.page_link("DefectDashboard.py", label="Main database")
    with colp0:
        st.page_link("pages/0_API tutorial.py", label="API tutorial")
    with colp1:
        st.page_link("pages/1_DFT calculation details.py", label="DFT details")
    with colp2: 
        st.page_link("pages/2_About.py", label="About")
    with colp21:
        st.page_link("pages/3_Request defect.py", label="Request data")
    with colp3:
        st.page_link("pages/4_Contact.py", label="Contact")
    with colp4:
        st.page_link("pages/5_Acknowledgements.py", label="Acknowledgements")
    with colp5:
        st.page_link("pages/6_Imprint.py", label="Impressum")
    with colp6:
        st.page_link("pages/7_Version.py", label="Version")

st.header("1. DFT calculation details")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

st.subheader("1.1 Structural optimization for ground and excited states")
with st.container(border=False):
  st.markdown('''
            The Vienna  Ab initio Simulation Package (VASP) $[1,2]$ augmented wave (PAW) \
            method for the pseudopotentials $[3,4]$ was performed to investigate all hBN structures.  \
            While the ground-state configuration can be obtained by default Gaussian smearing, the excited-state \
            one needs manual electron occupation from the so-called $\Delta$SCF method $[5]$. With this \
            constraint method, both spin-up and spin-down transitions were considered. The hBN monolayer was \
            treated by adding the vacuum layer with 15 $\\text{\AA}$ separated from the neighboring repeated cell to exclude \
            layer-layer interaction. All defects were in turn added at the center of  7$\\times$7$\\times$1 supercell \
            as it had been verified not to have neighboring-cell effects. All defect geometries were relaxed by \
            fixing the cell until the total energy and all forces were converged at 10$^{-4}$ eV and 10$^{-2}$ eV/$\\text{\AA}$, \
            respectively. Spin configurations; singlets, doublets, and triplets, were constrained by the difference in \
            the number of unpaired electrons controlled by NUPDOWN in VASP. Last, The HSE06 functional was employed to \
            circumvent the common underestimation of the band gap with the single $\Gamma$-point scheme.
  ''')

st.subheader("1.2 Zero-phonon-line calculation")
with st.container(border=False):
  st.markdown(''' 
            A single dominant peak observed in the experimental photoluminescence is related to the zero-phonon line (ZPL). \
            This ZPL is defined as the transition without phonons involved. As such, this can be computed from the total \
            energy difference between the ground and excited configurations. It is worth noting that the zero-point energy \
            is canceled out by the ground and excited configurations. As noted earlier, the spin pathway between spin up \
            and down is considered separately to conserve the radiative transition; this results in two ZPLs for certain defects if both spin transitions exist.
  ''')

st.subheader("1.3 Excitation and emission polarizations")
with st.container(border=False):
  st.markdown('''
    Excitation and emission polarizations can be extracted from the transition dipole calculation. In principle, the polarizations \
    were orthogonal to their dipoles; hence, both dipoles were rotated by 90$^\circ$ and taken modulo 60$^\circ$ to obtain \
    the nearest angle to the crystal axis. Although the hexagonal lattice is spaced 120$^\circ$, after 180$^\circ$, the \
    angle from the crystal axis will be identical. To make the theoretical polarization compatible with polarization-resolved \
    PL experiments, both dipoles were projected onto the $xy$-plane to compute the in-plane polarization visibility.\n

    In order to calculate the dipoles, the wavefunctions after structural optimization can be extracted using the\
    PyVaspwfc Python code $[6]$. This also implies that the wavefunctions between ground states and excited states \
    are not necessarily the same. This leads to two types of dipoles; excitation and emission dipoles. The former is \
    responsible for the transition from the wavefunction of the most stable ground states to the wavefunction of excited \
    state without geometry relaxation. Meanwhile, the latter describes the transition from the wavefunction of the \
    most stable excited state to the wavefunction of the most stable ground state. This relation can be expressed as
  ''')
  st.latex(r'''
    \boldsymbol{\mu} = \frac{i\hbar}{(E_{f} - E_{i})m}\bra{\psi_{f}}\textbf{p}\ket{\psi_{i}}, \qquad (Eq.1)
  ''')
  st.markdown(''' 
    where the initial and final wavefunctions denoted by $\psi_{i/f}$ and the respective eigenvalues of the initial/final orbitals are indicated by $E_{i/f}$. \
    Electron mass is denoted by $m$, and a momentum operator is denoted by $\mathbf{p}$. As the wavefunctions are taken from different structures, \
    the modified version of PyVaspwfc is needed instead $[7]$. Since the dipoles can contribute both in-plan and out-of-plane directions, such contribution can be \
    differentiated by considering $\mu_z$ in the following expression 
  ''')
  st.latex(r'''
    \boldsymbol{\mu} = |\mu_x|\hat{x} + |\mu_y|\hat{y} + |\mu_z|\hat{z}. \qquad (Eq.2)
  ''')
  st.markdown('''If it is equal to 0, the dipole becomes purely in-plane (with respect to the $xy$-plane of hBN crystal). This can be quantified by the so-called \
    *linear in-plane polarization visibility*. ''')
  

st.subheader("1.4 Radiative transition rate and lifetime")
with st.container(border=False):
  st.markdown('''
    Radiative transition is the transition between two defect states that conserves spin polarization. This can be quantified by the following equation
  ''')
  st.latex(r'''
    \Gamma_{\mathrm{R}}=\frac{n_D e^2}{3 \pi \epsilon_0 \hbar^4 c^3} E_0^3 \mu_{\mathrm{e}-\mathrm{h}}^2, \qquad (Eq.3)
  ''')
  st.markdown('''
    where $\Gamma_{\mathrm{R}}$ is the radiative transition rate. $e$ is the electron charge; $\epsilon_0$ is vacuum permittivity; \
    $E_0$ is the ZPL energy; $n_{\mathrm{D}}$ is set to 1.85, which is the refractive index of the host hBN in the visible $[8]$; \
    and $\mu_{\mathrm{e}-\mathrm{h}}^2$ is the modulus square of dipole moment obtained by $Eq.1$ . Finally, the lifetime \
    is calculated by taking the inverse of the transition rate. It should be noted that the calculated lifetime can be different \
    from the experimental value due to the Purcell effect $[9]$. That is, most experiments attach hBN layers to a substrate, \
    which can alter the density of states that the emitter can couple to. The dipole emission pattern and the emitter lifetime are therefore affected.
  ''')

  st.subheader("1.5 Non-radiative transition rate and lifetime")
with st.container(border=False):
  st.markdown('''
    Despite the occurrence of radiative transition, there are instances where transitions between defects occur through intersystem crossing.\
     This transition is so-called non-radiative. The rate of this transition can be obtained by the following equations. 
  ''')
  st.latex(r'''
   \Gamma_{\mathrm{NR}}=\frac{2 \pi}{\hbar} g \sum_{n, m} p_{i n}\left|\left\langle f m\left|H^{\mathrm{e}-\mathrm{ph}}\right| i n\right\rangle\right|^2 \delta\left(E_{f m}-E_{i n}\right), \qquad (Eq.4)
  ''')
  st.markdown('''
    where $\Gamma_{\mathrm{NR}}$ is the non-radiative transition rate between electron state $i$ in phonon state $n$ and electron state $f$ in phonon state $m$. \
    $g$ is the degeneracy factor. $p_{in}$ is the thermal probability distribution of state $|in>$ based on the Boltzmann distribution. \
    $H^{\mathrm{e}-\mathrm{ph}}$ is the electron-phonon coupling Hamiltonian. Finally, the lifetime is the inverse of the transition rate, similar to the radiative case.
  ''')

  st.subheader("1.6 Quantum efficiency")
with st.container(border=False):
  st.markdown('''
    Once the radiative and non-radiative transition rates can be computed, the quantum efficiency can be then acquired from
  ''')
  st.latex(r'''
    \eta = \frac{\Gamma_{\mathrm{R}}}{\Gamma_{\mathrm{R}}+\Gamma_{\mathrm{NR}}}. \qquad (Eq.5)
  ''')

  st.subheader("1.7 Photoluminescence")
with st.container(border=False):
  st.markdown('''
    Photoluminescence $L(\hbar\omega)$ can be computed from
  ''')
  st.latex(r'''
    L(\hbar\omega) = C\omega^3 A(\hbar\omega), \qquad (Eq.6)
  ''')
  st.markdown('''
    where $C$ is a normalization constant from fitting experimental data, and $A(\hbar\omega)$ is the optical spectral function given by
  ''')
  st.latex(r'''
    A(E_{ZPL} - \hbar\omega) = \frac{1}{2\pi}\int_{-\infty}^{\infty}G(t)\exp(-i\omega t-\gamma|t|) dt, \qquad (Eq.7)
  ''')
  st.markdown(''' where $G(t)$ is the generating function of $G(t) = \exp(S(t) - S(0))$, and $\gamma$ is a fitting parameter. \\
  Then the time-dependent spectral function $S(t)$ is attained by
  ''')
  st.latex(r'''
  S(t) = \int_0^\infty S(\hbar\omega)\exp(-i\omega t)d(\hbar\omega), \qquad (Eq.8)
  ''')
  st.markdown(''' 
  where $S(\hbar\omega)$ is a *total* Huang-Rhys (HR) factor, which can be calculated from 
  ''')
  st.latex(r'''
  S(\hbar\omega) = \sum_k s_k\delta(\hbar\omega - \hbar\omega_k), \qquad (Eq.9)
  ''')
  st.markdown('''
  where $s_k$ is the *partial* HR factor for each phonon mode $k$, given by
  ''')
  st.latex(r'''
  s_k = \frac{\omega_k q_k^2}{2\hbar}, \qquad (Eq.10)
  ''')
  st.markdown('''
  where $q_k$ is the configuration coordinate, provided by the following expression
  ''')
  st.latex(r'''
  q_k = \sum_{\alpha,i}\sqrt{m_\alpha}\left(R_{e,\alpha i} - R_{g,\alpha i}\right)\Delta r_{k,\alpha i}. \qquad (Eq.11)
  ''')
  st.markdown('''
  α and $i$ run over the atomic species and the spatial coordinates $(x,y,z)$, respectively. $m_{α}$ is the \
  mass of atom species α. $R_g$ and $R_e$ are the stable atomic positions in the ground and excited states, respectively,\
   while $\Delta r_{k,αi}$ is the displacement vector of atom α at the phonon mode $k$ between the ground and excited states.
  ''')

  st.subheader("1.8 Quantum memory properties")
with st.container(border=False):
  st.markdown('''
    All quantum memory properties have been evaluated based on the off-resonant Raman protocol, which relies on the dynamics \
    in the $\Lambda$ electronic structures. For more details on the computational techniques and the data production of the \
    quantum memory properties, we refer the interested reader to the articles $[10,11]$
  ''')

st.header("2. Database acquisition")
with st.container(border=False):
  st.markdown('''
    $Figure. 1$ depicts the collection of this database. In the beginning, 158 impurities covering groups III-VI 
    and their complexes are created in the hBN monolayer. Their total spins are then determined by spin multiplicity: singlet, 
    doublet, and triplet. we found 95 out of 158 defects acting as triplet/singlet states under the neutral-charge state, \
    while the rest preferred the doublet state. For these doublet defects, they will be charged with $\pm 1$ charges. This \
    guarantees that every defect can behave as triplet and singlet configurations. The structures of both total spins are, \
    in turn, optimized, and this can be treated as a ground state. For an excited state, the electrons are manually occupied using \
    the $\Delta$SCF approach. Taking into account the electronic transitions separately, for instance, from spin up to up or from spin \
    down to down, this yields 257 triplet electronic structures for ground states, 257 triplet electronic structures for excited states,\
     and 211 singlet electronic structures for ground states. We note that only triplet states are considered for their excited states. \
     As a consequence, the properties can now be extracted by the methodology described above.
  ''')
  st.image('database_workflow_v5.png', caption="""Figure. 1 Flowchart of the DFT database acquisition. A DFT calculation was\
   initially performed to investigate hBN defects. After that, ground and excited photophysical properties over 257 \
   triplet transitions were extracted. Note that the symbol * denotes properties scheduled for future updates within \
   the database. """,width = 900)

st.header("3. Defect identification procedure")
with st.container(border=False):
  st.markdown('''
      The database offers multiple options for practical exploration of defect properties. For effective defect identification,\
       it is important to recognize the limitations of DFT to ensure promising defects are not inadvertently overlooked. Accordingly, \
       the step-by-step procedure is described below.

      1. One underlying experimental observation is the zero phonon line (the most prominent peak from the photoluminescence spectrum). \
      This property is directly accessible in the database; however, it is recommended to furnish a range rather than a specific value. \
      This entails conducting a search within a range of  $\pm$0.4 eV from the observed ZPL. The finite accuracy of DFT and residual strain \
      from the experiment justify this range, rendering it incompatible with the unstrained defects documented in the database.
      
      2. While the ZPL range serves as a reliable indicator, additional insights can be obtained from the fabrication technique as well. For instance, \
      if a defect is fabricated using ion implantation, we can infer certain defects based on the ions employed. Meanwhile, defects formed through the\
       use of a scanning electron microscope are inclined to be carbon-related defects emerging as a result.
      
      3. Then, we can further narrow down the potential defect candidates by considering other photophysical properties such \
      as lifetime, polarization orientation, etc. As explained earlier, the lifetime from DFT can be different from the experimental \
      value due to the purcell effect; however, the order of magnitude is still compatible.

      4. Comparing several parameters between the database and experiments is expected to yield the right defect promising for the experiment. The database \
      will be frequently updated with new defects and new defect properties. In addition, users can also request specific data (defects or properties) which \
      will be prioritized for the next update
    ''')

st.header("References")
with st.container(border=False):
  st.markdown('''
    1. [Kresse, Georg, and Jürgen Furthmüller. *"Efficiency of ab-initio total energy calculations for metals and \
    semiconductors using a plane-wave basis set."* Computational materials science 6, no. 1 (1996): \
    15-50.](https://www.sciencedirect.com/science/article/abs/pii/0927025696000080?via%3Dihub)
    2. [Kresse, Georg, and Jürgen Furthmüller. *"Efficient iterative schemes for ab initio total-energy calculations \
    using a plane-wave basis set."* Physical review B 54, no. 16 (1996): \
    11169.](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.54.11169)
    3. [Blöchl, Peter E. *"Projector augmented-wave method."* Physical review B 50, no. 24 (1994): \
    17953.](https://doi.org/10.1103/PhysRevB.50.17953)
    4. [Kresse, Georg, and Daniel Joubert. *"From ultrasoft pseudopotentials to the projector \
    augmented-wave method."* Physical review b 59, no. 3 (1999): 1758.](https://doi.org/10.1103/PhysRevB.59.1758)
    5. [Jones, Robert O., and Olle Gunnarsson. *"The density functional formalism, its applications and prospects."* \
    Reviews of Modern Physics 61, no. 3 (1989): 689.](https://link.aps.org/doi/10.1103/RevModPhys.61.689)
    6. [PyVaspwfc](https://github.com/liming-liu/pyvaspwfc)
    7. [Davidsson, Joel. *"Theoretical polarization of zero phonon lines in point defects."* Journal of Physics: \
    Condensed Matter 32, no. 38 (2020): 385502.](https://doi.org/10.1088/1361-648X/ab94f4)
    8. [Vogl, Tobias, Geoff Campbell, Ben C. Buchler, Yuerui Lu, and Ping Koy Lam. *"Fabrication and deterministic \
    transfer of high-quality quantum emitters in hexagonal boron nitride."* Acs Photonics 5, no. 6 (2018): 
    \2305-2312.](https://dx.doi.org/10.1021/acsphotonics.8b00127)
    9. [Vogl, Tobias, Marcus W. Doherty, Ben C. Buchler, Yuerui Lu, and Ping Koy Lam. *"Atomic localization of \
    quantum emitters in multilayer hexagonal boron nitride."* Nanoscale 11, no. 30 (2019): 
    \14362-14371.](https://doi.org/10.1039/C9NR04269E)
    10. [Cholsuk, Chanaprom, Aslı Çakan, Sujin Suwanna, and Tobias Vogl. *"Identifying electronic transitions of defects \
    in hexagonal boron nitride for quantum memories."* Advanced Optical Materials 12, (2024): \
    2302760.](https://doi.org/10.1002/adom.202302760)
    11. [Nateeboon, Takla, Chanaprom Cholsuk, Tobias Vogl, and Sujin Suwanna. *"Modeling the performance and bandwidth of \
    single-atom adiabatic quantum memories."* APL Quantum 1, no. 2 (2024): \
    026107.](https://doi.org/10.1063/5.0188597)
  ''')

st.write("--")

