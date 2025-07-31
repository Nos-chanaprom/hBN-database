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
import plotly.colors as pc
import sqlite3  # Added for DB support

@st.cache_data
def load_table(table_name: str, db_path: str = "Supplementary_database_totalE_3.db") -> pd.DataFrame:
    """
    Load a full table from the SQLite database into a DataFrame.
    """
    conn = sqlite3.connect(db_path)
    query = f'SELECT * FROM "{table_name}"'
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Fix: attempt to convert all object-type columns to numeric
    for col in df.select_dtypes(include='object').columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')  # 'ignore' avoids overwriting true strings
        # fallback: coerce clearly numeric-looking columns
        if df[col].str.isnumeric().any():
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# --- Replace Excel backend with DB backend ---


### https://plotly.com/python/images/###

# Get the list of all files and directories 
# in the root directory
#defects={}
#path = "monolayer/database_triplet" 
#defects_list = os.listdir(path)
#defects_list.sort()
#for defect in defects_list:
#    path2 = path+"/"+defect
#    charge_list = os.listdir(path2)
#    defects[defect] = charge_list


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
# ----------------------------
# Function to Extract NBANDS
# ----------------------------

def extract_nbands(outcar_path):
    """
    Extracts the NBANDS value from the last non-empty line of the OUTCAR_transition file.
    
    Parameters:
    - outcar_path (str): Path to the OUTCAR_transition file.
    
    Returns:
    - int: The number of bands (NBANDS).
    
    Raises:
    - FileNotFoundError: If the specified file does not exist.
    - ValueError: If NBANDS cannot be found or converted to an integer.
    """
    try:
        with open(outcar_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {outcar_path} was not found.")
    
    # Iterate over the lines in reverse to find the last non-empty line
    for line in reversed(lines):
        stripped_line = line.strip()
        if stripped_line:  # Check if the line is not empty
            # Split the line by whitespace and take the first element
            first_column = stripped_line.split()[0]
            try:
                nbands = int(first_column)
                return nbands
            except ValueError:
                raise ValueError(f"Cannot convert '{first_column}' to an integer for NBANDS.")
    
    # If no non-empty lines are found
    raise ValueError("No non-empty lines found in the OUTCAR_transition file to extract NBANDS.")

# Function to read defect formation energies from a file
def read_formation_energies(file_path):
    data = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        defect_name = parts[0]
        charge = int(parts[1])
        corrected_energy = float(parts[2])
        uncorrected_energy = float(parts[3])

        if defect_name not in data:
            data[defect_name] = []

        data[defect_name].append({
            'charge': charge,
            'corrected': corrected_energy,
            'uncorrected': uncorrected_energy
        })

    return data

# Function to plot formation energy diagram using Plotly
def plot_diagram_plotly(data, title,base_font: int = 12):
    fig = go.Figure()
    # Track y-axis limits
    min_energy, max_energy = np.inf, -np.inf

    for defect_name, charge_states in data.items():
        for energy_type in ['corrected', 'uncorrected']:
            for state in charge_states:
                q = state['charge']
                E_f0 = state[energy_type]
                formation_energy = E_f0 + q * E_F
                # Update min/max for y-axis
                min_energy = min(min_energy, formation_energy.min())
                max_energy = max(max_energy, formation_energy.max())

                label = f"q={q}, {energy_type}"
                
                linestyle = 'solid' if energy_type == 'corrected' else 'dash'

                fig.add_trace(go.Scatter(
                    x=E_F,
                    y=formation_energy,
                    mode='lines',
                    line=dict(dash=linestyle, width=2, color=color_map[q]),
                    name=label
                ))

    fig.update_xaxes(
        title="E<sub>Fermi</sub> (eV)",
        title_font={"size": 22},
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True
    )
    fig.update_yaxes(
        title="E<sub>form</sub> (eV)",
        title_font={"size": 22},
        showgrid=False,
        showline=True,
        zeroline=False,  # Removes horizontal line at y=0
        linewidth=2,
        linecolor='black',
        mirror=True
    )
    fig.update_layout(
        #title=title,   # title of the plot
        template="plotly_white",       # still grab all the white-template defaults…
        paper_bgcolor="white",         # …and force the outside margin to white
        plot_bgcolor="white",          # …and force the inside plotting area to white
        font=dict(size=18, color="Black"),
        showlegend=True,
        xaxis_range=[0, 6],
        yaxis_range=[min_energy - 0.5, max_energy + 0.5],  # Padding for aesthetics
        width=600,
        height=500,
        margin=dict(l=70,r=70,t=30,b=90),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='gray',
            borderwidth=0.5,
            font=dict(size=12),
            orientation="v"
        )
    )

    return fig

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
                   ### start here
                # refractive-index input placed below the defect search
                refractive_index = st.number_input(
                    "Refractive index (n)",
                    value=1.85,
                    min_value=0.1,
                    step=0.01,
                    format="%.2f",
                    help="Adjust the reported vacuum lifetime via τ = τ₀·1.85/n"
                )
                st.session_state["refractive_index"] = refractive_index

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

def spin_marker_exc_fig (spinstate, band_energy, size, xcor, e_ref , bandlimit ,emin, emax,fig):
                fig2=fig
                scale =32
                delta = -0.04
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
    
    Photophysical_properties = load_table('updated_data')
    #stash the original (vacuum) lifetime before formatting
    Photophysical_properties = load_table('updated_data')
    original_col = "Emission properties: Lifetime (ns)"
    Photophysical_properties['lifetime_db'] = Photophysical_properties[original_col].astype(float)
    # stash original characteristic time for interactive override
    char_col = "Excitation properties: Characteristic time (ns)"
    Photophysical_properties['char_db'] = Photophysical_properties[char_col].astype(float)

    ## rounding numbers
    Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)  ## select from columns 5
    
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
    # Apply filters (renders Defect search + refractive-index)
    df_filtered = filter_dataframe(Photophysical_properties)

    # Retrieve user-provided refractive index (default 1.85)
    refr_index = st.session_state.get("refractive_index", 1.85)

    # Overwrite lifetime for filtered rows
    Photophysical_properties.loc[df_filtered.index, original_col] = \
        Photophysical_properties.loc[df_filtered.index, 'lifetime_db'] \
            .apply(lambda τ: f"{τ * 1.85 / refr_index:.2E}")

    # Overwrite characteristic time for filtered rows
    Photophysical_properties.loc[df_filtered.index, char_col] = \
        Photophysical_properties.loc[df_filtered.index, 'char_db'] \
            .apply(lambda τ: f"{τ * 1.85 / refr_index:.2E}")

    # Drop helper column
    Photophysical_properties.drop(columns=['lifetime_db','char_db'], inplace=True)

    # Provide a table with selection checkboxes
    def dataframe_with_selections(df):
        df_with_selections = df.copy()
        df_with_selections.insert(0, "Select", False)
        edited_df = st.data_editor(
            df_with_selections,
            hide_index=True,
            column_config={"Select": st.column_config.CheckboxColumn(required=True)},
            disabled=df.columns,
        )
        return edited_df[edited_df.Select]

    # Display selection
    selection = dataframe_with_selections(Photophysical_properties.loc[df_filtered.index])
    st.write("Your selection:")
    st.data_editor(selection, hide_index=True)

####### END SEARCH ENGINE ########
if selection.empty :
    ele1 = Photophysical_properties[(Photophysical_properties["Defect"] == "AlN") &
        (Photophysical_properties["Host"]  == "monolayer")]
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

    host = ele12.loc[:,"Host"]
    host_m = host.reset_index().drop("index", axis='columns')

    chosenlist = ele12.loc[:,['Defect','Charge state','Optical spin transition','Spin multiplicity','Host']].to_numpy()
