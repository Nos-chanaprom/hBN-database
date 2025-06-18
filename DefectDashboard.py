import PIL
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import warnings
import time

### https://plotly.com/python/images/###

# Get the list of all files and directories 
# in the root directory
defects={}
path = "database_triplet"
defects_list = os.listdir(path)
defects_list.sort()
for defect in defects_list:
    path2 = path+"/"+defect
    charge_list = os.listdir(path2)
    defects[defect] = charge_list


## path for doublet singlet
# defectsDS={}
# pathDS = "database_doublet_single"
# defectsDS_list = os.listdir(pathDS)
# defectsDS_list.sort()
# for defect in defectsDS_list:
#     pathDS2 = pathDS+"/"+defect
#     spin_DS = os.listdir(pathDS2)
#     defectsDS[defect] = spin_DS
################################### WEB ##########################################
warnings.filterwarnings('ignore')

st.set_page_config(page_title="hBN Defects Database", page_icon=":atom_symbol:",layout="wide")

## Add background image
st.markdown(
    """
    <div class="banner">
        <img src="https://raw.githubusercontent.com/QCS-Theory/hBN-database/0f0c021bbd3b224390446c29651f97d3e6050e7f/icon/banner_file_size_3.svg" alt="Banner Image">
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

st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

with st.container(border=True):
    colp11, colp1,colp2,colp21, colp3,colp4,colp5,colp6 = st.columns(8, gap="small")
    with colp11:
        st.page_link("DefectDashboard.py", label="Main database")
    with colp1:
        st.page_link("pages/1_DFT calculation details.py", label="DFT calculation details")
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

css = '''
<style>
    [data-testid="stSidebar"]{
        min-width: 0px;   
        max-width: 0px;
    }
</style>
'''
### min-width and max-width for the sidebar is 230px in case we want to turn it on
st.markdown(css, unsafe_allow_html=True)


####################################################################################
####### START SEARCH ENGINE ########
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    df = df.copy()
    df.rename(columns={"Excitation properties: dipole_x":"Excitation properties: µₓ (Debye)",
                "Excitation properties: dipole_y":"Excitation properties: μᵧ (Debye)",
                "Excitation properties: dipole_z":"Excitation properties: µz (Debye)",
                "Excitation properties: Intensity":"Excitation properties: Intensity (Debye)",
                "Excitation properties: Angle of excitation dipole wrt the crystal axis":"Excitation properties: Angle of excitation dipole wrt the crystal axis (degree)",
                "Emission properties: dipole_x":"Emission properties: µₓ (Debye)",
                "Emission properties: dipole_y":"Emission properties: μᵧ (Debye)",
                "Emission properties: dipole_z":"Emission properties: µz (Debye)",
                "Emission properties: Intensity":"Emission properties: Intensity (Debye)",
                "Emission properties: Angle of emission dipole wrt the crystal axis":"Emission properties: Angle of emission dipole wrt the crystal axis (degree)"},inplace=True)
    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns.drop('Defect name'),['Defect','Emission properties: ZPL (eV)',
        'Emission properties: ZPL (nm)','Emission properties: Lifetime (ns)'])
        for column in to_filter_columns:
            # left, right = st.columns((1, 20))
            # left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = st.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                col001,col002=st.columns(2, gap="Small")
                with col001:
                    user_num_input_min = col001.number_input(
                        label = f"Min Values for {column}, Min: {_min}",
                        min_value = _min,
                        max_value = _max,
                        value =_min,
                        step=step,
                    )
                with col002:
                     user_num_input_max = col002.number_input(
                        label = f"Max Value for {column}, Max: {_max}",
                        min_value = _min,
                        max_value = _max,
                        value =_max,
                        step=step,
                    )
                df = df[df[column].between(*(user_num_input_min,user_num_input_max))]
            elif column == "Defect":
                user_text_input = st.text_input(
                    f"To find a defect, use the KrögerVink notation without indices *e.g. AsN for $As_N$*",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]
            elif column == "Excitation properties: Characteristic time (ns)" or "Emission properties: Lifetime (ns)" or "Quantum memory properties: Qualify factor at n =1.76 & Kappa = 0.05" or "Quantum memory properties: g (MHz)":
                df[column] = df[column].astype(float)
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                col001,col002=st.columns(2, gap="Small")
                with col001:
                    user_num_input_min = col001.number_input(
                        label = f"Min Values for {column}, Min: {_min}",
                        min_value = _min,
                        max_value = _max,
                        value =_min,
                        step=step,
                    )
                with col002:
                     user_num_input_max = col002.number_input(
                        label = f"Max Value for {column}, Max: {_max:.2E}",
                        min_value = _min,
                        max_value = _max,
                        value =_max,
                        step=step,
                    )
                df = df[df[column].between(*(user_num_input_min,user_num_input_max))]
                df[column] = df[column].map("{:.2E}".format)
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = st.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df

# with st.container(border=True):
#     st.markdown(
#         """
#         ### How to Use
#         - From "hBN defects Search Engine", find your defects by filttering the different parameters.
#         - In "Your selection" section, you will find your selected defect.
#         - All the Data related to the selected defects in "Your selection" section will be displayed automatically.
#         - The default defects are $Al_N$ and $Al_NP_B$
#     """
#     )
    

Search_cont = st.container(border=True)
with Search_cont:
    st.header("Search engine for hBN defects")
    Photophysical_properties = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='updated_data',engine = 'openpyxl',header=[0])
    ## rounding numbers
    Photophysical_properties.iloc[:,4:]=Photophysical_properties.iloc[:,4:].round(2)
    
    Photophysical_properties["Emission properties: ZPL (nm)"]=Photophysical_properties["Emission properties: ZPL (nm)"].astype(int)
    Photophysical_properties["Excitation properties: Characteristic time (ns)"]=Photophysical_properties["Excitation properties: Characteristic time (ns)"].astype(int)
    Photophysical_properties["Excitation properties: Characteristic time (ns)"] = Photophysical_properties["Excitation properties: Characteristic time (ns)"].map("{:.2E}".format)
    Photophysical_properties["Emission properties: Lifetime (ns)"]=Photophysical_properties["Emission properties: Lifetime (ns)"].astype(int)
    Photophysical_properties["Emission properties: Lifetime (ns)"] = Photophysical_properties["Emission properties: Lifetime (ns)"].map("{:.2E}".format)
    Photophysical_properties["Quantum memory properties: Qualify factor at n =1.76 & Kappa = 0.05"]=Photophysical_properties["Quantum memory properties: Qualify factor at n =1.76 & Kappa = 0.05"].astype(int)
    Photophysical_properties["Quantum memory properties: Qualify factor at n =1.76 & Kappa = 0.05"] = Photophysical_properties["Quantum memory properties: Qualify factor at n =1.76 & Kappa = 0.05"].map("{:.2E}".format)
    Photophysical_properties["Quantum memory properties: g (MHz)"]=Photophysical_properties["Quantum memory properties: g (MHz)"].astype(int)
    Photophysical_properties["Quantum memory properties: g (MHz)"] = Photophysical_properties["Quantum memory properties: g (MHz)"].map("{:.2E}".format)
   
    Photophysical_properties['Defect name']=Photophysical_properties['Defect name'].map(lambda x: "${}$".format(x.replace("$","")))
    df_searchEngine = filter_dataframe(Photophysical_properties)

    ### Selected Table ####
    def dataframe_with_selections(df):
        df_with_selections = df.copy()
        df_with_selections.insert(0, "Select", False)

        # Get dataframe row-selections from user with st.data_editor
        edited_df = st.data_editor(
            df_with_selections,
            hide_index=True,
            column_config={"Select": st.column_config.CheckboxColumn(required=True), "Defect name": None},
            disabled=df.columns,
        )

        # Filter the dataframe using the temporary column, then drop the column
        selected_rows = edited_df[edited_df.Select]
        return selected_rows


    selection = dataframe_with_selections(df_searchEngine)
    st.write("Your selection:")
    selection_selection = st.data_editor(
            selection,
            hide_index=True,
            column_config={"Select": None,"Defect name": None},
            disabled=selection.columns
        )

####### END SEARCH ENGINE ########
if selection.empty :
    ele1 = Photophysical_properties[Photophysical_properties['Defect']=="AlN"]
    ele2 = Photophysical_properties[Photophysical_properties['Defect']=="AlNPB"]
    ele12 = pd.concat([ele1,ele2])

    chosen_defect = ele12.loc[:,'Defect']
    chosen_defect_m = chosen_defect.reset_index().drop("index", axis='columns')

    chargestate_defect = ele12.loc[:,'Charge state']
    chargestate_defect_m = chargestate_defect.reset_index().drop("index", axis='columns')

    spin_transition = ele12.loc[:,'Optical spin transition']
    spin_transition_m = spin_transition.reset_index().drop("index", axis='columns')

    spin_multiplicity = ele12.loc[:,"Spin multiplicity"]
    spin_multiplicity_m = spin_multiplicity.reset_index().drop("index", axis='columns')

    chosenlist = ele12.loc[:,['Defect','Charge state','Optical spin transition','Spin multiplicity']].to_numpy()
else:
    chosen_defect = selection.loc[:,'Defect']
    chosen_defect_m = chosen_defect.reset_index().drop("index", axis='columns')
    
    chargestate_defect = selection.loc[:,'Charge state']
    chargestate_defect_m = chargestate_defect.reset_index().drop("index", axis='columns')
    
    spin_transition = selection.loc[:,'Optical spin transition']
    spin_transition_m = spin_transition.reset_index().drop("index", axis='columns')

    spin_multiplicity = selection.loc[:,"Spin multiplicity"]
    spin_multiplicity_m = spin_multiplicity.reset_index().drop("index", axis='columns')
    
    chosenlist = selection.loc[:,['Defect','Charge state','Optical spin transition','Spin multiplicity']].to_numpy()

selection_str =[]
for ele in chosenlist:
    selection_str.append(ele[0] + " (charge state: " +str(ele[1]) + ", " +ele[2] +", " + str(ele[3])+")")
