import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------------------
# Configuration and Setup
# ----------------------------

# Define the path to the OUTCAR.txt file for the triplet ground state
triplet_outcar_path = "OUTCAR_transition"  # Update this path as needed

# Define the defect identifier (used for plotting labels)
str_defect = "defect"  # Replace with your defect name

# Number of spin states to plot
spin_nummer = 4

# ----------------------------
# Initialize Variables
# ----------------------------

# Lists to store band energies and Fermi energy
band_energy_spinUp_filled = []
band_energy_spinUp_unfilled = []
band_energy_spinDown_filled = []
band_energy_spinDown_unfilled = []
fermi_energy = []

# ----------------------------
# Read and Parse Triplet Ground State Data
# ----------------------------

# Read the OUTCAR.txt file using pandas
try:
    df = pd.read_fwf(triplet_outcar_path, sep="\s+", header=None, skip_blank_lines=True)
except FileNotFoundError:
    raise FileNotFoundError(f"The file {triplet_outcar_path} was not found.")

# Process each row to extract energies
for row in range(len(df)):
    if row == 0 or row == 888:    #NBANDS + 4
        # Extract Fermi energy
        df2 = df.iloc[row, 0].split()
        if len(df2) >= 3:
            fermi_energy.append(df2[2])
    elif 4 <= row < 888: #NBANDS + 4
        # Spin-up bands
        df2 = df.iloc[row, 0].split()
        df_row = [ele for ele in df2 if ele.strip()]
        if len(df_row) >= 3:
            occupancy = round(float(df_row[2]))
            energy = float(df_row[1])
            if occupancy == 1:
                band_energy_spinUp_filled.append(energy)
            elif occupancy == 0:
                band_energy_spinUp_unfilled.append(energy)
    elif row > 891: #NBANDS + 9
        # Spin-down bands
        df2 = df.iloc[row, 0].split()
        #print(df2)
        df_row = [ele for ele in df2 if ele.strip()]
        if len(df_row) >= 3:
            occupancy = round(float(df_row[2]))
            energy = float(df_row[1])
            if occupancy == 1:
                band_energy_spinDown_filled.append(energy)
            elif occupancy == 0:
                band_energy_spinDown_unfilled.append(energy)

# ----------------------------
# Convert Fermi Energy to Float
# ----------------------------

fermi_energy = [float(i) for i in fermi_energy if i != '0']  # Exclude default '0' if not set
if not fermi_energy:
    raise ValueError("Fermi energy not found in the specified rows of OUTCAR.txt.")

# ----------------------------
# Calculate Reference Energies
# ----------------------------

try:
    # Convert lists to numpy arrays for efficient processing
    up_filled = np.array(band_energy_spinUp_filled)
    up_unfilled = np.array(band_energy_spinUp_unfilled)
    down_filled = np.array(band_energy_spinDown_filled)
    down_unfilled = np.array(band_energy_spinDown_unfilled)
    
    # Reference energy for filled spin-up bands (last energy below -5 eV)
    triplet_ref = up_filled[up_filled < 1.24][-1]
    
    # Reference energy for unfilled spin-up bands (first energy above 1 eV)
    triplet_unf_ref = up_unfilled[up_unfilled > 7.25][0]
    
except IndexError:
    # Default reference values if expected energies are not found
    triplet_ref = 1.24
    triplet_unf_ref = 7.25
    print("Warning: Reference energies not found. Using default values.")

# ----------------------------
# Adjust Energies Relative to References
# ----------------------------

# Adjust filled and unfilled energies
fup = [energy - triplet_ref for energy in up_filled[-spin_nummer:]]
ufup = [energy - triplet_ref for energy in up_unfilled[:spin_nummer]]
fdown = [energy - triplet_ref for energy in down_filled[-spin_nummer:]]
ufdown = [energy - triplet_ref for energy in down_unfilled[:spin_nummer]]

# ----------------------------
# Combine All Adjusted Energies
# ----------------------------

all_band_energy = np.concatenate([fup, ufup, fdown, ufdown])
# Determine plot y-axis limits
try:
    eemin = np.min(all_band_energy)
    eemax = np.max(all_band_energy)
except ValueError:
    # If all_band_energy is empty, set default limits
    eemin = 0
    eemax = 6
    print("Warning: No band energies found. Using default plot limits.")


# ----------------------------
# Define Spin Marker Function
# ----------------------------

