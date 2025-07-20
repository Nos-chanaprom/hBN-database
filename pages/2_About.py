import streamlit as st

## Add background image
st.set_page_config(page_title="About",layout="wide")
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

st.title("About")
with st.container(border=False):
  st.markdown("""### Our paper
  Color centers in hexagonal boron nitride (hBN) have become an intensively researched system due to their potential\
   applications in quantum technologies. There has been a large variety of defects being fabricated, yet, for many of \
   them, the atomic origin remains unclear. The direct imaging of the defect is technically very challenging, in particular\
     since, in a diffraction-limited spot, there are many defects and then one has to identify the one that is optically\
     active. Another approach is to compare the photophysical properties with theoretical simulations and identify which \
     defect has a matching signature. It has been shown that a single property for this is insufficient and causes misassignments.\
      Here, we publish a density functional theory (DFT)-based searchable online database covering the electronic structure \
      of hBN defects (257 triplet and 211 singlet configurations), as well as their photophysical fingerprint (excited state lifetime,\
       quantum efficiency, transition dipole moment and orientation, polarization visibility, and many more). All data \
       is open-source and publicly accessible at https://h-bn.info and can be downloaded. It is possible to enter \
       the experimentally observed defect signature and the database will output possible candidates which can be narrowed\
        down by entering as many observed properties as possible. The database will be continuously updated with more defects \
        and new photophysical properties (which can also be specifically requested by any users). The database therefore \
        allows one to reliably identify defects but also investigate which defects might be promising for magnetic field \
         sensing or quantum memory applications.
  """)

with st.container(border=False):
  st.markdown("""### People
  This database is maintained by the [QCS group](https://www.ce.cit.tum.de/qcs/team/) at TUM 
  """) 

with st.container(border=False):
  st.subheader("How to cite")
  st.markdown('''
  For using any of the data, please cite: \n
    [Chanaprom Cholsuk, Ashkan Zand, Asli Cakan, Tobias Vogl, *"The hBN defects database: a theoretical compilation of color centers in hexagonal boron nitride."* The Journal of Physical Chemistry C, 2024, 128 (30), 12716.](https://doi.org/10.1021/acs.jpcc.4c03404) \n
    For specific properties of particular defects, please also cite the data originally published as follows:
  ''')
  st.markdown('''
  Quantum memory properties
  * [Cholsuk, Chanaprom, Aslı Çakan, Sujin Suwanna, and Tobias Vogl. *"Identifying electronic transitions of defects \
  in hexagonal boron nitride for quantum memories."* Advanced Optical Materials , 2024, 12, 2302760. \
  ](https://doi.org/10.1002/adom.202302760)
  ''')
  st.markdown('''
      Polarization dynamics properties for carbon-related defects
      * [Kumar, Anand, Caglar Samaner, Chanaprom Cholsuk, Tjorben Matthes, Serkan Paçal, Yagız Oyun, Ashkan Zand et al. \
      *"Polarization dynamics of solid-state quantum emitters."* ACS nano, 2024, 18 (7), 5270. \
      ](https://doi.org/10.1021/acsnano.3c08940)
      ''')
  st.markdown('''
      Photophysical properties
      * [Cholsuk, Chanaprom, Sujin Suwanna, and Tobias Vogl. *"Comprehensive scheme for identifying defects in solid-state \
      quantum systems."* The Journal of Physical Chemistry Letters, 2023, 14 (29), 6564. \
      ](https://doi.org/10.1021/acs.jpclett.3c01475)
      ''')


with st.container(border=False):
  st.markdown("""
  ### Contact details  
  For the feedback and requesting the feature functionality, please contact h-bn@qcs.cit.tum.de 
  """)

st.write("--")