tab_selection = st.tabs(selection_str)
tabs_index =0
for tabs in tab_selection:
    with tabs:
        str_defect = chosen_defect_m.iloc[tabs_index,0]
        chargestate_defect = chargestate_defect_m.iloc[tabs_index,0]
        spin_transition = spin_transition_m.iloc[tabs_index,0]
        spin_multiplicity = spin_multiplicity_m.iloc[tabs_index,0]

        try: 
            name_change = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='updated_data',engine = 'openpyxl')
            latexdefect = name_change[name_change['Defect']==str_defect]['Defect name'].reset_index().iloc[0,1]
            latexdefect = latexdefect.replace("$","")

        except IndexError:
            latexdefect = str_defect
        ##############################33 Singlet Doublet #################################    
        if spin_multiplicity == 'singlet'or spin_multiplicity == 'doublet':

            ### Ground Sate
            band_energy_spinUp_filled_triplet = []
            band_energy_spinUp_unfilled_triplet = []
            band_energy_spinDown_filled_triplet = []
            band_energy_spinDown_unfilled_triplet = []
            fermi_energy_triplet = ['0','0']

            ### Excited State
            band_energy_spinUp_filled_excited_triplet = []
            band_energy_spinUp_unfilled_excited_triplet = []
            band_energy_spinDown_filled_excited_triplet = []
            band_energy_spinDown_unfilled_excited_triplet = []
            fermi_energy_excited_triplet = ['0','0']

            if spin_multiplicity == 'singlet':
                triplet_path = "database_doublet_single/" + str_defect + "/singlet/ground/output_database.txt"
                excited_triplet_path= "database_doublet_single/" + str_defect + "/singlet/excited/output_database.txt"

                atomposition_triplet = "database_doublet_single/" + str_defect + "/singlet/ground/CONTCAR_cartesian"
                atomposition_excited_triplet = "database_doublet_single/" + str_defect + "/singlet/excited/CONTCAR_cartesian"

                fractional_triplet = "database_doublet_single/" + str_defect + "/singlet/ground/CONTCAR_fractional"
                fractional_excited_triplet = "database_doublet_single/" + str_defect + "/singlet/excited/CONTCAR_fractional"

                cif_triplet = "database_doublet_single/" + str_defect + "/singlet/ground/structure.cif"
                cif_excited_triplet = "database_doublet_single/" + str_defect + "/singlet/excited/structure.cif"

            elif spin_multiplicity == 'doublet':
                triplet_path = "database_doublet_single/" + str_defect + "/doublet/ground/output_database.txt"
                excited_triplet_path= "database_doublet_single/" + str_defect + "/doublet/excited/output_database.txt"

                atomposition_triplet = "database_doublet_single/" + str_defect + "/doublet/ground/CONTCAR_cartesian"
                atomposition_excited_triplet = "database_doublet_single/" + str_defect + "/doublet/excited/CONTCAR_cartesian"

                fractional_triplet = "database_doublet_single/" + str_defect + "/doublet/ground/CONTCAR_fractional"
                fractional_excited_triplet = "database_doublet_single/" + str_defect + "/doublet/excited/CONTCAR_fractional"

                cif_triplet = "database_doublet_single/" + str_defect + "/doublet/ground/structure.cif"
                cif_excited_triplet = "database_doublet_single/" + str_defect + "/doublet/excited/structure.cif"
            
            ### Ground State ###
            df = pd.read_fwf(triplet_path, sep=" ",header=None)  

            band_energy_spinUp_filled_triplet = []
            band_energy_spinUp_unfilled_triplet = []
            band_energy_spinDown_filled_triplet = []
            band_energy_spinDown_unfilled_triplet = []
            fermi_energy_triplet = []
            for row in range(0,512,1):
                if row == 0 or row == 256:
                    df2 = df.iloc[row,0].split(" ")
                    df_row = [ele for ele in df2 if ele.strip()]
                    fermi_energy_triplet.append(df_row[2])
                elif row > 3 and row < 256: 
                    df2 = df.iloc[row,0].split(" ")
                    df_row = [ele for ele in df2 if ele.strip()]
                    if round(float(df_row[2])) == 1 :
                        band_energy_spinUp_filled_triplet.append(float(df_row[1]))
                    elif round(float(df_row[2])) == 0:
                        band_energy_spinUp_unfilled_triplet.append(float(df_row[1]))
                elif row > 259: 
                    df2 = df.iloc[row,0].split(" ")
                    df_row = [ele for ele in df2 if ele.strip()]
                    if round(float(df_row[2])) == 1 :
                        band_energy_spinDown_filled_triplet.append(float(df_row[1]))
                    elif round(float(df_row[2])) == 0:
                        band_energy_spinDown_unfilled_triplet.append(float(df_row[1]))

            ### Excited State ###
            df = pd.read_fwf(excited_triplet_path, sep=" ",header=None)  

            band_energy_spinUp_filled_excited_triplet = []
            band_energy_spinUp_unfilled_excited_triplet = []
            band_energy_spinDown_filled_excited_triplet = []
            band_energy_spinDown_unfilled_excited_triplet = []
            fermi_energy_excited_triplet_path = []
            for row in range(0,512,1):
                if row == 0 or row == 256:
                    df2 = df.iloc[row,0].split(" ")
                    df_row = [ele for ele in df2 if ele.strip()]
                    fermi_energy_excited_triplet.append(df_row[2])
                elif row > 3 and row < 256: 
                    df2 = df.iloc[row,0].split(" ")
                    df_row = [ele for ele in df2 if ele.strip()]
                    if round(float(df_row[2])) == 1 :
                        band_energy_spinUp_filled_excited_triplet.append(float(df_row[1]))
                    elif round(float(df_row[2])) == 0:
                        band_energy_spinUp_unfilled_excited_triplet.append(float(df_row[1]))
                elif row > 259: 
                    df2 = df.iloc[row,0].split(" ")
                    df_row = [ele for ele in df2 if ele.strip()]
                    if round(float(df_row[2])) == 1 :
                        band_energy_spinDown_filled_excited_triplet.append(float(df_row[1]))
                    elif round(float(df_row[2])) == 0:
                        band_energy_spinDown_unfilled_excited_triplet.append(float(df_row[1]))

            fermi_energy_triplet = [float(i) for i in fermi_energy_triplet]
            fermi_energy_excited_triplet = [float(i) for i in fermi_energy_excited_triplet]

            spin_nummer = 4

            try: 
                upfreiplet = np.array(band_energy_spinUp_filled_triplet)
                upfreipletexc = np.array(band_energy_spinUp_filled_excited_triplet)

                upunfreiplet = np.array(band_energy_spinDown_unfilled_triplet)
                upunfreipletexc = np.array(band_energy_spinUp_unfilled_excited_triplet)

                triplet_ref = upfreiplet[upfreiplet < -5][-1]
                excited_triplet_ref = upfreipletexc[upfreipletexc < -5][-1] 

                tripletunf_ref = upunfreiplet[upunfreiplet > 1][0]
                excited_triplet_ref = upunfreipletexc[upunfreipletexc > 1][0]

            except IndexError:
                triplet_ref =-5
                excited_triplet_ref = -5

                tripletunf_ref = 1
                excited_triplet_ref = 1


            fup_t = [energy - triplet_ref for energy in band_energy_spinUp_filled_triplet[-spin_nummer:]]
            ufup_t = [energy - triplet_ref for energy in band_energy_spinUp_unfilled_triplet[:spin_nummer]]
            fdown_t = [energy - triplet_ref for energy in band_energy_spinDown_filled_triplet[-spin_nummer:]]
            ufdown_t = [energy - triplet_ref for energy in band_energy_spinDown_unfilled_triplet[:spin_nummer]]

            fup_t_exc = [energy - triplet_ref for energy in band_energy_spinUp_filled_excited_triplet[-spin_nummer:]]
            ufup_t_exc = [energy - triplet_ref for energy in band_energy_spinUp_unfilled_excited_triplet[:spin_nummer]]
            fdown_t_exc = [energy - triplet_ref for energy in band_energy_spinDown_filled_excited_triplet[-spin_nummer:]]
            ufdown_t_exc = [energy - triplet_ref for energy in band_energy_spinDown_unfilled_excited_triplet[:spin_nummer]]

            all_band_energy = np.concatenate([fup_t_exc,fup_t,ufup_t,ufup_t_exc,fdown_t,fdown_t_exc,ufdown_t,ufdown_t_exc])

            try:
                eemin = np.min(all_band_energy)
                eemax = np.max(all_band_energy)
            except ValueError:  #raised if `y` is empty.
                eemin =0
                eemax =6

            def spin_marker_exc_fig (spinstate, band_energy, size, xcor, e_ref , bandlimit ,emin, emax,fig):
                fig2=fig
                scale =32
                delta = 0
                emin = emin
                emax = emax
                if spinstate == 'fup':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band+size/2,band+size/2-size/3,band+size/2-size/3,
                                            band,band,band-size/12,band-size/12,
                                            band-size/2,band-size/2,
                                            band-size/12,band-size/12,band,band,
                                            band+size/2-size/3,band+size/2-size/3,band+size/2])

                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow, fill="toself",mode='lines',opacity=1, fillcolor= 'black',
                                                name=r'{}'.format(band)))
                        fig2.add_shape(type="rect",x0=0, y0=0, x1=1, y1=-1+emin,fillcolor='rgb(116, 167, 200)', layer="below")

                        delta += 0.02

                elif spinstate == 'fdown':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)            
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band-size/2,band-size/2+size/3,band-size/2+size/3,
                                            band,band,band+size/12,band+size/12,
                                            band+size/2,band+size/2,
                                            band+size/12,band+size/12,band,band,
                                            band-size/2+size/3,band-size/2+size/3,band-size/2])            
                        
                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow, fill="toself",mode='lines', opacity=1, fillcolor= 'black',
                                                name=r'{}'.format(band)))
                        #fig2.add_shape(type="rect",x0=xcor+0.1, y0=-5-fermi_energy, x1=xcor-0.15, y1=-1+emin,fillcolor="Blue",opacity=0.1)

                        delta += 0.02

                elif spinstate == 'ufup':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band+size/2,band+size/2-size/3,band+size/2-size/3,
                                            band,band,band-size/12,band-size/12,
                                            band-size/2,band-size/2,
                                            band-size/12,band-size/12,band,band,
                                            band+size/2-size/3,band+size/2-size/3,band+size/2])
                        
                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow,mode='lines', fill="toself",opacity=1, fillcolor= 'white',
                                                name=r'{}'.format(band)))
                        fig2.add_shape(type="rect",x0=0, y0=bandlimit-e_ref, x1=1, y1=1+emax,fillcolor= 'rgb(237, 140, 140)', layer="below")

                        delta += 0.02

                elif spinstate == 'ufdown':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band-size/2,band-size/2+size/3,band-size/2+size/3,
                                            band,band,band+size/12,band+size/12,
                                            band+size/2,band+size/2,
                                            band+size/12,band+size/12,band,band,
                                            band-size/2+size/3,band-size/2+size/3,band-size/2])

                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow,mode='lines',fill="toself",opacity=1, fillcolor= 'white',
                                                name=r'{}'.format(band)))
                        
                        #fig2.add_shape(type="rect",x0=xcor+0.1, y0=1-fermi_energy, x1=xcor-0.15, y1=1+emax,fillcolor="red",opacity=0.1)

                        delta += 0.02

            fig = go.Figure()
            
            spin_marker_exc_fig ('fup', fup_t, size=0.5, xcor=0.3,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig)
            spin_marker_exc_fig ('ufup', ufup_t, size=0.5, xcor=0.3, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig)
            spin_marker_exc_fig ('fdown', fdown_t, size=0.5, xcor=0.7,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig)
            spin_marker_exc_fig ('ufdown', ufdown_t, size=0.5, xcor=0.7, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig)
            
            fig2 = go.Figure()
            
            spin_marker_exc_fig ('fup', fup_t_exc, size=0.5, xcor=0.3,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig2)
            spin_marker_exc_fig ('ufup', ufup_t_exc, size=0.5, xcor=0.3, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig2)
            spin_marker_exc_fig ('fdown', fdown_t_exc, size=0.5, xcor=0.7,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig2)
            spin_marker_exc_fig ('ufdown', ufdown_t_exc, size=0.5, xcor=0.7, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax,fig=fig2)
            #### Figures and tables
            fig.update_xaxes(
                    title_font = {"size": 30},
                    showgrid=False,
                    range=[0, 1],
                    showticklabels=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True
                    )

            fig.update_yaxes(
                    title_font = {"size": 20},
                    showgrid=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True,
                    )

            #### Figures and tables
            fig2.update_xaxes(
                    title_font = {"size": 30},
                    showgrid=False,
                    range=[0, 1],
                    showticklabels=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True
                    )

            fig2.update_yaxes(
                    title_font = {"size": 20},
                    showgrid=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True,
                    )

            try: 
                name_change = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='updated_data',engine = 'openpyxl')
                latexdefect = name_change[name_change['Defect']==str_defect]['Defect name'].reset_index().iloc[0,1]
                latexdefect = latexdefect.replace("$","")

            except IndexError:
                latexdefect = str_defect

            fig2.update_layout(showlegend=False, 
                            xaxis_title=r"${}$".format(latexdefect),
                            yaxis_title=r"$E(eV)$ ",
                            font=dict(size=18,color="Black")
                            )

            fig.update_layout(showlegend=False, 
                            xaxis_title=r"${}$".format(latexdefect),
                            yaxis_title=r"$E(eV)$ ",
                            font=dict(size=18,color="Black")
                            )


            col1, col2 = st.columns(2,gap ="small")#st.columns([0.5,0.5])
            with col1:
                with st.container(border=True):
                    st.header('Kohn-Sham electronic transition')
                    tab1, tab2 = st.tabs(["Ground State","Excited State"])
                    with tab1:                
                        st.components.v1.html(fig.to_html(include_mathjax='cdn'),width=530, height=600)
                    with tab2: 
                        st.components.v1.html(fig2.to_html(include_mathjax='cdn'),width=530, height=600)
            with col2:
                with st.container(border=True):
                    ########################## atomic position data frame  ###################################
                    if  type(chosen_defect) == str:
                        latexdefect = 'Al_N'
                        atomicposition_sin = pd.read_csv("database_triplet/" + 'AlN' + "/triplet/CONTCAR_cartesian",sep=';', header=0)        
                    else:
                        try: 
                            atomicposition_sin = pd.read_csv(atomposition_triplet,sep=';', header=0)
                        except NameError or ValueError:
                            latexdefect = 'Al_N'
                            atomicposition_sin = pd.read_csv("database_triplet/" + str_defect + "/triplet/CONTCAR_cartesian",sep=';', header=0)
                    atomicposition = pd.DataFrame(columns = ['properties', 'X','Y','Z'])
                    for row in range(atomicposition_sin.shape[0]):
                        if 0 <row<4:
                            df2 = atomicposition_sin.iloc[row,0].split(" ")
                            df_row = [ele for ele in df2 if ele.strip()]
                            atomicposition.loc[row,['X','Y','Z']] = df_row
                    atomicposition.loc[1:4,'properties'] = ['Lattice a', 'Lattice b', 'Lattice c']
                    ##
                    iindex =0
                    startind =6
                    dataframeind = 3
                    letternumber =[[ele for ele in atomicposition_sin.iloc[4,0].split(" ") if ele.strip()],
                                [ele for ele in atomicposition_sin.iloc[5,0].split(" ") if ele.strip()]]
                    bnnumber=[]
                    for num in letternumber[1]:
                        letter =letternumber[0][iindex]
                        numnum = int(num)
                        bnnumber.append(numnum)
                        for element in range(1,numnum+1):
                            startind =startind+1
                            dataframeind= dataframeind+1     
                            df2 = atomicposition_sin.iloc[startind,0].split(" ")
                            df_row = [ele for ele in df2 if ele.strip()]
                            atomicposition.loc[dataframeind,['X','Y','Z']] = df_row[0:3]
                            atomicposition.loc[dataframeind,'properties'] = '{}-{}'.format(letter,element)
                        iindex+=1
                    
                    atomicposition.loc[:,['X','Y','Z']]=atomicposition.loc[:,['X','Y','Z']].astype(float).round(decimals=5)

                    #### plot atomic bonds
                    st.header("Atomic positions for a ground triplet state (${}$)".format(latexdefect))    
                    fig3D = go.Figure()
                    i=0
                    letters=letternumber[0]
                    numbers=letternumber[1]

                    numcounter=0
                    indexcounter=3
                    atomsize=6
                    for ele in letters:
                        if ele == 'B':
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele,marker=dict( size=atomsize, color='rgb(255,147,150)')))
                        elif ele == 'C':
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele,marker=dict(size=atomsize,color='rgb(206,0,0)')))
                        elif ele == 'N':
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele, marker=dict(size=atomsize,color='rgb(0,0,255)')))
                        else:
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele, marker=dict( size=atomsize)))
                        numcounter+=1
                        indexcounter=indexcounter+numberint

                    ## atome bonds
                    atoms= atomicposition.iloc[3:]
                    for ele in atoms['properties']:
                        if  list(ele)[0] =='B':
                            ele_loc=atoms[atoms['properties'] == ele]
                            ele_index=ele_loc.index
                            other= atoms.drop(ele_index)
                            other.iloc[:,1:4]=other.iloc[:,1:4]-atoms.iloc[ele_index[0]-4,1:4]
                            other['norm'] = other.iloc[:,1:4].apply(lambda x: x **2).apply(np.sum, axis=1)
                            near_atom_diff= other.sort_values(by=['norm'],ascending=True)
                            near_atom_diff=near_atom_diff[near_atom_diff["norm"]<3]
                            near_atom_1=atoms.iloc[near_atom_diff.index-4]
                            near_atom_2=near_atom_1.copy()
                            near_atom_2['element'] = near_atom_2['properties'].map(lambda x:  list(x)[0])
                            near_atom_3=near_atom_2[near_atom_2['element']== 'N']
                            near_atom=atoms.iloc[near_atom_3.index-4].iloc[0:3]
                            tail=ele_loc.to_numpy()
                            head=near_atom.to_numpy()
                            for i in range(0,near_atom.shape[0]):
                                fig3D.add_trace(go.Scatter3d(x=[tail[0,1],head[i,1]], y=[tail[0,2],head[i,2]],z=[tail[0,3],head[i,3]],hoverinfo ='skip', mode='lines', line=dict(color='black',width=5),showlegend=False))


                    ## dipole
                    dipole = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='updated_data',engine = 'openpyxl',header=[0])
                    try: 
                        dipole_emi = dipole[(dipole['Defect'] == str_defect) & (dipole['Charge state'] ==chargetrans[str_charge]) & (dipole['Optical spin transition'] == spin_transition)]
                    except  NameError :
                        dipole_emi = dipole[dipole['Defect'] == str_defect]
                    except  KeyError:
                        dipole_emi = dipole[dipole['Defect'] == str_defect]

                    tail_emi_plane = dipole_emi['Emission properties: linear In-plane Polarization Visibility'].values[0]
                    tail_emi_cry = dipole_emi['Emission properties: Angle of emission dipole wrt the crystal axis'].values[0]
                    tail_exc_plane = dipole_emi['Excitation properties: linear In-plane Polarization Visibility'].values[0]
                    tail_exc_cry = dipole_emi['Excitation properties: Angle of excitation dipole wrt the crystal axis'].values[0]
                    
                    ctrystal_axes_start = np.array([3.736,7.960,1.668])
                    ctrystal_axes_start2=np.array([3.736,3.960,1.668])
                    ctrystal_axes_end = np.array([3.736,11.960,1.668])-ctrystal_axes_start

                    theta_emi =  np.radians((1-tail_emi_plane)*90)
                    #theta_emi =  np.radians(90)
                    theta_exc =  np.radians((1-tail_exc_plane)*90)

                    phi_emi = np.radians(tail_emi_cry)
                    #phi_emi =np.radians(0)
                    phi_exc = np.radians(tail_exc_cry)

                    ## ploting Emission Dipole
                    # rotate z-axis
                    c, s = np.cos(phi_emi), np.sin(phi_emi)
                    r_z = np.array(((c,-s,0), (s,c,0), (0,0,1)))
                    # rotate x-axis
                    c, s = np.cos(theta_emi), np.sin(theta_emi)
                    r_x = np.array(((1,0,0), (0,c, -s), (0,s, c)))

                    r_xz=np.dot(r_x,r_z)
                    head = np.dot(r_xz,ctrystal_axes_end)  #ctrystal_axes_end
                    tail=np.array([3.736,7.960,1.668])

                    head=head+ctrystal_axes_start
                    ctrystal_axes_end= ctrystal_axes_end+ctrystal_axes_start        

                    fig3D.add_trace(go.Cone(x=[head[0]], y=[head[1]], z=[head[2]], u=[head[0]-tail[0]], v=[head[1]-tail[1]], w=[head[2]-tail[2]],
                                            colorscale='ylorrd',showscale=False,hoverinfo='skip',sizeref=0.2))
                    fig3D.add_trace(go.Scatter3d(x=[tail[0],head[0]], y=[tail[1],head[1]],z=[tail[2],head[2]],hoverinfo ='skip',marker=dict(size=3, color='yellow'),
                                                line=dict(color='orange',width=6),showlegend=True,name="Emission"))
                    fig3D.add_trace(go.Scatter3d(x=[ctrystal_axes_start2[0],ctrystal_axes_end[0]], y=[ctrystal_axes_start2[1],ctrystal_axes_end[1]],z=[ctrystal_axes_start2[2],ctrystal_axes_end[2]],
                                                hoverinfo ='skip', marker=dict(size=1, color='red'), line=dict(color='red',width=5,dash='dot'),showlegend=True,name="Crystal Axis"))
                    
                    ## ploting Excitation Dipole
                    ctrystal_axes_end = np.array([3.736,11.960,1.668])-ctrystal_axes_start
                    # rotate z-axis
                    c, s = np.cos(phi_exc), np.sin(phi_exc)
                    r_z = np.array(((c,-s,0), (s,c,0), (0,0,1)))
                    # rotate x-axis
                    c, s = np.cos(theta_exc), np.sin(theta_exc)
                    r_x = np.array(((1,0,0), (0,c, -s), (0,s, c)))

                    r_xz=np.dot(r_x,r_z)
                    head = np.dot(r_xz,ctrystal_axes_end)  #ctrystal_axes_end
                    tail=np.array([3.736,7.960,1.668])

                    head=head+ctrystal_axes_start
                    ctrystal_axes_end= ctrystal_axes_end+ctrystal_axes_start        

                    fig3D.add_trace(go.Cone(x=[head[0]], y=[head[1]], z=[head[2]], u=[head[0]-tail[0]], v=[head[1]-tail[1]], w=[head[2]-tail[2]],
                                            colorscale='Greens',showscale=False,hoverinfo='skip',sizeref=0.2))
                    fig3D.add_trace(go.Scatter3d(x=[tail[0],head[0]], y=[tail[1],head[1]],z=[tail[2],head[2]],hoverinfo ='skip',marker=dict(size=3, color='green'),
                                                line=dict(color='green',width=6),showlegend=True,name="Excitation"))

                    fig3D.update_layout(scene = dict( zaxis = dict( range=[0,25],showgrid=False, backgroundcolor="rgb(0,0,0)",gridcolor="rgb(0,0,0)",zeroline=False,showticklabels =False,title =' '), 
                                                    yaxis = dict(showgrid=False,backgroundcolor="rgb(0,0,0)",gridcolor="rgb(0,0,0)",zeroline=False,showticklabels =False,title =' '), 
                                                    xaxis = dict(showgrid=False,backgroundcolor="rgb(0,0,0)",gridcolor="rgb(0,0,0)",zeroline=False,showticklabels =False,title =' '), 
                                                    camera_eye=dict(x=0, y=0, z=0.8))
                    )
                    st.plotly_chart(fig3D, use_container_width=True)
                    ### download data
                    with st.container(border=False):
                        st.header("Download data")
                        cold1, cold2,cold3  = st.columns(3,gap="Small")
                        with cold1:
                            st.download_button(
                                label="VASP cartesian ground-state",
                                data= open(atomposition_triplet, "r"),
                                file_name=f'VASP cartesian ground-state-{str_defect}'
                            )
                            st.download_button(
                                label="VASP cartesian excited-state",
                                data= open(atomposition_excited_triplet, "r"),
                                file_name=f'VASP cartesian excited-state-{str_defect}'
                            )
                        with cold2:
                            st.download_button(
                                label="VASP fractional ground-state",
                                data= open(fractional_triplet, "r"),
                                file_name=f'VASP fractional  ground-state-{str_defect}'
                            )
                            st.download_button(
                                label="VASP fractional excited-state",
                                data= open(fractional_excited_triplet, "r"),
                                file_name=f'VASP fractional excited-state-{str_defect}'
                            )
                        with cold3:
                            st.download_button(
                                label="CIF ground-state",
                                data= open(cif_triplet, "r"),
                                file_name=f'CIF ground-state-{str_defect}.cif'                
                            )
                            st.download_button(
                                label="CIF excited-sate",
                                data= open(cif_excited_triplet, "r"),
                                file_name=f'CIF excited-sate-{str_defect}.cif'                
                            )


            col3, col4 = st.columns(2,gap="medium")
            with col3:
                with st.container(border=True):
                    st.header("Photophysical properties of "+"${}$".format(latexdefect))
                    # col21, col22, col23 = st.columns(3)
                    tab1, tab2, tab3 = st.tabs(["Excitation Properties", "Emission Properties", "Quantum Memory Properties"])
                    ## col21
                    #tab1.subheader('Excitation Properties')
                    Photophysical_properties = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='Excitation properties',engine = 'openpyxl',header=[0])
                    Photophysical_properties.iloc[:,4:]=Photophysical_properties.iloc[:,4:].round(2)
                    Photophysical_properties["Characteristic time (ns)"]=Photophysical_properties["Characteristic time (ns)"].astype(int)
                    Photophysical_properties["Characteristic time (ns)"] = Photophysical_properties["Characteristic time (ns)"].map("{:.2E}".format)

                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])]
                    except  NameError :
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    except  KeyError:
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    ep2=ppdefects.iloc[:,3:]
                    ep2.rename(columns={"dipole_x":"µₓ (Debye)","dipole_y":"μᵧ (Debye)","dipole_z":"µz (Debye)","Intensity":"Intensity (Debye)","Angle of excitation dipole wrt the crystal axis":"Angle of excitation dipole wrt the crystal axis (degree)"},inplace=True)
                    ep2=ep2.T
                    jj =1
                    newheadcol =[]
                    #latppdefects.iloc[1,0].replace("$","")
                    for head in ep2.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    ep2.columns =newheadcol
                    tab1.dataframe(ep2,use_container_width=True)

                    ## col22
                    #col22.subheader('Emission Properties')

                    Photophysical_properties = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='Emission properties',engine = 'openpyxl',header=[0])
                    Photophysical_properties.iloc[:,4:]=Photophysical_properties.iloc[:,4:].round(2)
                    Photophysical_properties["ZPL (nm)"]=Photophysical_properties["ZPL (nm)"].astype(int)
                    Photophysical_properties["Lifetime (ns)"]=Photophysical_properties["Lifetime (ns)"].astype(int)
                    Photophysical_properties["Lifetime (ns)"] = Photophysical_properties["Lifetime (ns)"].map("{:.2E}".format)
                    Photophysical_properties["Configuration coordinate (amu^(1/2) \AA)"]=Photophysical_properties["Configuration coordinate (amu^(1/2) \AA)"]
                    Photophysical_properties["Ground-state total energy (eV)"]=Photophysical_properties["Ground-state total energy (eV)"]
                    Photophysical_properties["Excited-state total energy (eV)"]=Photophysical_properties["Excited-state total energy (eV)"]

                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])]
                    except  NameError :
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    except  KeyError:
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    emp=ppdefects.iloc[:,3:]
                    emp.rename(columns={"dipole_x":"µₓ (Debye)","dipole_y":"μᵧ (Debye)","dipole_z":"µz (Debye)","Intensity":"Intensity (Debye)","Angle of emission dipole wrt the crystal axis":"Angle of emission dipole wrt the crystal axis (degree)","Configuration coordinate (amu^(1/2) \AA)":"Configuration coordinate (amu^(1/2) Å)","Ground-state total energy (eV)":"Ground-state total energy (eV)","Excited-state total energy (eV)":"Excited-state total energy (eV)"},inplace=True)
                    emp=emp.T
                    jj =1
                    newheadcol =[]
                    #latppdefects.iloc[1,0].replace("$","")
                    for head in emp.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    emp.columns =newheadcol
                    tab2.dataframe(emp,use_container_width=True)
                    
                    #col23
                    #col23.subheader('Quantum Memory Properties')
                    Photophysical_properties = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='Quantum memory properties',engine = 'openpyxl',header=[0])
                    Photophysical_properties.iloc[:,4:]=Photophysical_properties.iloc[:,4:].round(2)
                    Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"]=Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].astype(int)
                    Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"] = Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].map("{:.2E}".format)
                    Photophysical_properties["g (MHz)"]=Photophysical_properties["g (MHz)"].astype(int)
                    Photophysical_properties["g (MHz)"] = Photophysical_properties["g (MHz)"].map("{:.2E}".format)
                
                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])]
                    except  NameError :
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    except  KeyError:
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    qmp = ppdefects.iloc[:,3:]
                    qmp=qmp.T
                    jj =1
                    newheadcol =[]
                    #latppdefects.iloc[1,0].replace("$","")
                    for head in qmp.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    qmp.columns =newheadcol
                    tab3.dataframe(qmp,use_container_width=True)
            with col4:
                with st.container(border=True):
                    st.header('Computational setting')
                    df = pd.DataFrame(
                        {
                            "Computational Setting": ["DFT calculator", "Functional", "Pseudopotentials","Cutoff Energy","Kpoint",
                                                    "Supercell size", "Energy convergence","Force convergence","Vacuum region" ],
                            "Value": ["VASP", "HSE06", "PAW","500 eV","Γ point","7x7x1","1e-4 eV","0.01 eV/Å","15 Å"]
                        }
                    )
                    st.dataframe(df, hide_index=True)
    

        ############################### Triplet  State ########################################3
        elif spin_multiplicity == 'triplet':
            

            if chargestate_defect == 0:
                str_charge = "neutral"
                chosen_chargestate=["neutral"]
            elif chargestate_defect == -1:
                str_charge = "charge_negative_1"
                chosen_chargestate=["charge_negative_1"]
            elif chargestate_defect == 1:
                str_charge = "charge_positive_1"
                chosen_chargestate=["charge_positive_1"]
            else:
                chosen_chargestate=[]

            ###############################

            ### Singlet
            band_energy_spinUp_filled = []
            band_energy_spinUp_unfilled = []
            band_energy_spinDown_filled = []
            band_energy_spinDown_unfilled = []
            fermi_energy = ['0','0']

            ### Triplet
            band_energy_spinUp_filled_triplet = []
            band_energy_spinUp_unfilled_triplet = []
            band_energy_spinDown_filled_triplet = []
            band_energy_spinDown_unfilled_triplet = []
            fermi_energy_triplet = ['0','0']

            ### Excited Triplet
            band_energy_spinUp_filled_excited_triplet = []
            band_energy_spinUp_unfilled_excited_triplet = []
            band_energy_spinDown_filled_excited_triplet = []
            band_energy_spinDown_unfilled_excited_triplet = []
            fermi_energy_excited_triplet = ['0','0']

            if chosen_chargestate == ["neutral"] :
                singlet_path = "database_triplet/" + str_defect + "/singlet/output_database.txt"
                triplet_path = "database_triplet/" + str_defect + "/triplet/output_database.txt"
                excited_triplet_path= "database_triplet/" + str_defect + "/excited_triplet/output_database.txt"

                atomposition_singlet = "database_triplet/" + str_defect + "/singlet/CONTCAR_cartesian"
                atomposition_triplet = "database_triplet/" + str_defect + "/triplet/CONTCAR_cartesian"
                atomposition_excited_triplet = "database_triplet/" + str_defect + "/excited_triplet/CONTCAR_cartesian"

                fractional_singlet = "database_triplet/" + str_defect + "/singlet/CONTCAR_fractional"
                fractional_triplet = "database_triplet/" + str_defect + "/triplet/CONTCAR_fractional"
                fractional_excited_triplet = "database_triplet/" + str_defect + "/excited_triplet/CONTCAR_fractional"

                cif_singlet = "database_triplet/" + str_defect + "/singlet/structure.cif"
                cif_triplet = "database_triplet/" + str_defect + "/triplet/structure.cif"
                cif_excited_triplet = "database_triplet/" + str_defect + "/excited_triplet/structure.cif"

                ### Singlet State ###
                df = pd.read_fwf(singlet_path, sep=" ",header=None)  

                band_energy_spinUp_filled = []
                band_energy_spinUp_unfilled = []
                band_energy_spinDown_filled = []
                band_energy_spinDown_unfilled = []
                fermi_energy = []
                for row in range(0,512,1):
                    if row == 0 or row == 256:
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        fermi_energy.append(df_row[2])
                    elif row > 3 and row < 256: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinUp_filled.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinUp_unfilled.append(float(df_row[1]))
                    elif row > 259: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinDown_filled.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinDown_unfilled.append(float(df_row[1]))

                ### Triplet State ###
                df = pd.read_fwf(triplet_path, sep=" ",header=None)  

                band_energy_spinUp_filled_triplet = []
                band_energy_spinUp_unfilled_triplet = []
                band_energy_spinDown_filled_triplet = []
                band_energy_spinDown_unfilled_triplet = []
                fermi_energy_triplet = []
                for row in range(0,512,1):
                    if row == 0 or row == 256:
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        fermi_energy_triplet.append(df_row[2])
                    elif row > 3 and row < 256: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinUp_filled_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinUp_unfilled_triplet.append(float(df_row[1]))
                    elif row > 259: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinDown_filled_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinDown_unfilled_triplet.append(float(df_row[1]))

                ### Excited Triplet State ###
                try:
                    df = pd.read_fwf(excited_triplet_path, sep=" ",header=None)
                except FileNotFoundError:
                    if spin_transition =="down-down":
                        try1 = "database_triplet/" + str_defect + "/excited_triplet_down/output_database.txt"
                        df = pd.read_fwf(try1, sep=" ",header=None)
                    elif spin_transition =="up-up":
                        try1 = "database_triplet/" + str_defect + "/excited_triplet_up/output_database.txt"
                        df = pd.read_fwf(try1, sep=" ",header=None)

                band_energy_spinUp_filled_excited_triplet = []
                band_energy_spinUp_unfilled_excited_triplet = []
                band_energy_spinDown_filled_excited_triplet = []
                band_energy_spinDown_unfilled_excited_triplet = []
                fermi_energy_excited_triplet_path = []
                for row in range(0,512,1):
                    if row == 0 or row == 256:
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        fermi_energy_excited_triplet.append(df_row[2])
                    elif row > 3 and row < 256: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinUp_filled_excited_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinUp_unfilled_excited_triplet.append(float(df_row[1]))
                    elif row > 259: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinDown_filled_excited_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinDown_unfilled_excited_triplet.append(float(df_row[1]))

                fermi_energy = [float(i) for i in fermi_energy]
                fermi_energy_triplet = [float(i) for i in fermi_energy_triplet]
                fermi_energy_excited_triplet = [float(i) for i in fermi_energy_excited_triplet]
                            

            elif chosen_chargestate == ["charge_positive_1"]  or chosen_chargestate == ["charge_negative_1"]:
                singlet_path = "database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/singlet/output_database.txt"
                triplet_path = "database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/triplet/output_database.txt"
                excited_triplet_path = "database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/excited_triplet/output_database.txt"

                atomposition_singlet = "database_triplet/" + str_defect + "/" + chosen_chargestate[0]+ "/singlet/CONTCAR_cartesian"
                atomposition_triplet = "database_triplet/" + str_defect + "/" + chosen_chargestate[0]+ "/triplet/CONTCAR_cartesian"
                atomposition_excited_triplet = "database_triplet/" + str_defect + "/" + chosen_chargestate[0]+ "/excited_triplet/CONTCAR_cartesian"

                fractional_singlet = "database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/singlet/CONTCAR_fractional"
                fractional_triplet = "database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/triplet/CONTCAR_fractional"
                fractional_excited_triplet = "database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/excited_triplet/CONTCAR_fractional"

                cif_singlet = "database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/singlet/structure.cif"
                cif_triplet = "database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/triplet/structure.cif"
                cif_excited_triplet = "database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/excited_triplet/structure.cif"

                ### Singlet
                df = pd.read_fwf(singlet_path, sep=" ",header=None)  
                
                band_energy_spinUp_filled = []
                band_energy_spinUp_unfilled = []
                band_energy_spinDown_filled = []
                band_energy_spinDown_unfilled = []
                fermi_energy = []
                for row in range(0,512,1):
                    if row == 0 or row == 256:
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        fermi_energy.append(df_row[2])
                    elif row > 3 and row < 256: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinUp_filled.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinUp_unfilled.append(float(df_row[1]))
                    elif row > 259: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinDown_filled.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinDown_unfilled.append(float(df_row[1]))
                ### Triplet
                df = pd.read_fwf(triplet_path, sep=" ",header=None)  

                band_energy_spinUp_filled_triplet = []
                band_energy_spinUp_unfilled_triplet = []
                band_energy_spinDown_filled_triplet = []
                band_energy_spinDown_unfilled_triplet = []
                fermi_energy_triplet = []

                for row in range(0,512,1):
                    if row == 0 or row == 256:
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        fermi_energy_triplet.append(df_row[2])
                    elif row > 3 and row < 256: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinUp_filled_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinUp_unfilled_triplet.append(float(df_row[1]))
                    elif row > 259: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinDown_filled_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinDown_unfilled_triplet.append(float(df_row[1]))

                ### Excited Triplet State ###
                #df = pd.read_fwf(excited_triplet_path, sep=" ",header=None)  
                #### add location of charge by Nos 24.10.2024
                try:
                    df = pd.read_fwf(excited_triplet_path, sep=" ",header=None)
                except FileNotFoundError:
                    if chosen_chargestate == ["charge_negative_1"]:
                        if spin_transition =="down-down":
                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                            df = pd.read_fwf(try1, sep=" ",header=None)
                        elif spin_transition =="up-up":
                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                            df = pd.read_fwf(try1, sep=" ",header=None)
                    elif chosen_chargestate == ["charge_positive_1"]:
                        if spin_transition =="down-down":
                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                            df = pd.read_fwf(try1, sep=" ",header=None)
                        elif spin_transition =="up-up":
                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
                            df = pd.read_fwf(try1, sep=" ",header=None)
                ##################
                band_energy_spinUp_filled_excited_triplet = []
                band_energy_spinUp_unfilled_excited_triplet = []
                band_energy_spinDown_filled_excited_triplet = []
                band_energy_spinDown_unfilled_excited_triplet = []
                fermi_energy_excited_triplet = []
                for row in range(0,512,1):
                    if row == 0 or row == 256:
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        fermi_energy_excited_triplet.append(df_row[2])
                    elif row > 3 and row < 256: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinUp_filled_excited_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinUp_unfilled_excited_triplet.append(float(df_row[1]))
                    elif row > 259: 
                        df2 = df.iloc[row,0].split(" ")
                        df_row = [ele for ele in df2 if ele.strip()]
                        if round(float(df_row[2])) == 1 :
                            band_energy_spinDown_filled_excited_triplet.append(float(df_row[1]))
                        elif round(float(df_row[2])) == 0:
                            band_energy_spinDown_unfilled_excited_triplet.append(float(df_row[1]))

                fermi_energy = [float(i) for i in fermi_energy]
                fermi_energy_triplet = [float(i) for i in fermi_energy_triplet]
                fermi_energy_excited_triplet = [float(i) for i in fermi_energy_excited_triplet]          

                
            spin_nummer = 4

            try: 
                upfsinglet = np.array(band_energy_spinUp_filled)
                upfreiplet = np.array(band_energy_spinUp_filled_triplet)
                upfreipletexc = np.array(band_energy_spinUp_filled_excited_triplet)

                upunfsinglet = np.array(band_energy_spinUp_unfilled)
                upunfreiplet = np.array(band_energy_spinDown_unfilled_triplet)
                upunfreipletexc = np.array(band_energy_spinUp_unfilled_excited_triplet)

                singlet_ref = upfsinglet[upfsinglet < -5][-1]
                triplet_ref = upfreiplet[upfreiplet < -5][-1]
                excited_triplet_ref = upfreipletexc[upfreipletexc < -5][-1] 

                singletunf_ref = upunfsinglet[upunfsinglet > 1][0]
                tripletunf_ref = upunfreiplet[upunfreiplet > 1][0]
                excited_triplet_ref = upunfreipletexc[upunfreipletexc > 1][0]

            except IndexError:
                singlet_ref = -5
                triplet_ref =-5
                excited_triplet_ref = -5

                singletunf_ref = 1
                tripletunf_ref = 1
                excited_triplet_ref = 1

            fup = [energy - singlet_ref for energy in band_energy_spinUp_filled[-spin_nummer:]]
            ufup = [energy - singlet_ref for energy in band_energy_spinUp_unfilled[:spin_nummer]]
            fdown = [energy - singlet_ref for energy in band_energy_spinDown_filled[-spin_nummer:]]
            ufdown = [energy - singlet_ref for energy in band_energy_spinDown_unfilled[:spin_nummer]]

            fup_t = [energy - triplet_ref for energy in band_energy_spinUp_filled_triplet[-spin_nummer:]]
            ufup_t = [energy - triplet_ref for energy in band_energy_spinUp_unfilled_triplet[:spin_nummer]]
            fdown_t = [energy - triplet_ref for energy in band_energy_spinDown_filled_triplet[-spin_nummer:]]
            ufdown_t = [energy - triplet_ref for energy in band_energy_spinDown_unfilled_triplet[:spin_nummer]]

            fup_t_exc = [energy - triplet_ref for energy in band_energy_spinUp_filled_excited_triplet[-spin_nummer:]]
            ufup_t_exc = [energy - triplet_ref for energy in band_energy_spinUp_unfilled_excited_triplet[:spin_nummer]]
            fdown_t_exc = [energy - triplet_ref for energy in band_energy_spinDown_filled_excited_triplet[-spin_nummer:]]
            ufdown_t_exc = [energy - triplet_ref for energy in band_energy_spinDown_unfilled_excited_triplet[:spin_nummer]]

            all_band_energy = np.concatenate([fup,ufup,fup_t_exc,fup_t,ufup_t,ufup_t_exc,fdown,fdown_t,fdown_t_exc, ufdown,ufdown_t,ufdown_t_exc])

            try:
                eemin = np.min(all_band_energy)
                eemax = np.max(all_band_energy)
            except ValueError:  #raised if `y` is empty.
                eemin =0
                eemax =6

            ### Plots ### 

            def spin_marker (spinstate, band_energy, size, xcor, e_ref , bandlimit ,emin, emax):
                scale =32
                delta = 0
                emin = emin
                emax = emax
                if spinstate == 'fup':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band+size/2,band+size/2-size/3,band+size/2-size/3,
                                            band,band,band-size/12,band-size/12,
                                            band-size/2,band-size/2,
                                            band-size/12,band-size/12,band,band,
                                            band+size/2-size/3,band+size/2-size/3,band+size/2])

                        fig.add_trace(go.Scatter(x=x_arrow, y=y_arrow, fill="toself",mode='lines',opacity=1, fillcolor= 'black',
                                                name=r'{}'.format(band)))
                        fig.add_shape(type="rect",x0=xcor-0.1, y0=0, x1=xcor+0.4, y1=-1+emin,fillcolor='rgb(116, 167, 200)', layer="below")

                        delta += 0.02

                elif spinstate == 'fdown':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)            
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band-size/2,band-size/2+size/3,band-size/2+size/3,
                                            band,band,band+size/12,band+size/12,
                                            band+size/2,band+size/2,
                                            band+size/12,band+size/12,band,band,
                                            band-size/2+size/3,band-size/2+size/3,band-size/2])            
                        
                        fig.add_trace(go.Scatter(x=x_arrow, y=y_arrow, fill="toself",mode='lines', opacity=1, fillcolor= 'black',
                                                name=r'{}'.format(band)))
                        #fig.add_shape(type="rect",x0=xcor+0.1, y0=-5-fermi_energy, x1=xcor-0.15, y1=-1+emin,fillcolor="Blue",opacity=0.1)

                        delta += 0.02

                elif spinstate == 'ufup':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band+size/2,band+size/2-size/3,band+size/2-size/3,
                                            band,band,band-size/12,band-size/12,
                                            band-size/2,band-size/2,
                                            band-size/12,band-size/12,band,band,
                                            band+size/2-size/3,band+size/2-size/3,band+size/2])
                        
                        fig.add_trace(go.Scatter(x=x_arrow, y=y_arrow,mode='lines', fill="toself",opacity=1, fillcolor= 'white',
                                                name=r'{}'.format(band)))
                        fig.add_shape(type="rect",x0=xcor-0.1, y0=bandlimit-e_ref, x1=xcor+0.4, y1=1+emax,fillcolor= 'rgb(237, 140, 140)', layer="below")

                        delta += 0.02

                elif spinstate == 'ufdown':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band-size/2,band-size/2+size/3,band-size/2+size/3,
                                            band,band,band+size/12,band+size/12,
                                            band+size/2,band+size/2,
                                            band+size/12,band+size/12,band,band,
                                            band-size/2+size/3,band-size/2+size/3,band-size/2])

                        fig.add_trace(go.Scatter(x=x_arrow, y=y_arrow,mode='lines',fill="toself",opacity=1, fillcolor= 'white',
                                                name=r'{}'.format(band)))
                        
                        #fig.add_shape(type="rect",x0=xcor+0.1, y0=1-fermi_energy, x1=xcor-0.15, y1=1+emax,fillcolor="red",opacity=0.1)

                        delta += 0.02

            #### excited triplet plot
            def spin_marker_exc (spinstate, band_energy, size, xcor, e_ref , bandlimit ,emin, emax):
                scale =32
                delta = 0
                emin = emin
                emax = emax
                if spinstate == 'fup':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band+size/2,band+size/2-size/3,band+size/2-size/3,
                                            band,band,band-size/12,band-size/12,
                                            band-size/2,band-size/2,
                                            band-size/12,band-size/12,band,band,
                                            band+size/2-size/3,band+size/2-size/3,band+size/2])

                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow, fill="toself",mode='lines',opacity=1, fillcolor= 'black',
                                                name=r'{}'.format(band)))
                        fig2.add_shape(type="rect",x0=0, y0=0, x1=1, y1=-1+emin,fillcolor='rgb(116, 167, 200)', layer="below")

                        delta += 0.02

                elif spinstate == 'fdown':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)            
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band-size/2,band-size/2+size/3,band-size/2+size/3,
                                            band,band,band+size/12,band+size/12,
                                            band+size/2,band+size/2,
                                            band+size/12,band+size/12,band,band,
                                            band-size/2+size/3,band-size/2+size/3,band-size/2])            
                        
                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow, fill="toself",mode='lines', opacity=1, fillcolor= 'black',
                                                name=r'{}'.format(band)))
                        #fig2.add_shape(type="rect",x0=xcor+0.1, y0=-5-fermi_energy, x1=xcor-0.15, y1=-1+emin,fillcolor="Blue",opacity=0.1)

                        delta += 0.02

                elif spinstate == 'ufup':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band+size/2,band+size/2-size/3,band+size/2-size/3,
                                            band,band,band-size/12,band-size/12,
                                            band-size/2,band-size/2,
                                            band-size/12,band-size/12,band,band,
                                            band+size/2-size/3,band+size/2-size/3,band+size/2])
                        
                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow,mode='lines', fill="toself",opacity=1, fillcolor= 'white',
                                                name=r'{}'.format(band)))
                        fig2.add_shape(type="rect",x0=0, y0=bandlimit-e_ref, x1=1, y1=1+emax,fillcolor= 'rgb(237, 140, 140)', layer="below")

                        delta += 0.02

                elif spinstate == 'ufdown':
                    for band in band_energy:
                        xl= np.array(xcor)
                        yl =np.array(band)
                        x_arrow = np.array([xcor+delta,xcor+size/scale+delta,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor+3*size/scale,xcor+3*size/scale,xcor+size/(scale*2)+delta,
                                            xcor+size/(scale*2)+delta,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-3*size/scale,xcor-3*size/scale,xcor-size/(scale*2)+delta,
                                            xcor-size/(scale*2)+delta,xcor-size/scale+delta,xcor+delta])
                        y_arrow = np.array([band-size/2,band-size/2+size/3,band-size/2+size/3,
                                            band,band,band+size/12,band+size/12,
                                            band+size/2,band+size/2,
                                            band+size/12,band+size/12,band,band,
                                            band-size/2+size/3,band-size/2+size/3,band-size/2])

                        fig2.add_trace(go.Scatter(x=x_arrow, y=y_arrow,mode='lines',fill="toself",opacity=1, fillcolor= 'white',
                                                name=r'{}'.format(band)))
                        
                        #fig2.add_shape(type="rect",x0=xcor+0.1, y0=1-fermi_energy, x1=xcor-0.15, y1=1+emax,fillcolor="red",opacity=0.1)

                        delta += 0.02

            fig = go.Figure()
            spin_marker ('fup', fup_t, size=0.5, xcor=0.6,e_ref = singlet_ref,bandlimit =singletunf_ref,emin=eemin, emax=eemax)
            spin_marker ('ufup', ufup_t, size=0.5, xcor=0.6,e_ref = singlet_ref,bandlimit =singletunf_ref,emin=eemin, emax=eemax)
            spin_marker ('fdown', fdown_t, size=0.5, xcor=0.9,e_ref = singlet_ref,bandlimit =singletunf_ref,emin=eemin, emax=eemax)
            spin_marker ('ufdown', ufdown_t, size=0.5, xcor=0.9,e_ref = singlet_ref,bandlimit =singletunf_ref,emin=eemin, emax=eemax)

            spin_marker ('fup', fup, size=0.5, xcor=0.1,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            spin_marker ('ufup', ufup, size=0.5, xcor=0.1, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            spin_marker ('fdown', fdown, size=0.5, xcor=0.4,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            spin_marker ('ufdown', ufdown, size=0.5, xcor=0.4, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            
            #### Figures and tables
            fig.update_xaxes(
                    title_font = {"size": 30},
                    showgrid=False,
                    range=[0, 1],
                    showticklabels=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True
                    )

            fig.update_yaxes(
                    title_font = {"size": 20},
                    showgrid=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True,
                    )

            fig2 = go.Figure()        
            spin_marker_exc ('fup', fup_t_exc, size=0.5, xcor=0.3,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            spin_marker_exc ('ufup', ufup_t_exc, size=0.5, xcor=0.3, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            spin_marker_exc ('fdown', fdown_t_exc, size=0.5, xcor=0.7,e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            spin_marker_exc ('ufdown', ufdown_t_exc, size=0.5, xcor=0.7, e_ref = triplet_ref,bandlimit =tripletunf_ref,emin=eemin, emax=eemax)
            
            #### Figures and tables
            fig2.update_xaxes(
                    title_font = {"size": 30},
                    showgrid=False,
                    range=[0, 1],
                    showticklabels=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True
                    )

            fig2.update_yaxes(
                    title_font = {"size": 20},
                    showgrid=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True,
                    )


            try: 
                name_change = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='updated_data',engine = 'openpyxl')
                latexdefect = name_change[name_change['Defect']==str_defect]['Defect name'].reset_index().iloc[0,1]
                latexdefect = latexdefect.replace("$","")

            except IndexError:
                latexdefect = str_defect

            fig.update_layout(showlegend=False, 
                            xaxis_title=r"${}$".format(latexdefect),
                            yaxis_title=r"$E(eV)$ ",
                            font=dict(size=18,color="Black")
                            )

            fig2.update_layout(showlegend=False, 
                            xaxis_title=r"${}$".format(latexdefect),
                            yaxis_title=r"$E(eV)$ ",
                            font=dict(size=18,color="Black")
                            )

            fig.add_trace(go.Scatter(
                x=[0.25, .75],
                y=[3,3],
                text=["Singlet","Triplet"],
                mode="text",
            ))

            fig2.add_trace(go.Scatter(
                x=[0.5],
                y=[3,3],
                text=["Triplet"],
                mode="text",
            ))

            fig.update_traces(textfont_size=13)
            chargetrans = {'charge_positive_1':1,'charge_negative_1':-1,'neutral':0}


            row1 = st.columns(2)
            row2 = st.columns(2)


            col1, col2 = st.columns(2,gap ="small")#st.columns([0.5,0.5])
            with col1:
                with st.container(border=True):
                    st.header('Kohn-Sham electronic transition')
                    tab1, tab2 = st.tabs(["Ground State","Excited State"])
                    with tab1:                
                        st.components.v1.html(fig.to_html(include_mathjax='cdn'),width=530, height=600)
                    with tab2: 
                        st.components.v1.html(fig2.to_html(include_mathjax='cdn'),width=530, height=600)
            with col2:
                with st.container(border=True):
                    ######################### atomic position data frame  #################################3
                    if  type(chosen_defect) == str:
                        latexdefect = 'Al_N'
                        atomicposition_sin = pd.read_csv("database_triplet/" + 'AlN' + "/triplet/CONTCAR_cartesian",sep=';', header=0)        
                    else:
                        try: 
                            atomicposition_sin = pd.read_csv(atomposition_triplet,sep=';', header=0)
                        except NameError or ValueError:
                            latexdefect = 'Al_N'
                            atomicposition_sin = pd.read_csv("database_triplet/" + str_defect + "/triplet/CONTCAR_cartesian",sep=';', header=0)
                    atomicposition = pd.DataFrame(columns = ['properties', 'X','Y','Z'])
                    for row in range(atomicposition_sin.shape[0]):
                        if 0 <row<4:
                            df2 = atomicposition_sin.iloc[row,0].split(" ")
                            df_row = [ele for ele in df2 if ele.strip()]
                            atomicposition.loc[row,['X','Y','Z']] = df_row
                    atomicposition.loc[1:4,'properties'] = ['Lattice a', 'Lattice b', 'Lattice c']
                    ##
                    iindex =0
                    startind =6
                    dataframeind = 3
                    letternumber =[[ele for ele in atomicposition_sin.iloc[4,0].split(" ") if ele.strip()],
                                [ele for ele in atomicposition_sin.iloc[5,0].split(" ") if ele.strip()]]
                    bnnumber=[]
                    for num in letternumber[1]:
                        letter =letternumber[0][iindex]
                        numnum = int(num)
                        bnnumber.append(numnum)
                        for element in range(1,numnum+1):
                            startind =startind+1
                            dataframeind= dataframeind+1     
                            df2 = atomicposition_sin.iloc[startind,0].split(" ")
                            df_row = [ele for ele in df2 if ele.strip()]
                            atomicposition.loc[dataframeind,['X','Y','Z']] = df_row[0:3]
                            atomicposition.loc[dataframeind,'properties'] = '{}-{}'.format(letter,element)
                        iindex+=1
                    
                    atomicposition.loc[:,['X','Y','Z']]=atomicposition.loc[:,['X','Y','Z']].astype(float).round(decimals=5)

                    #### plot atomic bonds
                    st.header("Atomic positions for a ground triplet state (${}$)".format(latexdefect))    
                    fig3D = go.Figure()
                    i=0
                    letters=letternumber[0]
                    numbers=letternumber[1]

                    numcounter=0
                    indexcounter=3
                    atomsize=6
                    for ele in letters:
                        if ele == 'B':
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele,marker=dict( size=atomsize, color='rgb(255,147,150)')))
                        elif ele == 'C':
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele,marker=dict(size=atomsize,color='rgb(206,0,0)')))
                        elif ele == 'N':
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele, marker=dict(size=atomsize,color='rgb(0,0,255)')))
                        else:
                            numberint= int(numbers[numcounter])
                            xb,yb,zb= np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,1]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,2]),np.array(atomicposition.iloc[indexcounter:indexcounter+numberint,3])
                            fig3D.add_trace(go.Scatter3d(x= xb,y=yb,z=zb, mode='markers', name=ele, marker=dict( size=atomsize)))
                        numcounter+=1
                        indexcounter=indexcounter+numberint

                    ## atome bonds
                    atoms= atomicposition.iloc[3:]
                    for ele in atoms['properties']:
                        if  list(ele)[0] =='B':
                            ele_loc=atoms[atoms['properties'] == ele]
                            ele_index=ele_loc.index
                            other= atoms.drop(ele_index)
                            other.iloc[:,1:4]=other.iloc[:,1:4]-atoms.iloc[ele_index[0]-4,1:4]
                            other['norm'] = other.iloc[:,1:4].apply(lambda x: x **2).apply(np.sum, axis=1)
                            near_atom_diff= other.sort_values(by=['norm'],ascending=True)
                            near_atom_diff=near_atom_diff[near_atom_diff["norm"]<3]
                            near_atom_1=atoms.iloc[near_atom_diff.index-4]
                            near_atom_2=near_atom_1.copy()
                            near_atom_2['element'] = near_atom_2['properties'].map(lambda x:  list(x)[0])
                            near_atom_3=near_atom_2[near_atom_2['element']== 'N']
                            near_atom=atoms.iloc[near_atom_3.index-4].iloc[0:3]
                            tail=ele_loc.to_numpy()
                            head=near_atom.to_numpy()
                            for i in range(0,near_atom.shape[0]):
                                fig3D.add_trace(go.Scatter3d(x=[tail[0,1],head[i,1]], y=[tail[0,2],head[i,2]],z=[tail[0,3],head[i,3]],hoverinfo ='skip', mode='lines', line=dict(color='black',width=5),showlegend=False))


                    ## dipole
                    dipole = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='updated_data',engine = 'openpyxl',header=[0])
                    try: 
                        dipole_emi = dipole[(dipole['Defect'] == str_defect) & (dipole['Charge state'] ==chargetrans[str_charge]) & (dipole['Optical spin transition'] == spin_transition)]
                    except  NameError :
                        dipole_emi = dipole[dipole['Defect'] == str_defect]
                    except  KeyError:
                        dipole_emi = dipole[dipole['Defect'] == str_defect]

                    tail_emi_plane = dipole_emi['Emission properties: linear In-plane Polarization Visibility'].values[0]
                    tail_emi_cry = dipole_emi['Emission properties: Angle of emission dipole wrt the crystal axis'].values[0]
                    tail_exc_plane = dipole_emi['Excitation properties: linear In-plane Polarization Visibility'].values[0]
                    tail_exc_cry = dipole_emi['Excitation properties: Angle of excitation dipole wrt the crystal axis'].values[0]
                    
                    ctrystal_axes_start = np.array([3.736,7.960,1.668])
                    ctrystal_axes_start2=np.array([3.736,3.960,1.668])
                    ctrystal_axes_end = np.array([3.736,11.960,1.668])-ctrystal_axes_start

                    theta_emi =  np.radians((1-tail_emi_plane)*90)
                    #theta_emi =  np.radians(90)
                    theta_exc =  np.radians((1-tail_exc_plane)*90)

                    phi_emi = np.radians(tail_emi_cry)
                    #phi_emi =np.radians(0)
                    phi_exc = np.radians(tail_exc_cry)

                    ## ploting Emission Dipole
                    # rotate z-axis
                    c, s = np.cos(phi_emi), np.sin(phi_emi)
                    r_z = np.array(((c,-s,0), (s,c,0), (0,0,1)))
                    # rotate x-axis
                    c, s = np.cos(theta_emi), np.sin(theta_emi)
                    r_x = np.array(((1,0,0), (0,c, -s), (0,s, c)))

                    r_xz=np.dot(r_x,r_z)
                    head = np.dot(r_xz,ctrystal_axes_end)  #ctrystal_axes_end
                    tail=np.array([3.736,7.960,1.668])

                    head=head+ctrystal_axes_start
                    ctrystal_axes_end= ctrystal_axes_end+ctrystal_axes_start        

                    fig3D.add_trace(go.Cone(x=[head[0]], y=[head[1]], z=[head[2]], u=[head[0]-tail[0]], v=[head[1]-tail[1]], w=[head[2]-tail[2]],
                                            colorscale='ylorrd',showscale=False,hoverinfo='skip',sizeref=0.2))
                    fig3D.add_trace(go.Scatter3d(x=[tail[0],head[0]], y=[tail[1],head[1]],z=[tail[2],head[2]],hoverinfo ='skip',marker=dict(size=3, color='yellow'),
                                                line=dict(color='orange',width=6),showlegend=True,name="Emission"))
                    fig3D.add_trace(go.Scatter3d(x=[ctrystal_axes_start2[0],ctrystal_axes_end[0]], y=[ctrystal_axes_start2[1],ctrystal_axes_end[1]],z=[ctrystal_axes_start2[2],ctrystal_axes_end[2]],
                                                hoverinfo ='skip', marker=dict(size=1, color='red'), line=dict(color='red',width=5,dash='dot'),showlegend=True,name="Crystal Axis"))
                    
                    ## ploting Excitation Dipole
                    ctrystal_axes_end = np.array([3.736,11.960,1.668])-ctrystal_axes_start
                    # rotate z-axis
                    c, s = np.cos(phi_exc), np.sin(phi_exc)
                    r_z = np.array(((c,-s,0), (s,c,0), (0,0,1)))
                    # rotate x-axis
                    c, s = np.cos(theta_exc), np.sin(theta_exc)
                    r_x = np.array(((1,0,0), (0,c, -s), (0,s, c)))

                    r_xz=np.dot(r_x,r_z)
                    head = np.dot(r_xz,ctrystal_axes_end)  #ctrystal_axes_end
                    tail=np.array([3.736,7.960,1.668])

                    head=head+ctrystal_axes_start
                    ctrystal_axes_end= ctrystal_axes_end+ctrystal_axes_start        

                    fig3D.add_trace(go.Cone(x=[head[0]], y=[head[1]], z=[head[2]], u=[head[0]-tail[0]], v=[head[1]-tail[1]], w=[head[2]-tail[2]],
                                            colorscale='Greens',showscale=False,hoverinfo='skip',sizeref=0.2))
                    fig3D.add_trace(go.Scatter3d(x=[tail[0],head[0]], y=[tail[1],head[1]],z=[tail[2],head[2]],hoverinfo ='skip',marker=dict(size=3, color='green'),
                                                line=dict(color='green',width=6),showlegend=True,name="Excitation"))

                    fig3D.update_layout(scene = dict( zaxis = dict( range=[0,25],showgrid=False, backgroundcolor="rgb(0,0,0)",gridcolor="rgb(0,0,0)",zeroline=False,showticklabels =False,title =' '), 
                                                    yaxis = dict(showgrid=False,backgroundcolor="rgb(0,0,0)",gridcolor="rgb(0,0,0)",zeroline=False,showticklabels =False,title =' '), 
                                                    xaxis = dict(showgrid=False,backgroundcolor="rgb(0,0,0)",gridcolor="rgb(0,0,0)",zeroline=False,showticklabels =False,title =' '), 
                                                    camera_eye=dict(x=0, y=0, z=0.8))
                    )
                    st.plotly_chart(fig3D, use_container_width=True)
                    ####################### download data atomic position ###################################################333
                    with st.container(border=False):
                        st.header("Download data")
                        cold1, cold2,cold3  = st.columns(3,gap="Small") # cartesian, fraction, cif files respectively
                        with cold1:
                            try:
                                st.download_button(
                                    label="VASP cartesian ground triplet",
                                    data= open(atomposition_triplet, "r"),
                                    file_name=f'VASP cartesian ground triplet-{str_defect}'
                                )
                            except :
                                st.download_button(
                                    label="VASP cartesian ground triplet",
                                    data= open(atomposition_triplet, "r"),
                                    file_name=f'VASP cartesian ground triplet-{str_defect}2'
                                )
                            try:
                                st.download_button(
                                    label="VASP cartesian ground singlet",
                                    data= open(atomposition_singlet, "r"),
                                    file_name=f'VASP cartesian ground singlet-{str_defect}'
                                )
                            except:
                                st.download_button(
                                    label="VASP cartesian ground singlet",
                                    data= open(atomposition_singlet, "r"),
                                    file_name=f'VASP cartesian ground singlet-{str_defect}2'
                                ) 
                            try:
                                st.download_button(
                                    label="VASP cartesian excited triplet",
                                    data= open(atomposition_excited_triplet, "r"),
                                    file_name=f'VASP cartesian excited triplet-{str_defect}-{chargestate_defect}'
                                )
                            except FileNotFoundError:
                                if spin_transition =="down-down":
                                    try1 = "database_triplet/" + str_defect + "/excited_triplet_down/CONTCAR_cartesian"                        
                                elif spin_transition =="up-up":
                                    try1 = "database_triplet/" + str_defect + "/excited_triplet_up/CONTCAR_cartesian"
                                try:
                                    st.download_button(
                                        label="VASP cartesian excited triplet",
                                        data= open(try1, "r"),
                                        file_name=f'VASP cartesian excited triplet-{str_defect}-{chargestate_defect}'
                                    )
                                #except:
                                #    st.download_button(
                                #        label="VASP cartesian excited triplet",
                                #        data= open(try1, "r"),
                                #        file_name=f'VASP cartesian excited triplet-{str_defect}-{chargestate_defect}2'
                                #    )
                                #### the above part commented and the below part added by Nos 24.10.2024
                                except FileNotFoundError:
                                    if chosen_chargestate == ["charge_negative_1"]:
                                        if spin_transition =="down-down":
                                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                                        elif spin_transition =="up-up":
                                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                                    elif chosen_chargestate == ["charge_positive_1"]:
                                        if spin_transition =="down-down":
                                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                                        elif spin_transition =="up-up":
                                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
                                    try:
                                        st.download_button(
                                            label="VASP cartesian excited triplet",
                                            data= open(try1, "r"),
                                            file_name=f'VASP cartesian excited triplet-{str_defect}-charge{chargestate_defect}'
                                        )
                                    except:
                                        st.download_button(
                                            label="VASP cartesian excited triplet",
                                            data= open(try1, "r"),
                                            file_name=f'VASP cartesian excited triplet-{str_defect}-{chargestate_defect}2'
                                        )
                ##################
                        with cold2:
                            try:
                                st.download_button(
                                    label="VASP fractional ground triplet",
                                    data= open(fractional_triplet, "r"),
                                    file_name=f'VASP fractional ground triplet-{str_defect}'
                                )
                            except:
                                st.download_button(
                                    label="VASP fractional ground triplet",
                                    data= open(fractional_triplet, "r"),
                                    file_name=f'VASP fractional ground triplet-{str_defect}2'
                                )
                            try:
                                st.download_button(
                                    label="VASP fractional ground singlet",
                                    data= open(fractional_singlet, "r"),
                                    file_name=f'VASP fractional ground singlet-{str_defect}'
                                )
                            except:
                                st.download_button(
                                    label="VASP fractional ground singlet",
                                    data= open(fractional_singlet, "r"),
                                    file_name=f'VASP fractional ground singlet-{str_defect}2'
                                )
                            try:
                                st.download_button(
                                    label="VASP fractional excited triplet",
                                    data= open(fractional_excited_triplet, "r"),
                                    file_name=f'VASP fractional excited triplet-{str_defect}-{chargestate_defect}'
                                )
                            except FileNotFoundError:
                                if spin_transition =="down-down":
                                    try1 = "database_triplet/" + str_defect + "/excited_triplet_down/CONTCAR_fractional"                        
                                elif spin_transition =="up-up":
                                    try1 = "database_triplet/" + str_defect + "/excited_triplet_up/CONTCAR_fractional"
                                try:    
                                    st.download_button(
                                        label="VASP fractional excited triplet",
                                        data= open(try1, "r"),
                                        file_name=f'VASP fractional excited triplet-{str_defect}-{chargestate_defect}'
                                    )
                                #except:
                                #    st.download_button(
                                #        label="VASP fractional excited triplet",
                                #        data= open(try1, "r"),
                                #        file_name=f'VASP fractional excited triplet-{str_defect}-{chargestate_defect}2'
                                #    )
                                #### the above part commented and the below part added by Nos 24.10.2024
                                except FileNotFoundError:
                                    if chosen_chargestate == ["charge_negative_1"]:
                                        if spin_transition =="down-down":
                                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                                        elif spin_transition =="up-up":
                                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                                    elif chosen_chargestate == ["charge_positive_1"]:
                                        if spin_transition =="down-down":
                                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                                        elif spin_transition =="up-up":
                                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
                                    try:
                                        st.download_button(
                                            label="VASP fractional excited triplet",
                                            data= open(try1, "r"),
                                            file_name=f'VASP fractional excited triplet-{str_defect}-charge{chargestate_defect}'
                                        )
                                    except:
                                        st.download_button(
                                            label="VASP fractional excited triplet",
                                            data= open(try1, "r"),
                                            file_name=f'VASP fractional excited triplet-{str_defect}-{chargestate_defect}2'
                                        )
                        with cold3:
                            try:
                                st.download_button(
                                    label="CIF ground triplet",
                                    data= open(cif_triplet, "r"),
                                    file_name=f'CIF ground triplet-{str_defect}.cif'                
                                )
                            except:
                                st.download_button(
                                    label="CIF ground triplet",
                                    data= open(cif_triplet, "r"),
                                    file_name=f'CIF ground triplet-{str_defect}2.cif'                
                                )
                            try:
                                st.download_button(
                                    label="CIF ground singlet",
                                    data= open(cif_singlet, "r"),
                                    file_name=f'CIF ground singlet-{str_defect}.cif'                
                                )
                            except:
                                st.download_button(
                                    label="CIF ground singlet",
                                    data= open(cif_singlet, "r"),
                                    file_name=f'CIF ground singlet-{str_defect}2.cif'                
                                )
                            try:
                                st.download_button(
                                    label="CIF excited triplet",
                                    data= open(cif_excited_triplet, "r"),
                                    file_name=f'CIF excited triplet-{str_defect}-{chargestate_defect}.cif'                
                                )
                            except FileNotFoundError:
                                if spin_transition =="down-down":
                                    try1 = "database_triplet/" + str_defect + "/excited_triplet_down/structure.cif"                        
                                elif spin_transition =="up-up":
                                    try1 = "database_triplet/" + str_defect + "/excited_triplet_up/structure.cif"
                                try:
                                    st.download_button(
                                        label="CIF excited triplet",
                                        data= open(try1, "r"),
                                        file_name=f'CIF excited triplet-{str_defect}-{chargestate_defect}.cif'                
                                    )
                                #except:
                                #    st.download_button(
                                #        label="CIF excited triplet",
                                #        data= open(try1, "r"),
                                #        file_name=f'CIF excited triplet-{str_defect}-{chargestate_defect}2.cif'                
                                #    )
                                #### the above part commented and the below part added by Nos 24.10.2024
                                except FileNotFoundError:
                                    if chosen_chargestate == ["charge_negative_1"]:
                                        if spin_transition =="down-down":
                                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                                        elif spin_transition =="up-up":
                                            try1 = "database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                                    elif chosen_chargestate == ["charge_positive_1"]:
                                        if spin_transition =="down-down":
                                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                                        elif spin_transition =="up-up":
                                            try1 = "database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
                                    try:
                                        st.download_button(
                                            label="CIF excited triplet",
                                            data= open(try1, "r"),
                                            file_name=f'CIF excited triplet-{str_defect}-charge{chargestate_defect}'
                                        )
                                    except:
                                        st.download_button(
                                            label="CIF excited triplet",
                                            data= open(try1, "r"),
                                            file_name=f'CIF excited triplet-{str_defect}-{chargestate_defect}2'
                                        )


            col3, col4 = st.columns(2,gap="medium")
            with col3:
                with st.container(border=True):
                    st.header("Photophysical properties of "+"${}$".format(latexdefect))
                    # col21, col22, col23 = st.columns(3)
                    tab1, tab2, tab3 = st.tabs(["Excitation Properties", "Emission Properties", "Quantum Memory Properties"])
                    ## col21
                    #tab1.subheader('Excitation Properties')
                    Photophysical_properties = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='Excitation properties',engine = 'openpyxl',header=[0])
                    Photophysical_properties.iloc[:,4:]=Photophysical_properties.iloc[:,4:].round(2)
                    Photophysical_properties["Characteristic time (ns)"]=Photophysical_properties["Characteristic time (ns)"].astype(int)
                    Photophysical_properties["Characteristic time (ns)"] = Photophysical_properties["Characteristic time (ns)"].map("{:.2E}".format)

                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])]
                    except  NameError :
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    except  KeyError:
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    ep2=ppdefects.iloc[:,3:]
                    ep2.rename(columns={"dipole_x":"µₓ (Debye)","dipole_y":"μᵧ (Debye)","dipole_z":"µz (Debye)","Intensity":"Intensity (Debye)","Angle of excitation dipole wrt the crystal axis":"Angle of excitation dipole wrt the crystal axis (degree)"},inplace=True)
                    ep2=ep2.T
                    jj =1
                    newheadcol =[]
                    #latppdefects.iloc[1,0].replace("$","")
                    for head in ep2.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    ep2.columns =newheadcol
                    tab1.dataframe(ep2,use_container_width=True)

                    ## col22
                    #col22.subheader('Emission Properties')

                    Photophysical_properties = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='Emission properties',engine = 'openpyxl',header=[0])
                    Photophysical_properties.iloc[:,4:]=Photophysical_properties.iloc[:,4:].round(2)
                    Photophysical_properties["ZPL (nm)"]=Photophysical_properties["ZPL (nm)"].astype(int)
                    Photophysical_properties["Lifetime (ns)"]=Photophysical_properties["Lifetime (ns)"].astype(int)
                    Photophysical_properties["Lifetime (ns)"] = Photophysical_properties["Lifetime (ns)"].map("{:.2E}".format)
                    Photophysical_properties["Configuration coordinate (amu^(1/2) \AA)"]=Photophysical_properties["Configuration coordinate (amu^(1/2) \AA)"]
                    Photophysical_properties["Ground-state total energy (eV)"]=Photophysical_properties["Ground-state total energy (eV)"]
                    Photophysical_properties["Excited-state total energy (eV)"]=Photophysical_properties["Excited-state total energy (eV)"]

                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])]
                    except  NameError :
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    except  KeyError:
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    emp=ppdefects.iloc[:,3:]
                    emp.rename(columns={"dipole_x":"µₓ (Debye)","dipole_y":"μᵧ (Debye)","dipole_z":"µz (Debye)","Intensity":"Intensity (Debye)","Angle of emission dipole wrt the crystal axis":"Angle of emission dipole wrt the crystal axis (degree)","Configuration coordinate (amu^(1/2) \AA)":"Configuration coordinate (amu^(1/2) Å)","Ground-state total energy (eV)":"Ground-state total energy (eV)","Excited-state total energy (eV)":"Excited-state total energy (eV)"},inplace=True)
                    emp=emp.T
                    jj =1
                    newheadcol =[]
                    #latppdefects.iloc[1,0].replace("$","")
                    for head in emp.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    emp.columns =newheadcol
                    tab2.dataframe(emp,use_container_width=True)
                    
                    #col23
                    #col23.subheader('Quantum Memory Properties')
                    Photophysical_properties = pd.read_excel('Supplementary_database_totalE_2.xlsx',sheet_name='Quantum memory properties',engine = 'openpyxl',header=[0])
                    Photophysical_properties.iloc[:,4:]=Photophysical_properties.iloc[:,4:].round(2)
                    Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"]=Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].astype(int)
                    Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"] = Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].map("{:.2E}".format)
                    Photophysical_properties["g (MHz)"]=Photophysical_properties["g (MHz)"].astype(int)
                    Photophysical_properties["g (MHz)"] = Photophysical_properties["g (MHz)"].map("{:.2E}".format)
                
                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])]
                    except  NameError :
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    except  KeyError:
                        ppdefects = Photophysical_properties[Photophysical_properties['Defect'] == str_defect]
                    qmp = ppdefects.iloc[:,3:]
                    qmp=qmp.T
                    jj =1
                    newheadcol =[]
                    #latppdefects.iloc[1,0].replace("$","")
                    for head in qmp.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    qmp.columns =newheadcol
                    tab3.dataframe(qmp,use_container_width=True)
            with col4:
                with st.container(border=True):
                    st.header('Computational setting')
                    df = pd.DataFrame(
                        {
                            "Computational Setting": ["DFT calculator", "Functional", "Pseudopotentials","Cutoff Energy","Kpoint",
                                                    "Supercell size", "Energy convergence","Force convergence","Vacuum region" ],
                            "Value": ["VASP", "HSE06", "PAW","500 eV","Γ point","7x7x1","1e-4 eV","0.01 eV/Å","15 Å"]
                        }
                    )
                    st.dataframe(df, hide_index=True)

    tabs_index += 1


st.header("References")
with st.container(border=False):
    st.markdown('''
    For using any of the data, please cite: \n
    [Chanaprom Cholsuk, Ashkan Zand, Asli Cakan, Tobias Vogl, *"The hBN defects database: a theoretical compilation of color centers in hexagonal boron nitride."* The Journal of Physical Chemistry C, 2024, 128 (30), 12716.](https://doi.org/10.1021/acs.jpcc.4c03404) \n
    For specific properties of particular defects, please also cite the data originally published as follows:
    ''')
    st.markdown('''
    Quantum memory properties
    * [Cholsuk, Chanaprom, Asli Çakan, Sujin Suwanna, and Tobias Vogl. *"Identifying electronic transitions of defects \
    in hexagonal boron nitride for quantum memories."* Advanced Optical Materials, 2024, 12, 2302760. \
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

st.write("--")
