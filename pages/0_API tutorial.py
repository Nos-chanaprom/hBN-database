import streamlit as st
import requests # for API
import pandas as pd # for Table

## Add background image
st.set_page_config(page_title="Request data",layout="wide")
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

st.title("API tutorial")

with st.container(border=False):
    st.markdown("""
    To use our API, first, one needs to download the following `.py` file and place it in your working directory.
    """)

    url = "https://raw.githubusercontent.com/QCS-Theory/hBN-database/main/get_hBN_defects_database.py"
    response = requests.get(url)
    file_content = response.text

    st.download_button(
        label="Download get_hBN_defects_database.py",
        data=file_content,
        file_name="get_hBN_defects_database.py",
        mime="text/x-python"
    )

with st.container(border=False):
    st.markdown("""
    In your Python script or interactive session, import the function.  
    Invoke `get_database` with the desired filtering criteria as shown below:

    ```python
    from get_hBN_defects_database import get_database
    data = get_database(
        option=["ZPL"],
        host=["monolayer", "bulk"],
        spin_multiplicity=["singlet", "doublet", "triplet"],
        charge_state=[-2, -1, 0, 1, 2],
        optical_spin_transition=["up", "down"],
        value_range=(2.0, 4.0),
        download_db=False
    )
    ```

    **The keyword arguments perform the following functions:**

    - **`option`**:  
      Specifies which database columns to return. The complete set of valid keys is listed in Table below.  
      To retrieve all columns, use:

      ```python
      option = ["all"]
      ```

    - **`host`**:  
      Selects between the monolayer and bulk hBN datasets. By default, both are returned.

    - **`spin_multiplicity`**:  
      Filters defects by their spin multiplicity. If omitted, all multiplicities are included.

    - **`charge_state`**:  
      Filters defects by charge state. Defaults to all if unspecified.

    - **`optical_spin_transition`**:  
      Filters by optical spin transition (e.g., `"up"` refers up→up, and `"down"` refers down→down). Both are returned if not specified.

    - **`value_range`**:  
      Restricts the numeric range of the selected property. When omitted, no range filtering is applied.

    - **`download_db`**:  
      If set to `True`, downloads the raw SQLite database file (named like `hbn_defects_<options>.db`) to the working directory. However, one needs to specify the function as
       
    ```python
    from get_hBN_defects_database import get_database
    data, file_path = get_database(
        option=["all"],
        download_db=True
    )
    ```
    """)

    table_data = [
    ["Host", "TEXT: host material identifier", "-"],
    ["Defect", "TEXT: defect chemical formula/code", "-"],
    ["Defect name", "TEXT: descriptive name of the defect", "-"],
    ["Charge state", "INTEGER: integer charge state", "-"],
    ["Spin multiplicity", "TEXT: spin configuration of defects", "-"],
    ["Optical spin transition", "TEXT: allowed optical spin transition", "-"],
    ["Excitation properties: dipole_x (Debye)", "REAL: x-component of excitation dipole moment", "abs_dipole_x"],
    ["Excitation properties: dipole_y (Debye)", "REAL: y-component of excitation dipole moment", "abs_dipole_y"],
    ["Excitation properties: dipole_z (Debye)", "REAL: z-component of excitation dipole moment", "abs_dipole_z"],
    ["Excitation properties: linear In-plane Polarization Visibility", "REAL: Visibility", "abs_visibility"],
    ["Excitation properties: Intensity (Debye)", "REAL: Strength of excitation transition dipole moment", "abs_tdm"],
    ["Excitation properties: Characteristic time (ns)", "REAL: Time of excitation transition", "abs_lifetime"],
    ["Excitation properties: Angle of excitation wrt the crystal axis", "REAL: excitation polarization angle", "abs_angle"],
    ["Emission properties: dipole_x (Debye)", "REAL: x-component of emission dipole moment", "ems_dipole_x"],
    ["Emission properties: dipole_y (Debye)", "REAL: y-component of emission dipole moment", "ems_dipole_y"],
    ["Emission properties: dipole_z (Debye)", "REAL: z-component of emission dipole moment", "ems_dipole_z"],
    ["Emission properties: linear In-plane Polarization Visibility", "REAL: Visibility", "ems_visibility"],
    ["Emission properties: Intensity (Debye)", "REAL: Strength of emission transition dipole moment", "ems_tdm"],
    ["Emission properties: ZPL (eV)", "REAL: ZPL energy", "ZPL"],
    ["Emission properties: ZPL (nm)", "REAL: ZPL wavelength", "ZPL_nm"],
    ["Emission properties: lifetime (ns)", "REAL: Radiative lifetime of emission", "lifetime"],
    ["Emission properties: Angle of emission wrt the crystal axis", "REAL: emission polarization angle", "ems_angle"],
    ["Emission properties: Polarization misalignment (degree)", "REAL: dipole misalignment angle", "misalignment"],
    ["Emission properties: Configuration coordinate (amu^1/2/Å)", "REAL: Q value", "Q"],
    ["Emission properties: HR factor", "REAL: S value", "HR"],
    ["Emission properties: DW factor", "REAL: DW value", "DW"],
    ["Emission properties: Ground-state total energy (eV)", "REAL: total energy", "E_ground"],
    ["Emission properties: Excited-state total energy (eV)", "REAL: total energy", "E_excited"],
    ["Ground-state structure", "BLOB: atomic structure file (CIF file)", "structure_ground"],
    ["Excited-state structure", "BLOB: atomic structure file (CIF file)", "structure_excited"],
    ["Ground-state electronic structure", "BLOB: raw OUTCAR file (VASP format) for electronic structure", "band_ground"],
    ["Excited-state electronic structure", "BLOB: raw OUTCAR file (VASP format) for electronic structure", "band_excited"],
    ["PL lineshape", "BLOB: raw PL lineshape file with the broadening parameter (γ) equal to 1", "PL"]
    ]

    df = pd.DataFrame(table_data, columns=["Column name in .db file", "Type and description", "Option"])

    st.markdown("**Available `option` keys and database description**")
    st.dataframe(df, use_container_width=True)

    st.markdown(""" **Full code example**

    In this example, we demonstrate how to retrieve data for plotting a histogram of the ZPL values from both bulk and monolayer hBN defects.
    The retrieval is configured with the following criteria:
    - ZPL range: 1 to 5 eV
    - Spin transition: only spin-up optical transitions
    - Charge states included: −2, −1, 0, +1, and +2
    - Spin multiplicities considered: singlet, doublet, and triplet
    - Raw database file is not downloaded (download_db=False)
    - The filtered data can then be used to generate the desired histogram.

    ```python
    from get_hBN_defects_database import get_database
    import matplotlib.pyplot as plt

    data_ZPL = get_database(
        option=["ZPL"],
        host=["monolayer","bulk"], # Optional: if omitted, all host types are included
        spin_multiplicity=["singlet","doublet","triplet"], # Optional: includes all spin multiplicities if not specified
        charge_state=[-2, -1, 0, 1, 2],  # Optional: includes all charge states if not specified
        optical_spin_transition=["up"],
        value_range=(1,5),
        download_db=False
    )

    plt.hist(data_ZPL.iloc[:,6],bins=30, edgecolor='black')
    plt.xlabel("ZPL (eV)")
    plt.ylabel("Frequency")
    ```
    """)