def spin_marker(spinstate, band_energy, size, xcor, e_ref, bandlimit, emin, emax):
    """
    Adds arrow-like markers to the Plotly figure to represent energy bands.
    
    Parameters:
    - spinstate (str): Type of spin state ('fup', 'fdown', 'ufup', 'ufdown').
    - band_energy (list): List of energy values.
    - size (float): Size parameter for the arrows.
    - xcor (float): x-coordinate for placing the arrow.
    - e_ref (float): Reference energy for normalization.
    - bandlimit (float): Energy limit for the bands.
    - emin (float): Minimum energy for the plot.
    - emax (float): Maximum energy for the plot.
    """
    scale = 32
    delta = -0.04
    for band in band_energy:
        # Define arrow coordinates
        x_arrow = [
            xcor + delta , xcor + size / scale + delta, xcor + size / (scale * 2) + delta,
            xcor + size / (scale * 2) + delta, xcor + 3 * size / scale, xcor + 3 * size / scale,
            xcor + size / (scale * 2) + delta, xcor + size / (scale * 2) + delta,
            xcor - size / (scale * 2) + delta, xcor - size / (scale * 2) + delta,
            xcor - 3 * size / scale, xcor - 3 * size / scale,
            xcor - size / (scale * 2) + delta, xcor - size / (scale * 2) + delta,
            xcor - size / scale + delta, xcor + delta
        ]
        
        if spinstate == 'fup':
            y_arrow = [
                band + size / 2, band + size / 2 - size / 3, band + size / 2 - size / 3,
                band, band, band - size / 12, band - size / 12,
                band - size / 2, band - size / 2,
                band - size / 12, band - size / 12, band, band,
                band + size / 2 - size / 3, band + size / 2 - size / 3, band + size / 2
            ]
            fillcolor = 'black'
        elif spinstate == 'ufup':
            y_arrow = [
                band + size / 2, band + size / 2 - size / 3, band + size / 2 - size / 3,
                band, band, band - size / 12, band - size / 12,
                band - size / 2, band - size / 2,
                band - size / 12, band - size / 12, band, band,
                band + size / 2 - size / 3, band + size / 2 - size / 3, band + size / 2
            ]
            fillcolor = 'white'
        elif spinstate == 'fdown':
            y_arrow = [
                band - size / 2, band - size / 2 + size / 3, band - size / 2 + size / 3,
                band, band, band + size / 12, band + size / 12,
                band + size / 2, band + size / 2,
                band + size / 12, band + size / 12, band, band,
                band - size / 2 + size / 3, band - size / 2 + size / 3, band - size / 2
            ]
            fillcolor = 'black'
        elif spinstate == 'ufdown':
            y_arrow = [
                band - size / 2, band - size / 2 + size / 3, band - size / 2 + size / 3,
                band, band, band + size / 12, band + size / 12,
                band + size / 2, band + size / 2,
                band + size / 12, band + size / 12, band, band,
                band - size / 2 + size / 3, band - size / 2 + size / 3, band - size / 2
            ]
            fillcolor = 'white'
        else:
            continue  # Skip unknown spin states
        
        # Add the arrow as a filled scatter trace
        fig.add_trace(go.Scatter(
            x=x_arrow,
            y=y_arrow,
            fill="toself",
            mode='lines',
            opacity=1,
            fillcolor=fillcolor,
            line=dict(color='black'),
            showlegend=False
        ))
        
        # Add a rectangle to highlight the band region
        if spinstate in ['fup', 'fdown']:
            rect_color = 'rgba(116, 167, 200, 0.3)'  # Example color for filled bands
        else:
            rect_color = 'rgba(237, 140, 140, 0.3)'  # Example color for unfilled bands
        
        fig.add_shape(
            type="rect",
            x0=xcor - 0.05, y0=0 if spinstate in ['fup', 'fdown'] else bandlimit - e_ref,
            x1=xcor + 0.05, y1=-1 + emin if spinstate in ['fup', 'fdown'] else 1 + emax,
            fillcolor=rect_color,
            layer="below",
            line=dict(width=0)
        )
        
        delta += 0.02

# ----------------------------
# Initialize Plotly Figure
# ----------------------------

fig = go.Figure()

# ----------------------------
# Add Triplet Ground State Bands to Plot
# ----------------------------

# Adjusted xcor positions to minimize empty space
# Example: Using xcor=0.6 and xcor=0.7
spin_marker('fup', fup, size=0.5, xcor=0.6, e_ref=triplet_ref, bandlimit=triplet_unf_ref, emin=eemin, emax=eemax)
spin_marker('ufup', ufup, size=0.5, xcor=0.6, e_ref=triplet_ref, bandlimit=triplet_unf_ref, emin=eemin, emax=eemax)

spin_marker('fdown', fdown, size=0.5, xcor=0.7, e_ref=triplet_ref, bandlimit=triplet_unf_ref, emin=eemin, emax=eemax)
spin_marker('ufdown', ufdown, size=0.5, xcor=0.7, e_ref=triplet_ref, bandlimit=triplet_unf_ref, emin=eemin, emax=eemax)

# ----------------------------
# Configure Plot Axes and Layout
# ----------------------------

# Update X-axis to tightly fit around the active plotting region
fig.update_xaxes(
    title_font={"size": 30},
    showgrid=False,
    range=[0.5, 0.8],  # Adjusted range to cover xcor=0.6 and xcor=0.7 with buffer
    showticklabels=False,
    zeroline=False,
    showline=True,
    linewidth=2,
    linecolor='black',
    mirror=True,
)

# Update Y-axis
fig.update_yaxes(
    title_font={"size": 20},
    showgrid=False,
    zeroline=False,
    showline=True,
    linewidth=2,
    linecolor='black',
    mirror=True,
)

# Use str_defect directly for labeling
latexdefect = str_defect

# Update layout with titles, fonts, and size
fig.update_layout(
    showlegend=False, 
    xaxis_title=f"${latexdefect}$",
    yaxis_title=r"$E (eV)$",
    font=dict(size=18, color="Black"),
    plot_bgcolor='white',
    width=400,    # Set the width of the plot in pixels
    height=500    # Set the height of the plot in pixels
)

# Add annotations for "Triplet" centered between the two xcor positions
#fig.add_trace(go.Scatter(
#    x=[0.7, 0.7],
#    y=[eemax - 1, eemax - 1],
#    text=["Triplet"],
#    mode="text",
#    textposition="top center",
#    showlegend=False
#))

# Finalize and show the plot
# Save the figure as a PNG image
fig.write_image("band_structure.png",scale=4.17)  #scale = 4.17 is dpi = 300
#fig.show()