else:
    chosen_defect = selection.loc[:,'Defect']
    chosen_defect_m = chosen_defect.reset_index().drop("index", axis='columns')
    
    chargestate_defect = selection.loc[:,'Charge state']
    chargestate_defect_m = chargestate_defect.reset_index().drop("index", axis='columns')
    
    spin_transition = selection.loc[:,'Optical spin transition']
    spin_transition_m = spin_transition.reset_index().drop("index", axis='columns')

    spin_multiplicity = selection.loc[:,"Spin multiplicity"]
    spin_multiplicity_m = spin_multiplicity.reset_index().drop("index", axis='columns')

    host = selection.loc[:,"Host"]
    host_m = host.reset_index().drop("index", axis='columns')
    
    chosenlist = selection.loc[:,['Defect','Charge state','Optical spin transition','Spin multiplicity','Host']].to_numpy()

selection_str =[]
for ele in chosenlist:
    selection_str.append(ele[0] + " (charge state: " +str(ele[1]) + ", " +ele[2] +", " + str(ele[3]) + ", "+ str(ele[4])+")")
tab_selection = st.tabs(selection_str)
tabs_index =0
for tabs in tab_selection:
    with tabs:
        str_defect = chosen_defect_m.iloc[tabs_index,0]
        chargestate_defect = chargestate_defect_m.iloc[tabs_index,0]
        spin_transition = spin_transition_m.iloc[tabs_index,0]
        spin_multiplicity = spin_multiplicity_m.iloc[tabs_index,0]
        host = host_m.iloc[tabs_index,0]

        try: 
            name_change = load_table('updated_data')
            latexdefect = name_change[name_change['Defect']==str_defect]['Defect name'].reset_index().iloc[0,1]
            latexdefect = latexdefect.replace("$","")

        except IndexError:
            latexdefect = str_defect
        ##################### Bulk defects
        if host == 'bulk':
            charge_bulk = ['neutral','m1','m2','p1','p2']
            figs_ground = {}
            figs_excited = {}
            # Map your numeric chargestate_defect → folder name
            charge_map = {0:'neutral', -1:'m1', -2:'m2', 1:'p1', 2:'p2'}
            excited_charge = charge_map[chargestate_defect]
            for charge in charge_bulk:
                triplet_path = f"bulk/database/{str_defect}/{charge}/output_database.txt"
                df = pd.read_fwf(triplet_path, sep="\s+", header=None, skip_blank_lines=True)
                #### Ground states
                band_energy_spinUp_filled_triplet = []
                band_energy_spinUp_unfilled_triplet = []
                band_energy_spinDown_filled_triplet = []
                band_energy_spinDown_unfilled_triplet = []
                fermi_energy_triplet = []
                NBANDS = extract_nbands(triplet_path)
                for row in range(len(df)):
                    if row == 0 or row == NBANDS + 4:    # NBANDS + 4
                        # Extract Fermi energy
                        df2 = df.iloc[row,0].split()
                        #df_row = [ele for ele in df2 if ele.strip()]
                        if len(df2) >= 3:
                            fermi_energy_triplet.append(df2[2])
                    elif 4 <= row < NBANDS + 4:  # NBANDS + 4
                        # Spin-up bands
                        df2 = df.iloc[row, 0].split()
                        df_row = [ele for ele in df2 if ele.strip()]
                        if len(df_row) >= 3:
                            occupancy = round(float(df_row[2]))
                            energy = float(df_row[1])
                            if occupancy == 1:
                                band_energy_spinUp_filled_triplet.append(energy)
                            elif occupancy == 0:
                                band_energy_spinUp_unfilled_triplet.append(energy)
                    elif row > NBANDS + 9:  # NBANDS + 9
                        # Spin-down bands
                        df2 = df.iloc[row, 0].split()
                        # print(df2)
                        df_row = [ele for ele in df2 if ele.strip()]
                        if len(df_row) >= 3:
                            occupancy = round(float(df_row[2]))
                            energy = float(df_row[1])
                            if occupancy == 1:
                                band_energy_spinDown_filled_triplet.append(energy)
                            elif occupancy == 0:
                                band_energy_spinDown_unfilled_triplet.append(energy)

                fermi_energy_triplet = [float(i) for i in fermi_energy_triplet]
                # compute reference energies
                spin_nummer = 4
                try: 
                    upfreiplet = np.array(band_energy_spinUp_filled_triplet)

                    upunfreiplet = np.array(band_energy_spinUp_unfilled_triplet)
                        # Reference energy for filled spin-up bands (last energy below 1.24 eV)
                    triplet_ref = upfreiplet[upfreiplet < 1.24][-1]

                        # Reference energy for unfilled spin-up bands (first energy above 7.25 eV)
                    tripletunf_ref = upunfreiplet[upunfreiplet > 7.25][0]

                except IndexError:
                    triplet_ref = 1.24
                    tripletunf_ref = 7.25
            
                fup_t = [energy - triplet_ref for energy in band_energy_spinUp_filled_triplet[-spin_nummer:]]
                ufup_t = [energy - triplet_ref for energy in band_energy_spinUp_unfilled_triplet[:spin_nummer]]
                fdown_t = [energy - triplet_ref for energy in band_energy_spinDown_filled_triplet[-spin_nummer:]]
                ufdown_t = [energy - triplet_ref for energy in band_energy_spinDown_unfilled_triplet[:spin_nummer]]
                

                # build ground‐state figure
                fig_g = go.Figure()
                spin_marker_exc_fig('fup',   fup_t,    size=0.5, xcor=0.3,
                                    e_ref=triplet_ref, bandlimit=tripletunf_ref,
                                    emin=0, emax=6, fig=fig_g)  # replace emin/emax with your eemin, eemax if you compute them
                spin_marker_exc_fig('ufup',  ufup_t,   size=0.5, xcor=0.3,
                                    e_ref=triplet_ref, bandlimit=tripletunf_ref,
                                    emin=0, emax=6, fig=fig_g)
                spin_marker_exc_fig('fdown', fdown_t,  size=0.5, xcor=0.7,
                                    e_ref=triplet_ref, bandlimit=tripletunf_ref,
                                    emin=0, emax=6, fig=fig_g)
                spin_marker_exc_fig('ufdown',ufdown_t, size=0.5, xcor=0.7,
                                    e_ref=triplet_ref, bandlimit=tripletunf_ref,
                                    emin=0, emax=6, fig=fig_g)

                # layout styling
                fig_g.update_xaxes(
                    title_font = {"size": 30},
                    showgrid=False,
                    range=[0, 1],
                    showticklabels=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True
                    )

                fig_g.update_yaxes(
                    title_font = {"size": 20},
                    showgrid=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True,
                    )
                
                fig_g.update_layout(showlegend=False, 
                            xaxis_title=r"${}$".format(latexdefect),
                            yaxis_title=r"$E(eV)$ ",
                            font=dict(size=18,color="Black")
                            )

                figs_ground[charge] = fig_g
            
            # excited_path = f"bulk/database/{str_defect}/{excited_charge}/excited/output_database.txt"
            # Generic fallback path
            generic = f"bulk/database/{str_defect}/{excited_charge}/excited/output_database.txt"

            if spin_transition == "up-up":
                up_path = f"bulk/database/{str_defect}/{excited_charge}/excited_up/output_database.txt"
                if os.path.exists(up_path):
                    excited_path = up_path
                else:
                    excited_path = generic

            elif spin_transition == "down-down":
                down_path = f"bulk/database/{str_defect}/{excited_charge}/excited_down/output_database.txt"
                if os.path.exists(down_path):
                    excited_path = down_path
                else:
                    excited_path = generic

            else:
                excited_path = generic

            df_exc = pd.read_fwf(excited_path, sep="\s+", header=None, skip_blank_lines=True)  # ← unchanged
            # initialize lists (unchanged)
            band_energy_spinUp_filled_excited_triplet   = []
            band_energy_spinUp_unfilled_excited_triplet = []
            band_energy_spinDown_filled_excited_triplet = []
            band_energy_spinDown_unfilled_excited_triplet = []
            fermi_energy_excited_triplet = []

            # parse excited bands (unchanged)
            NBANDS_exc = extract_nbands(excited_path)
            for row in range(len(df_exc)):
                if row == 0 or row == NBANDS_exc + 4:
                    df2 = df_exc.iloc[row, 0].split()
                    if len(df2) >= 3:
                        fermi_energy_excited_triplet.append(df2[2])
                elif 4 <= row < NBANDS_exc + 4:
                    df2 = df_exc.iloc[row, 0].split()
                    df_row = [ele for ele in df2 if ele.strip()]
                    if len(df_row) >= 3:
                        occ = round(float(df_row[2]))
                        en  = float(df_row[1])
                        if occ == 1:
                            band_energy_spinUp_filled_excited_triplet.append(en)
                        else:
                            band_energy_spinUp_unfilled_excited_triplet.append(en)
                elif row > NBANDS_exc + 9:
                    df2 = df_exc.iloc[row, 0].split()
                    df_row = [ele for ele in df2 if ele.strip()]
                    if len(df_row) >= 3:
                        occ = round(float(df_row[2]))
                        en  = float(df_row[1])
                        if occ == 1:
                            band_energy_spinDown_filled_excited_triplet.append(en)
                        else:
                            band_energy_spinDown_unfilled_excited_triplet.append(en)

            # convert Fermi (unchanged)
            fermi_energy_excited_triplet = [float(i) for i in fermi_energy_excited_triplet]

            # compute references (you can reuse ground refs or recompute)
            try:
                upfreipletexc = np.array(band_energy_spinUp_filled_excited_triplet)
                upunfreipletexc = np.array(band_energy_spinUp_unfilled_excited_triplet)
                triplet_ref_exc     = upfreipletexc[upfreipletexc < 1.24][-1]
                tripletunf_ref_exc  = upunfreipletexc[upunfreipletexc > 7.25][0]
            except IndexError:
                triplet_ref_exc    = 1.24
                tripletunf_ref_exc = 7.25

            # shift energies (unchanged)
            fup_t_exc    = [e - triplet_ref_exc for e in band_energy_spinUp_filled_excited_triplet[-spin_nummer:]]
            ufup_t_exc   = [e - triplet_ref_exc for e in band_energy_spinUp_unfilled_excited_triplet[:spin_nummer]]
            fdown_t_exc  = [e - triplet_ref_exc for e in band_energy_spinDown_filled_excited_triplet[-spin_nummer:]]
            ufdown_t_exc = [e - triplet_ref_exc for e in band_energy_spinDown_unfilled_excited_triplet[:spin_nummer]]

            # build excited‐state figure
            fig_e = go.Figure()
            spin_marker_exc_fig('fup',   fup_t_exc,  size=0.5, xcor=0.3,
                                e_ref=triplet_ref_exc, bandlimit=tripletunf_ref_exc,
                                emin=0, emax=6, fig=fig_e)
            spin_marker_exc_fig('ufup',  ufup_t_exc, size=0.5, xcor=0.3,
                                e_ref=triplet_ref_exc, bandlimit=tripletunf_ref_exc,
                                emin=0, emax=6, fig=fig_e)
            spin_marker_exc_fig('fdown', fdown_t_exc, size=0.5, xcor=0.7,
                                e_ref=triplet_ref_exc, bandlimit=tripletunf_ref_exc,
                                emin=0, emax=6, fig=fig_e)
            spin_marker_exc_fig('ufdown',ufdown_t_exc, size=0.5, xcor=0.7,
                                e_ref=triplet_ref_exc, bandlimit=tripletunf_ref_exc,
                                emin=0, emax=6, fig=fig_e)

            # layout styling
            fig_e.update_xaxes(
                    title_font = {"size": 30},
                    showgrid=False,
                    range=[0, 1],
                    showticklabels=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True
                    )

            fig_e.update_yaxes(
                    title_font = {"size": 20},
                    showgrid=False,zeroline=False,
                    showline=True, linewidth=2, linecolor='black', mirror=True,
                    )
                
            fig_e.update_layout(showlegend=False, 
                            xaxis_title=r"${}$".format(latexdefect),
                            yaxis_title=r"$E(eV)$ ",
                            font=dict(size=18,color="Black")
                            )

            figs_excited[excited_charge] = fig_e

            # Render the six tabs
            col1, col2 = st.columns(2, gap="small")

            with col1:
                with st.container(border=True):
                    st.header('Kohn–Sham Electronic Transitions')
                    # Six tabs: five ground states + one excited state
                    tab_labels = charge_bulk + ['excited']
                    tabs = st.tabs(tab_labels)
                    for lbl, tab in zip(tab_labels, tabs):
                        with tab:
                            title = lbl if lbl != 'excited' else f"Excited ({excited_charge})"
                            st.subheader(title)
                            if lbl in figs_ground:
                                # Ground‐state figure for this charge
                                html = figs_ground[lbl].to_html(include_mathjax='cdn')
                                st.components.v1.html(html, width=530, height=600)
                            else:
                                # Single excited‐state figure
                                html = figs_excited[excited_charge].to_html(include_mathjax='cdn')
                                st.components.v1.html(html, width=530, height=600)

            with col2:
                with st.container(border=True):
                    if chargestate_defect == 0:
                        str_charge = "neutral"
                    elif chargestate_defect == -1:
                        str_charge = "m1"
                    elif chargestate_defect == -2:
                        str_charge = "m2"
                    elif chargestate_defect == 1:
                        str_charge = "p1"
                    elif chargestate_defect == 2:
                        str_charge = "p2"
                    
                    

                    if spin_transition == "up-up":
                        atomposition_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited_up/CONTCAR_cartesian"
                        if os.path.exists(atomposition_excited_triplet):
                            fractional_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited_up/CONTCAR_fractional"
                            cif_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited_up/structure.cif"
                        else:
                            atomposition_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_cartesian"
                            fractional_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_fractional"
                            cif_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/structure.cif"

                    elif spin_transition == "down-down":
                        atomposition_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited_down/CONTCAR_cartesian"
                        if os.path.exists(atomposition_excited_triplet):
                            fractional_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited_down/CONTCAR_fractional"
                            cif_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited_down/structure.cif"
                        else:
                            atomposition_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_cartesian"
                            fractional_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_fractional"
                            cif_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/structure.cif"

                    else:
                        atomposition_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_cartesian"
                        fractional_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_fractional"
                        cif_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/structure.cif"

                    atomposition_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/CONTCAR_cartesian"
                    #atomposition_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_cartesian"

                    fractional_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/CONTCAR_fractional"
                    #fractional_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/CONTCAR_fractional"

                    cif_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/structure.cif"
                    #cif_excited_triplet = "bulk/database/" + str_defect + "/" + str_charge + "/excited/structure.cif"
            
                    ########################## atomic position data frame  ###################################
                    if  type(chosen_defect) == str:
                        latexdefect = 'Al_N'
                        atomicposition_sin = pd.read_csv("monolayer/database_triplet/" + 'AlN' + "/triplet/CONTCAR_cartesian",sep=';', header=0)        
                    else:
                        try: 
                            atomicposition_sin = pd.read_csv(atomposition_triplet,sep=';', header=0)
                        except NameError or ValueError:
                            latexdefect = 'Al_N'
                            atomicposition_sin = pd.read_csv("monolayer/database_triplet/" + str_defect + "/triplet/CONTCAR_cartesian",sep=';', header=0)
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
                    st.header(f"Atomic positions of ${latexdefect}^{{{chargestate_defect}}}$")    
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
                    dipole = load_table('updated_data')
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
                    
                    ctrystal_axes_start = np.array([4.979,5.749,5.00298])
                    ctrystal_axes_start2=np.array([4.979,1.749,5.00298])
                    ctrystal_axes_end = np.array([4.979,9.749,5.00298])-ctrystal_axes_start
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
                    tail=np.array([4.979,5.749,5.00298])

                    head=head+ctrystal_axes_start
                    ctrystal_axes_end= ctrystal_axes_end+ctrystal_axes_start        

                    fig3D.add_trace(go.Cone(x=[head[0]], y=[head[1]], z=[head[2]], u=[head[0]-tail[0]], v=[head[1]-tail[1]], w=[head[2]-tail[2]],
                                            colorscale='ylorrd',showscale=False,hoverinfo='skip',sizeref=0.2))
                    fig3D.add_trace(go.Scatter3d(x=[tail[0],head[0]], y=[tail[1],head[1]],z=[tail[2],head[2]],hoverinfo ='skip',marker=dict(size=3, color='yellow'),
                                                line=dict(color='orange',width=6),showlegend=True,name="Emission"))
                    fig3D.add_trace(go.Scatter3d(x=[ctrystal_axes_start2[0],ctrystal_axes_end[0]], y=[ctrystal_axes_start2[1],ctrystal_axes_end[1]],z=[ctrystal_axes_start2[2],ctrystal_axes_end[2]],
                                                hoverinfo ='skip', marker=dict(size=1, color='red'), line=dict(color='red',width=5,dash='dot'),showlegend=True,name="Crystal Axis"))
                    
                    ## ploting Excitation Dipole
                    ctrystal_axes_end = np.array([4.979,9.749,5.00298])-ctrystal_axes_start
                    # rotate z-axis
                    c, s = np.cos(phi_exc), np.sin(phi_exc)
                    r_z = np.array(((c,-s,0), (s,c,0), (0,0,1)))
                    # rotate x-axis
                    c, s = np.cos(theta_exc), np.sin(theta_exc)
                    r_x = np.array(((1,0,0), (0,c, -s), (0,s, c)))

                    r_xz=np.dot(r_x,r_z)
                    head = np.dot(r_xz,ctrystal_axes_end)  #ctrystal_axes_end
                    tail=np.array([4.979,5.749,5.00298])
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
            ######## Formation energy
            path_formationE_Nrich = "bulk/database/" + str_defect + "/formation_energies_N_rich.txt"
            path_formationE_Npoor = "bulk/database/" + str_defect + "/formation_energies_N_poor.txt"
            # Load both files
            rich_data = read_formation_energies(path_formationE_Nrich)
            poor_data = read_formation_energies(path_formationE_Npoor)
            # Fermi level range (0 to 6 eV)
            E_F = np.linspace(0, 6, 200) 
            # Assign colors for charge states
                    # You can customize this list as needed
            color_palette = pc.qualitative.D3  # or Set1, Set2, etc.
            charge_states = sorted(set(state['charge'] for defect in rich_data.values() for state in defect))
            color_map = {q: color_palette[i % len(color_palette)] for i, q in enumerate(charge_states)}
            
                    # Plot and render N-rich diagram
            fig_rich = plot_diagram_plotly(rich_data, 'Defect Formation Energies (N-rich)')
                    # Plot and render N-poor diagram
            fig_poor = plot_diagram_plotly(poor_data, 'Defect Formation Energies (N-poor)')

            ######## for displaying defect formation energy and PL
            col3, col4 = st.columns(2,gap="medium")
            with col3:
                with st.container(border=True):
                    st.header("Defect Formation Energy of "+"${}$".format(latexdefect))
                    tab1, tab2 = st.tabs(["N-rich","N-poor"])
                    with tab1:                
                        st.plotly_chart(fig_rich, use_container_width=True,theme=None)   #  
                    with tab2: 
                        st.plotly_chart(fig_poor, use_container_width=True, theme=None)   #  ← change
            
            ###### for PL spectrum
            # Path to the PL file
            generic_PL = "bulk/database/" + str_defect + "/" + str_charge + "/PL.txt" 
            if spin_transition == "up-up":
                up_path = "bulk/database/" + str_defect + "/" + str_charge + "/PL_up.txt" 
                if os.path.exists(up_path):
                    path_PL = up_path
                else:
                    path_PL = generic_PL

            elif spin_transition == "down-down":
                down_path = "bulk/database/" + str_defect + "/" + str_charge + "/PL_down.txt" 
                if os.path.exists(down_path):
                    path_PL = down_path
                else:
                    path_PL = generic_PL

            else:
                path_PL = generic_PL

            with col4:
                with st.container(border=True):
                    #st.header("Luminescence spectrum of "+"${}$".format(latexdefect)+chargestate_defect)
                    st.header(f"Luminescence spectrum of ${latexdefect}^{{{chargestate_defect}}}$")
                    tab1, tab2 = st.tabs(["Photoluminescence","Absorption"])
                    with tab1:
                                # Check if the file exists
                        if os.path.exists(path_PL):
                                    # Load the data
                            data = np.loadtxt(path_PL)
                            wavelength = data[:, 0]
                            intensity = data[:, 1]

                                    # Create the figure
                            fig = go.Figure()

                            fig.add_trace(go.Scatter(
                                        x=wavelength,
                                        y=intensity,
                                        mode='lines',
                                        line=dict(width=2, color='orange'),
                                        name='PL Spectrum'
                                    ))

                                    # Update axes and layout
                            fig.update_xaxes(
                                        title='Wavelength (nm)',
                                        title_font={"size": 18},
                                        showline=True,
                                        linewidth=2,
                                        linecolor='black',
                                        mirror=True
                                    )
                            fig.update_yaxes(
                                        title='PL Intensity (arb. units)',
                                        title_font={"size": 18},
                                        showline=True,
                                        linewidth=2,
                                        linecolor='black',
                                        zeroline = False,
                                        mirror=True
                                    )

                            fig.update_layout(
                                        font=dict(size=16, color="black"),
                                        width=600,
                                        height=500,
                                        margin=dict(l=70, r=70, t=30, b=90),
                                        showlegend=False
                                    )                
                            st.components.v1.html(fig.to_html(include_mathjax='cdn'),width=550, height=600)
                        else:
                                    # Show a message if file is not found
                            st.write(f"**Photoluminescence absent owing to a lack of two-level defect states.**")

                    with tab2:
                                # Check if the file exists
                        if os.path.exists(path_PL):
                                    # Load the data
                            data = np.loadtxt(path_PL)
                            wavelength = data[:, 0]
                            intensity = data[:, 1]
                                    # Find the index of maximum PL intensity
                            max_index = np.argmax(intensity)
                                    # ZPL wavelength is the wavelength corresponding to max intensity
                            ZPL_wavelength = wavelength[max_index]
                                    # Mirror wavelengths about the ZPL
                            wavelength_mirrored = 2 * ZPL_wavelength - wavelength

                                    # Optional: sort the mirrored data by ascending wavelength for clean plotting
                            sorted_indices = np.argsort(wavelength_mirrored)
                            wavelength_mirrored_sorted = wavelength_mirrored[sorted_indices]
                            intensity_sorted = intensity[sorted_indices]

                                    # Create the figure
                            fig = go.Figure()

                            fig.add_trace(go.Scatter(
                                        x=wavelength_mirrored_sorted,
                                        y=intensity_sorted,
                                        mode='lines',
                                        line=dict(width=2, color='orange'),
                                        name='PL Spectrum'
                                    ))

                                    # Update axes and layout
                            fig.update_xaxes(
                                        title='Wavelength (nm)',
                                        title_font={"size": 18},
                                        showline=True,
                                        zeroline = False,
                                        linewidth=2,
                                        linecolor='black',
                                        mirror=True
                                    )
                            fig.update_yaxes(
                                        title='Normalized Intensity (arb. units)',
                                        title_font={"size": 18},
                                        showline=True,
                                        linewidth=2,
                                        zeroline = False,
                                        linecolor='black',
                                        mirror=True
                                    )

                            fig.update_layout(
                                        font=dict(size=16, color="black"),
                                        width=600,
                                        height=500,
                                        margin=dict(l=100, r=70, t=30, b=90),
                                        showlegend=False
                                    )                
                            st.components.v1.html(fig.to_html(include_mathjax='cdn'),width=550, height=600)
                        else:
                                    # Show a message if file is not found
                            st.write(f"**Absorption spectrum absent owing to a lack of two-level defect states.**")
            
            ######## for displaying 2 tables
            col5, col6 = st.columns(2,gap="medium")
            with col5:
                with st.container(border=True):
                    st.header(f"Photophysical properties of "+"${}$".format(latexdefect))
                            # col21, col22, col23 = st.columns(3)
                    tab1, tab2, tab3 = st.tabs(["Excitation Properties", "Emission Properties", "Quantum Memory Properties"])
                            ## col21
                            #tab1.subheader('Excitation Properties')
                    Photophysical_properties = load_table('Excitation properties')
                    Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
                    refr_index = st.session_state.get("refractive_index", 1.85)
                    Photophysical_properties["Characteristic time (ns)"] = (
                        Photophysical_properties["Characteristic time (ns)"]
                        .astype(float)
                        * (1.85 / refr_index)
                    )

                    Photophysical_properties["Characteristic time (ns)"] = (
                        Photophysical_properties["Characteristic time (ns)"]
                        .astype(int)                # uncomment if you want full precision
                        .map("{:.2E}".format)
                    )

                    # Photophysical_properties["Characteristic time (ns)"]=Photophysical_properties["Characteristic time (ns)"].astype(int)
                    # Photophysical_properties["Characteristic time (ns)"] = Photophysical_properties["Characteristic time (ns)"].map("{:.2E}".format)

                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargestate_defect) & (Photophysical_properties['Host'] =='bulk')]
                    except  NameError :
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='bulk')]
                    except  KeyError:
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='bulk')]
                    
                    
                    # 1) Pick off Host plus your other columns
                    cols = ['Host'] + list(ppdefects.columns[3:])  # Take host column and every column after the 3rd one

                    # 2) Slice and rename in one go
                    ep2 = (
                        ppdefects[cols]
                        .rename(columns={
                            "dipole_x": "µₓ (Debye)",
                            "dipole_y": "μᵧ (Debye)",
                            "dipole_z": "µz (Debye)",
                            "Intensity": "Intensity (Debye)",
                            "Angle of excitation dipole wrt the crystal axis":
                                "Angle of excitation dipole wrt the crystal axis (degree)"
                        })
                        
                    )
                    ##ep2 = ep2.T
                    ep2 = ep2.T.astype(str) ## corrected the conversion error 31.07.2025
                    # 3) Rebuild your `[Value i]` headers
                    jj =1
                    newheadcol =[]
                    for head in ep2.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    ep2.columns =newheadcol
                    # 4) Display
                    tab1.dataframe(ep2, use_container_width=True)

                            ## col22
                            #col22.subheader('Emission Properties')

                    Photophysical_properties = load_table('Emission properties')
                    Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
                    Photophysical_properties["ZPL (nm)"]=Photophysical_properties["ZPL (nm)"].astype(int)

                    refr_index = st.session_state.get("refractive_index", 1.85)
                    Photophysical_properties["Lifetime (ns)"] = (
                        Photophysical_properties["Lifetime (ns)"]
                        .astype(float)
                        * (1.85 / refr_index)
                    )

                    Photophysical_properties["Lifetime (ns)"] = (
                        Photophysical_properties["Lifetime (ns)"]
                        .astype(int)
                        .map("{:.2E}".format)
                    )

                    # Photophysical_properties["Lifetime (ns)"]=Photophysical_properties["Lifetime (ns)"].astype(int)
                    # Photophysical_properties["Lifetime (ns)"] = Photophysical_properties["Lifetime (ns)"].map("{:.2E}".format)
                    Photophysical_properties["Configuration coordinate (amu^(1/2) \AA)"]=Photophysical_properties["Configuration coordinate (amu^(1/2) \AA)"]
                    Photophysical_properties["Ground-state total energy (eV)"]=Photophysical_properties["Ground-state total energy (eV)"]
                    Photophysical_properties["Excited-state total energy (eV)"]=Photophysical_properties["Excited-state total energy (eV)"]

                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargestate_defect) & (Photophysical_properties['Host'] =='bulk')]
                    except  NameError :
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='bulk')]
                    except  KeyError:
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='bulk')]
                    emp=ppdefects.iloc[:,3:]
                    emp.rename(columns={"dipole_x":"µₓ (Debye)","dipole_y":"μᵧ (Debye)","dipole_z":"µz (Debye)","Intensity":"Intensity (Debye)","Angle of emission dipole wrt the crystal axis":"Angle of emission dipole wrt the crystal axis (degree)","Configuration coordinate (amu^(1/2) \AA)":"Configuration coordinate (amu^(1/2) Å)","Ground-state total energy (eV)":"Ground-state total energy (eV)","Excited-state total energy (eV)":"Excited-state total energy (eV)"},inplace=True)
                    ###emp=emp.T
                    emp=emp.T.astype(str) # Fixed 31.07.2025
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
                    Photophysical_properties = load_table('Quantum memory properties')
                    Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
                    Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"]=Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].astype(int)
                    Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"] = Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].map("{:.2E}".format)
                    Photophysical_properties["g (MHz)"]=Photophysical_properties["g (MHz)"].astype(int)
                    Photophysical_properties["g (MHz)"] = Photophysical_properties["g (MHz)"].map("{:.2E}".format)
                        
                    try: 
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])& (Photophysical_properties['Host'] =='bulk')]
                    except  NameError :
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='bulk')]
                    except  KeyError:
                        ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='bulk')]
                    qmp = ppdefects.iloc[:,3:]
                    ###qmp=qmp.T
                    qmp=qmp.T.astype(str) ## Fixed 31.07.2025
                    jj =1
                    newheadcol =[]
                            #latppdefects.iloc[1,0].replace("$","")
                    for head in qmp.iloc[0]:
                        newheadcol.append('[Value {i}]'.format(i=jj))
                        jj+=1
                    qmp.columns =newheadcol
                    tab3.dataframe(qmp,use_container_width=True)
            with col6:
                with st.container(border=True):
                    st.header('Computational setting')
                    df = pd.DataFrame(
                                {
                                    "Computational Setting": ["DFT calculator", "Functional", "Pseudopotentials","Cutoff Energy","Kpoint",
                                                            "Supercell size", "Energy convergence","Force convergence","Van der Waals force" ],
                                    "Value": ["VASP", "HSE(α=0.32)", "PAW","500 eV","Γ point","6x6x4","1e-4 eV","0.01 eV/Å","DFT-D3"]
                                }
                            )
                    st.dataframe(df, hide_index=True)



        elif host == 'monolayer':
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

                if spin_multiplicity == 'singlet' and host=='monolayer':
                    triplet_path = "monolayer/database_doublet_singlet/" + str_defect + "/singlet/ground/output_database.txt"
                    excited_triplet_path= "monolayer/database_doublet_singlet/" + str_defect + "/singlet/excited/output_database.txt"

                    atomposition_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/singlet/ground/CONTCAR_cartesian"
                    atomposition_excited_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/singlet/excited/CONTCAR_cartesian"

                    fractional_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/singlet/ground/CONTCAR_fractional"
                    fractional_excited_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/singlet/excited/CONTCAR_fractional"

                    cif_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/singlet/ground/structure.cif"
                    cif_excited_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/singlet/excited/structure.cif"

                elif spin_multiplicity == 'doublet' and host=='monolayer':
                    triplet_path = "monolayer/database_doublet_singlet/" + str_defect + "/doublet/ground/output_database.txt"
                    excited_triplet_path= "monolayer/database_doublet_singlet/" + str_defect + "/doublet/excited/output_database.txt"

                    atomposition_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/doublet/ground/CONTCAR_cartesian"
                    atomposition_excited_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/doublet/excited/CONTCAR_cartesian"

                    fractional_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/doublet/ground/CONTCAR_fractional"
                    fractional_excited_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/doublet/excited/CONTCAR_fractional"

                    cif_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/doublet/ground/structure.cif"
                    cif_excited_triplet = "monolayer/database_doublet_singlet/" + str_defect + "/doublet/excited/structure.cif"
                
                # Band structure
                ########## Ground State ###
                #df = pd.read_fwf(triplet_path, sep=" ",header=None)  
                df = pd.read_fwf(triplet_path, sep="\s+", header=None, skip_blank_lines=True)
                # Extract NBANDS automatically from the OUTCAR_transition file

                band_energy_spinUp_filled_triplet = []
                band_energy_spinUp_unfilled_triplet = []
                band_energy_spinDown_filled_triplet = []
                band_energy_spinDown_unfilled_triplet = []
                fermi_energy_triplet = []
                if host == 'monolayer':
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
                elif host == 'bulk':
                    NBANDS = extract_nbands(triplet_path)
                    for row in range(len(df)):
                        if row == 0 or row == NBANDS + 4:    # NBANDS + 4
                            # Extract Fermi energy
                            df2 = df.iloc[row,0].split()
                            #df_row = [ele for ele in df2 if ele.strip()]
                            if len(df2) >= 3:
                                fermi_energy_triplet.append(df2[2])
                        elif 4 <= row < NBANDS + 4:  # NBANDS + 4
                            # Spin-up bands
                            df2 = df.iloc[row, 0].split()
                            df_row = [ele for ele in df2 if ele.strip()]
                            if len(df_row) >= 3:
                                occupancy = round(float(df_row[2]))
                                energy = float(df_row[1])
                                if occupancy == 1:
                                    band_energy_spinUp_filled_triplet.append(energy)
                                elif occupancy == 0:
                                    band_energy_spinUp_unfilled_triplet.append(energy)
                        elif row > NBANDS + 9:  # NBANDS + 9
                            # Spin-down bands
                            df2 = df.iloc[row, 0].split()
                            # print(df2)
                            df_row = [ele for ele in df2 if ele.strip()]
                            if len(df_row) >= 3:
                                occupancy = round(float(df_row[2]))
                                energy = float(df_row[1])
                                if occupancy == 1:
                                    band_energy_spinDown_filled_triplet.append(energy)
                                elif occupancy == 0:
                                    band_energy_spinDown_unfilled_triplet.append(energy)
                                    
                ###### Excited State ###
                #df = pd.read_fwf(excited_triplet_path, sep=" ",header=None)  
                df = pd.read_fwf(excited_triplet_path, sep="\s+", header=None, skip_blank_lines=True)

                band_energy_spinUp_filled_excited_triplet = []
                band_energy_spinUp_unfilled_excited_triplet = []
                band_energy_spinDown_filled_excited_triplet = []
                band_energy_spinDown_unfilled_excited_triplet = []
                fermi_energy_excited_triplet_path = []
                if host == 'monolayer':
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
                elif host == 'bulk':
                    NBANDS = extract_nbands(excited_triplet_path)
                    for row in range(len(df)):
                        if row == 0 or row == NBANDS + 4:    # NBANDS + 4
                            # Extract Fermi energy
                            df2 = df.iloc[row,0].split()
                            #df_row = [ele for ele in df2 if ele.strip()]
                            if len(df2) >= 3:
                                fermi_energy_excited_triplet.append(df2[2])
                        elif 4 <= row < NBANDS + 4:  # NBANDS + 4
                            # Spin-up bands
                            df2 = df.iloc[row, 0].split()
                            df_row = [ele for ele in df2 if ele.strip()]
                            if len(df_row) >= 3:
                                occupancy = round(float(df_row[2]))
                                energy = float(df_row[1])
                                if occupancy == 1:
                                    band_energy_spinUp_filled_excited_triplet.append(energy)
                                elif occupancy == 0:
                                    band_energy_spinUp_unfilled_excited_triplet.append(energy)
                        elif row > NBANDS + 9:  # NBANDS + 9
                            # Spin-down bands
                            df2 = df.iloc[row, 0].split()
                            # print(df2)
                            df_row = [ele for ele in df2 if ele.strip()]
                            if len(df_row) >= 3:
                                occupancy = round(float(df_row[2]))
                                energy = float(df_row[1])
                                if occupancy == 1:
                                    band_energy_spinDown_filled_excited_triplet.append(energy)
                                elif occupancy == 0:
                                    band_energy_spinDown_unfilled_excited_triplet.append(energy)


                fermi_energy_triplet = [float(i) for i in fermi_energy_triplet]
                fermi_energy_excited_triplet = [float(i) for i in fermi_energy_excited_triplet]

                spin_nummer = 4
                if host == 'monolayer':
                    try: 
                        upfreiplet = np.array(band_energy_spinUp_filled_triplet)
                        upfreipletexc = np.array(band_energy_spinUp_filled_excited_triplet)

                        upunfreiplet = np.array(band_energy_spinUp_unfilled_triplet)
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

                #all_band_energy = np.concatenate([fup_t_exc,fup_t,ufup_t,ufup_t_exc,fdown_t,fdown_t_exc,ufdown_t,ufdown_t_exc])
                all_band_energy = np.concatenate([fup_t,fup_t_exc,ufup_t,ufup_t_exc,fdown_t,fdown_t_exc,ufdown_t,ufdown_t_exc])

                try:
                    eemin = np.min(all_band_energy)
                    eemax = np.max(all_band_energy)
                except ValueError:  #raised if `y` is empty.
                    eemin =0
                    eemax =6

                def spin_marker_exc_fig (spinstate, band_energy, size, xcor, e_ref , bandlimit ,emin, emax,fig):
                    fig2=fig
                    scale =32
                    delta = -0.04
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
                    name_change = load_table('updated_data')
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
                            atomicposition_sin = pd.read_csv("monolayer/database_triplet/" + 'AlN' + "/triplet/CONTCAR_cartesian",sep=';', header=0)        
                        else:
                            try: 
                                atomicposition_sin = pd.read_csv(atomposition_triplet,sep=';', header=0)
                            except NameError or ValueError:
                                ## latexdefect = 'Al_N'
                                if host == 'monolayer':
                                    atomicposition_sin = pd.read_csv("monolayer/database_triplet/" + str_defect + "/triplet/CONTCAR_cartesian",sep=';', header=0)
                                elif host == 'bulk':
                                    atomicposition_sin = pd.read_csv("bulk/database/" + str_defect + "/triplet/CONTCAR_cartesian",sep=';', header=0)
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
                        st.header("Atomic positions for ${}$".format(latexdefect))    
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
                        dipole = load_table('updated_data')
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
                        if host == 'monolayer':
                            ctrystal_axes_start = np.array([3.736,7.960,1.668])
                            ctrystal_axes_start2=np.array([3.736,3.960,1.668])
                            ctrystal_axes_end = np.array([3.736,11.960,1.668])-ctrystal_axes_start
                        elif host == 'bulk':
                            ctrystal_axes_start = np.array([4.979,5.749,5.00298])
                            ctrystal_axes_start2=np.array([4.979,1.749,5.00298])
                            ctrystal_axes_end = np.array([4.979,9.749,5.00298])-ctrystal_axes_start

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
                        if host == 'monolayer':
                            tail=np.array([3.736,7.960,1.668])
                        elif host == 'bulk':
                            tail=np.array([4.979,5.749,5.00298])

                        head=head+ctrystal_axes_start
                        ctrystal_axes_end= ctrystal_axes_end+ctrystal_axes_start        

                        fig3D.add_trace(go.Cone(x=[head[0]], y=[head[1]], z=[head[2]], u=[head[0]-tail[0]], v=[head[1]-tail[1]], w=[head[2]-tail[2]],
                                                colorscale='ylorrd',showscale=False,hoverinfo='skip',sizeref=0.2))
                        fig3D.add_trace(go.Scatter3d(x=[tail[0],head[0]], y=[tail[1],head[1]],z=[tail[2],head[2]],hoverinfo ='skip',marker=dict(size=3, color='yellow'),
                                                    line=dict(color='orange',width=6),showlegend=True,name="Emission"))
                        fig3D.add_trace(go.Scatter3d(x=[ctrystal_axes_start2[0],ctrystal_axes_end[0]], y=[ctrystal_axes_start2[1],ctrystal_axes_end[1]],z=[ctrystal_axes_start2[2],ctrystal_axes_end[2]],
                                                    hoverinfo ='skip', marker=dict(size=1, color='red'), line=dict(color='red',width=5,dash='dot'),showlegend=True,name="Crystal Axis"))
                        
                        ## ploting Excitation Dipole
                        if host == 'monolayer':
                            ctrystal_axes_end = np.array([3.736,11.960,1.668])-ctrystal_axes_start
                        elif host == 'bulk':
                            ctrystal_axes_end = np.array([4.979,9.749,5.00298])-ctrystal_axes_start

                        # rotate z-axis
                        c, s = np.cos(phi_exc), np.sin(phi_exc)
                        r_z = np.array(((c,-s,0), (s,c,0), (0,0,1)))
                        # rotate x-axis
                        c, s = np.cos(theta_exc), np.sin(theta_exc)
                        r_x = np.array(((1,0,0), (0,c, -s), (0,s, c)))

                        r_xz=np.dot(r_x,r_z)
                        head = np.dot(r_xz,ctrystal_axes_end)  #ctrystal_axes_end
                        if host == 'monolayer':
                            tail=np.array([3.736,7.960,1.668])
                        elif host == 'bulk':
                            tail=np.array([4.979,5.749,5.00298])

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
                
                col_raman = st.columns(1)
                with col_raman[0]:
                    with st.container(border=True):
                        st.header("Raman Spectrum")
                        raman_peak = []  # Initialize list to store peaks
                        raman_path = None

                        # Determine file path
                        if chosen_chargestate == ["neutral"] and spin_multiplicity == 'doublet':
                            raman_path = f"monolayer/database_doublet_singlet/{str_defect}/doublet/vasp_raman.dat-broaden.dat"

                        elif chosen_chargestate == ["neutral"] and spin_multiplicity == 'singlet':
                            raman_path = f"monolayer/database_doublet_singlet/{str_defect}/singlet/vasp_raman.dat-broaden.dat"
                
                        else:
                            st.write("**Raman spectrum is not available for this defect**")

                        # Load and plot Raman spectrum if file exists
                        if raman_path and os.path.exists(raman_path):
                            data_1 = np.loadtxt(raman_path)
                            wavenumber_1 = data_1[:, 0]
                            spectrum_1 = data_1[:, 1]

                            # Find peaks where intensity == 1
                            for k in range(len(spectrum_1)):
                                if spectrum_1[k] == 1:
                                    raman_peak.append(wavenumber_1[k])

                            # Create interactive Plotly figure
                            fig = go.Figure()

                            fig.add_trace(go.Scatter(
                                x=wavenumber_1,
                                y=spectrum_1,
                                mode='lines',
                                name='Raman Spectrum',
                                line=dict(width=2)
                            ))

                            # Add annotations for each peak
                            for peak in raman_peak:
                                fig.add_annotation(
                                    x=peak,
                                    y=1,
                                    text=f"{peak:.0f}",
                                    showarrow=True,
                                    arrowhead=1,
                                    ax=0,
                                    ay=-40,
                                    font=dict(size=10)
                                )

                            fig.update_layout(
                                xaxis_title='Raman shift (cm⁻¹)',
                                yaxis_title='Intensity (a.u.)',
                                xaxis_range=[100, 1700],
                                yaxis_range=[-0.05, 1.1],
                                height=500,
                                margin=dict(l=40, r=40, t=40, b=40),
                                showlegend=True
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        elif raman_path:
                            st.write("**Raman spectrum is not available for this defect.**")
                
                if host == 'monolayer':
                    col3, col4 = st.columns(2,gap="medium")
                    with col3:
                        with st.container(border=True):
                            st.header("Photophysical properties of "+"${}$".format(latexdefect))
                            # col21, col22, col23 = st.columns(3)
                            tab1, tab2, tab3 = st.tabs(["Excitation Properties", "Emission Properties", "Quantum Memory Properties"])
                            ## col21
                            #tab1.subheader('Excitation Properties')
                            Photophysical_properties = load_table('Excitation properties')
                            Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
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

                            Photophysical_properties = load_table('Emission properties')
                            Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
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
                            Photophysical_properties = load_table('Quantum memory properties')
                            Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
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

                if chosen_chargestate == ["neutral"] and host=='monolayer':
                    singlet_path = "monolayer/database_triplet/" + str_defect + "/singlet/output_database.txt"
                    triplet_path = "monolayer/database_triplet/" + str_defect + "/triplet/output_database.txt"
                    excited_triplet_path= "monolayer/database_triplet/" + str_defect + "/excited_triplet/output_database.txt"

                    atomposition_singlet = "monolayer/database_triplet/" + str_defect + "/singlet/CONTCAR_cartesian"
                    atomposition_triplet = "monolayer/database_triplet/" + str_defect + "/triplet/CONTCAR_cartesian"
                    atomposition_excited_triplet = "monolayer/database_triplet/" + str_defect + "/excited_triplet/CONTCAR_cartesian"

                    fractional_singlet = "monolayer/database_triplet/" + str_defect + "/singlet/CONTCAR_fractional"
                    fractional_triplet = "monolayer/database_triplet/" + str_defect + "/triplet/CONTCAR_fractional"
                    fractional_excited_triplet = "monolayer/database_triplet/" + str_defect + "/excited_triplet/CONTCAR_fractional"

                    cif_singlet = "monolayer/database_triplet/" + str_defect + "/singlet/structure.cif"
                    cif_triplet = "monolayer/database_triplet/" + str_defect + "/triplet/structure.cif"
                    cif_excited_triplet = "monolayer/database_triplet/" + str_defect + "/excited_triplet/structure.cif"

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
                            try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_down/output_database.txt"
                            df = pd.read_fwf(try1, sep=" ",header=None)
                        elif spin_transition =="up-up":
                            try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_up/output_database.txt"
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
                                

                elif (chosen_chargestate == ["charge_positive_1"]  or chosen_chargestate == ["charge_negative_1"]) and host=='monolayer':
                    singlet_path = "monolayer/database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/singlet/output_database.txt"
                    triplet_path = "monolayer/database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/triplet/output_database.txt"
                    excited_triplet_path = "monolayer/database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/excited_triplet/output_database.txt"

                    atomposition_singlet = "monolayer/database_triplet/" + str_defect + "/" + chosen_chargestate[0]+ "/singlet/CONTCAR_cartesian"
                    atomposition_triplet = "monolayer/database_triplet/" + str_defect + "/" + chosen_chargestate[0]+ "/triplet/CONTCAR_cartesian"
                    atomposition_excited_triplet = "monolayer/database_triplet/" + str_defect + "/" + chosen_chargestate[0]+ "/excited_triplet/CONTCAR_cartesian"

                    fractional_singlet = "monolayer/database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/singlet/CONTCAR_fractional"
                    fractional_triplet = "monolayer/database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/triplet/CONTCAR_fractional"
                    fractional_excited_triplet = "monolayer/database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/excited_triplet/CONTCAR_fractional"

                    cif_singlet = "monolayer/database_triplet/" + str_defect + "/" + chosen_chargestate[0]+"/singlet/structure.cif"
                    cif_triplet = "monolayer/database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/triplet/structure.cif"
                    cif_excited_triplet = "monolayer/database_triplet/" + str_defect +"/" + chosen_chargestate[0]+ "/excited_triplet/structure.cif"

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
                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                                df = pd.read_fwf(try1, sep=" ",header=None)
                            elif spin_transition =="up-up":
                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                                df = pd.read_fwf(try1, sep=" ",header=None)
                        elif chosen_chargestate == ["charge_positive_1"]:
                            if spin_transition =="down-down":
                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                                df = pd.read_fwf(try1, sep=" ",header=None)
                            elif spin_transition =="up-up":
                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
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
                    name_change = load_table('updated_data')
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
                            atomicposition_sin = pd.read_csv("monolayer/database_triplet/" + 'AlN' + "/triplet/CONTCAR_cartesian",sep=';', header=0)        
                        else:
                            try: 
                                atomicposition_sin = pd.read_csv(atomposition_triplet,sep=';', header=0)
                            except NameError or ValueError:
                                latexdefect = 'Al_N'
                                atomicposition_sin = pd.read_csv("monolayer/database_triplet/" + str_defect + "/triplet/CONTCAR_cartesian",sep=';', header=0)
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
                        dipole = load_table('updated_data')
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
                                        try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_down/CONTCAR_cartesian"                        
                                    elif spin_transition =="up-up":
                                        try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_up/CONTCAR_cartesian"
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
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                                            elif spin_transition =="up-up":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                                        elif chosen_chargestate == ["charge_positive_1"]:
                                            if spin_transition =="down-down":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                                            elif spin_transition =="up-up":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
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
                                        try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_down/CONTCAR_fractional"                        
                                    elif spin_transition =="up-up":
                                        try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_up/CONTCAR_fractional"
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
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                                            elif spin_transition =="up-up":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                                        elif chosen_chargestate == ["charge_positive_1"]:
                                            if spin_transition =="down-down":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                                            elif spin_transition =="up-up":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
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
                                        try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_down/structure.cif"                        
                                    elif spin_transition =="up-up":
                                        try1 = "monolayer/database_triplet/" + str_defect + "/excited_triplet_up/structure.cif"
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
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_down/output_database.txt"
                                            elif spin_transition =="up-up":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_negative_1/excited_triplet_up/output_database.txt"
                                        elif chosen_chargestate == ["charge_positive_1"]:
                                            if spin_transition =="down-down":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_down/output_database.txt"
                                            elif spin_transition =="up-up":
                                                try1 = "monolayer/database_triplet/" + str_defect + "/charge_positive_1/excited_triplet_up/output_database.txt"
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
                col_raman = st.columns(1)
                with col_raman[0]:
                    with st.container(border=True):
                        st.header("Raman Spectrum")
                        raman_peak = []  # Initialize list to store peaks
                        raman_path = None

                        # Determine file path
                        if chosen_chargestate == ["neutral"] and spin_multiplicity == 'triplet':
                            raman_path = f"monolayer/database_triplet/{str_defect}/triplet/vasp_raman.dat-broaden.dat"

                        elif chosen_chargestate == ["neutral"] and spin_multiplicity == 'singlet':
                            raman_path = f"monolayer/database_triplet/{str_defect}/singlet/vasp_raman.dat-broaden.dat"
         
                        elif chosen_chargestate == ["charge_negative_1"] and spin_multiplicity == 'triplet':
                            raman_path = f"monolayer/database_triplet/{str_defect}/{chosen_chargestate[0]}/triplet/vasp_raman.dat-broaden.dat"

                        else:
                            st.write("**Raman spectrum is not available for this defect**")

                        # Load and plot Raman spectrum if file exists
                        if raman_path and os.path.exists(raman_path):
                            data_1 = np.loadtxt(raman_path)
                            wavenumber_1 = data_1[:, 0]
                            spectrum_1 = data_1[:, 1]

                            # Find peaks where intensity == 1
                            for k in range(len(spectrum_1)):
                                if spectrum_1[k] == 1:
                                    raman_peak.append(wavenumber_1[k])

                            # Create interactive Plotly figure
                            fig = go.Figure()

                            fig.add_trace(go.Scatter(
                                x=wavenumber_1,
                                y=spectrum_1,
                                mode='lines',
                                name='Raman Spectrum',
                                line=dict(width=2)
                            ))

                            # Add annotations for each peak
                            for peak in raman_peak:
                                fig.add_annotation(
                                    x=peak,
                                    y=1,
                                    text=f"{peak:.0f}",
                                    showarrow=True,
                                    arrowhead=1,
                                    ax=0,
                                    ay=-40,
                                    font=dict(size=10)
                                )

                            fig.update_layout(
                                xaxis_title='Raman shift (cm⁻¹)',
                                yaxis_title='Intensity (a.u.)',
                                xaxis_range=[100, 1700],
                                yaxis_range=[-0.05, 1.1],
                                height=500,
                                margin=dict(l=40, r=40, t=40, b=40),
                                showlegend=True
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        elif raman_path:
                            st.write("**Raman spectrum is not available for this defect.**")


                col3, col4 = st.columns(2,gap="medium")
                with col3:
                    with st.container(border=True):
                        st.header("Photophysical properties of "+"${}$".format(latexdefect))
                        # col21, col22, col23 = st.columns(3)
                        tab1, tab2, tab3 = st.tabs(["Excitation Properties", "Emission Properties", "Quantum Memory Properties"])
                        ## col21
                        #tab1.subheader('Excitation Properties')
                        Photophysical_properties = load_table('Excitation properties')
                        Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
                        Photophysical_properties["Characteristic time (ns)"]=Photophysical_properties["Characteristic time (ns)"].astype(int)
                        Photophysical_properties["Characteristic time (ns)"] = Photophysical_properties["Characteristic time (ns)"].map("{:.2E}".format)

                        try: 
                            ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge]) & (Photophysical_properties['Host'] =='monolayer')]
                        except  NameError :
                            ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='monolayer')]
                        except  KeyError:
                            ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='monolayer')]
                        ep2=ppdefects.iloc[:,3:]
                        ep2.rename(columns={"dipole_x":"µₓ (Debye)","dipole_y":"μᵧ (Debye)","dipole_z":"µz (Debye)","Intensity":"Intensity (Debye)","Angle of excitation dipole wrt the crystal axis":"Angle of excitation dipole wrt the crystal axis (degree)"},inplace=True)
                        #ep2=ep2.T
                        ep2=ep2.T.astype(str)  ## Fixed 31.07.2025
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

                        Photophysical_properties = load_table('Emission properties')
                        Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
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
                        #emp=emp.T
                        emp=emp.T.astype(str) ## Fixed 31.07.2025
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
                        Photophysical_properties = load_table('Quantum memory properties')
                        Photophysical_properties.iloc[:,6:]=Photophysical_properties.iloc[:,6:].round(2)
                        Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"]=Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].astype(int)
                        Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"] = Photophysical_properties["Qualify factor at n =1.76 & Kappa = 0.05"].map("{:.2E}".format)
                        Photophysical_properties["g (MHz)"]=Photophysical_properties["g (MHz)"].astype(int)
                        Photophysical_properties["g (MHz)"] = Photophysical_properties["g (MHz)"].map("{:.2E}".format)
                    
                        try: 
                            ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Charge state'] ==chargetrans[str_charge])& (Photophysical_properties['Host'] =='monolayer')]
                        except  NameError :
                            ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='monolayer')]
                        except  KeyError:
                            ppdefects = Photophysical_properties[(Photophysical_properties['Defect'] == str_defect) & (Photophysical_properties['Host'] =='monolayer')]
                        qmp = ppdefects.iloc[:,3:]
                        #qmp=qmp.T
                        qmp=qmp.T.astype(str) # Fixed 31.07.2025
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
    [Chanaprom Cholsuk, Sujin Suwanna, Tobias Vogl, *"Advancing the hBN Defects Database through Photophysical Characterization of Bulk hBN."* 2025, arXiv:2507.18093.](https://doi.org/10.48550/arXiv.2507.18093) \n
    [Chanaprom Cholsuk, Ashkan Zand, Asli Cakan, Tobias Vogl, *"The hBN defects database: a theoretical compilation of color centers in hexagonal boron nitride."* The Journal of Physical Chemistry C, 2024, 128 (30), 12716.](https://doi.org/10.1021/acs.jpcc.4c03404) \n
    For specific properties of particular defects, please also cite the data originally published as follows:
    ''')
    st.markdown('''
    Raman spectrum
    * [Cholsuk, Chanaprom, Asli Çakan, Volker Deckert, Sujin Suwanna, and Tobias Vogl. *"Raman signatures of single point defects \
    in hexagonal boron nitride quantum emitters."* 2025, arXiv: 2502.21118. \
    ](https://doi.org/10.48550/arXiv.2502.21118)
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
