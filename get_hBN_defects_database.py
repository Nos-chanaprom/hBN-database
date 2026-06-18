import os
import requests
import sqlite3
import tempfile
import pandas as pd

RAW_DB_URL = (
    "https://raw.githubusercontent.com/"
    "QCS-Theory/hBN-database/main/"
    "hbn_defects_database.db"
)

# Mapping of user options to DB columns (numeric filters)
_OPTION_COLUMNS = {
    "all": None,
    "zpl": "Emission properties: ZPL (eV)",
    "lifetime": "Emission properties: Lifetime (ns)",
    "misalignment": "Emission properties: Polarization misalignment (degree)",
    "abs_dipole_x": "Excitation properties: dipole_x",
    "abs_dipole_y": "Excitation properties: dipole_y",
    "abs_dipole_z": "Excitation properties: dipole_z",
    "abs_tdm": "Excitation properties: intensity",
    "ems_dipole_x": "Emission properties: dipole_x",
    "ems_dipole_y": "Emission properties: dipole_y",
    "ems_dipole_z": "Emission properties: dipole_z",
    "ems_tdm": "Emission properties: intensity",
    "abs_visibility": "Excitation properties: linear in-plane Polarization Visibility",
    "abs_angle": "Excitation properties: Angle of excitation dipole wrt the crystal axis",
    "abs_lifetime": "Excitation properties: Characteristic time (ns)",
    "ems_visibility": "Emission properties: linear in-plane Polarization Visibility",
    "ems_angle": "Emission properties: Angle of emission dipole wrt the crystal axis",
    "zpl_nm": "Emission properties: ZPL (nm)",
    "q": "Emission properties: Configuration coordinate (amu^(1/2) \\AA)",
    "hr": "Emission properties: HR Factor",
    "dw": "Emission properties: DW factor",
    "e_ground": "Emission properties: Ground-state total energy (eV)",
    "e_excited": "Emission properties: Excited-state total energy (eV)",
    "structure_ground": "structure_ground",
    "structure_excited": "structure_excited",
    "band_ground": "electronic_transition_ground",
    "band_excited": "electronic_transition_excited",
    "pl": "PL",
    "raman" : "raman"
}

# Base columns always included
_BASE_COLS = [
    "Host", "Defect", "Defect name", "Charge state",
    "Spin multiplicity", "Optical spin transition"
]

# Valid filter values as stored in DB
_VALID_SPINS = {"singlet", "doublet", "triplet"}
_VALID_HOSTS = {"monolayer", "bulk"}
_VALID_CHARGE_STATES = {-2, -1, 0, 1, 2}
_VALID_OPTICAL = {"up", "down"}


def _download_full(out_path: str) -> None:
    """
    Download the full hbn_defects_structure.db into out_path.
    """
    resp = requests.get(RAW_DB_URL, stream=True)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def get_database(
    option,
    spin_multiplicity: list = None,
    host: list = None,
    charge_state: list = None,
    optical_spin_transition: list = None,
    value_range: tuple = None,
    download_db: bool = False
):
    """
    Download, filter, and return the hBN defects data.

    Parameters:
      option: str or list of str. E.g. 'zpl', ['zpl','lifetime']
      spin_multiplicity: list of 'singlet','doublet','triplet'
      host: list of 'monolayer','bulk'
      charge_state: list of integers -2, -1, 0, 1, 2
      optical_spin_transition: list of 'up','down'
      value_range: tuple(min, max) only if a single numeric option is selected
      download_db: bool; if True, save filtered data to a .db file in cwd

    Returns:
      DataFrame, or (DataFrame, file_path) if download_db is True.
    """
    # Normalize options to list
    if isinstance(option, str):
        opts = [option]
    elif isinstance(option, (list, tuple)):
        opts = list(option)
    else:
        raise ValueError("option must be a string or list of strings.")

    # Clean and validate each option
    norm_opts = [opt.strip().lower() for opt in opts]
    for opt in norm_opts:
        if opt not in _OPTION_COLUMNS:
            raise ValueError(f"Invalid option '{opt}'. Valid options: {list(_OPTION_COLUMNS.keys())}")

    # If 'all' present, select all columns and ignore others
    if 'all' in norm_opts:
        select_cols = None
        numeric_opts = []
    else:
        # Determine numeric columns for each option
        numeric_opts = [ _OPTION_COLUMNS[opt] for opt in norm_opts ]
        select_cols = _BASE_COLS + numeric_opts

        # Add fallback columns for the four special columns if they are requested
        fallback_map = {
            "structure_ground": "structure_ground_triplet",
            "structure_excited": "structure_excited_triplet",
            "electronic_transition_ground": "electronic_transition_ground_triplet",
            "electronic_transition_excited": "electronic_transition_excited_triplet",
        }

        for orig_col, fallback_col in fallback_map.items():
            if orig_col in select_cols and fallback_col not in select_cols:
                select_cols.append(fallback_col)

    # Download DB to temp file
    fd, tmp = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        _download_full(tmp)
        conn = sqlite3.connect(tmp)
        # Build query
        if select_cols is None:
            df = pd.read_sql_query("SELECT * FROM updated_data", conn)
        else:
            cols_sql = ", ".join(f'"{c}"' for c in select_cols)
            df = pd.read_sql_query(f"SELECT {cols_sql} FROM updated_data", conn)

        def replace_nulls_with_fallback(df, orig_col, fallback_col):
            if orig_col in df.columns and fallback_col in df.columns:
                df[orig_col] = df[orig_col].fillna(df[fallback_col])

        fallback_map = {
            "structure_ground": "structure_ground_triplet",
            "structure_excited": "structure_excited_triplet",
            "electronic_transition_ground": "electronic_transition_ground_triplet",
            "electronic_transition_excited": "electronic_transition_excited_triplet",
        }

        for orig_col, fallback_col in fallback_map.items():
            replace_nulls_with_fallback(df, orig_col, fallback_col)
        # Replace the _triplet columns to the None columns
        df.drop(columns=fallback_map.values(), inplace=True, errors='ignore')

    finally:
        conn.close()
        os.remove(tmp)

    # Apply spin filter
    if spin_multiplicity:
        spins = [s.strip().lower() for s in spin_multiplicity]
        invalid = set(spins) - _VALID_SPINS
        if invalid:
            raise ValueError(f"Invalid spin(s) {invalid}. Must be one of {_VALID_SPINS}.")
        df = df[df["Spin multiplicity"].str.lower().isin(spins)]

    # Apply host filter
    if host:
        hosts = [h.strip().lower() for h in host]
        invalid = set(hosts) - _VALID_HOSTS
        if invalid:
            raise ValueError(f"Invalid host(s) {invalid}. Must be one of {_VALID_HOSTS}.")
        df = df[df["Host"].str.lower().isin(hosts)]

    # Apply charge state filter
    if charge_state:
        try:
            states = [int(c) for c in charge_state]
        except Exception:
            raise ValueError("charge_state must be a list of integers.")
        invalid = set(states) - _VALID_CHARGE_STATES
        if invalid:
            raise ValueError(f"Invalid charge_state(s) {invalid}. Must be one of {_VALID_CHARGE_STATES}.")
        df = df[df["Charge state"].isin(states)]

    # Apply optical spin transition filter
    if optical_spin_transition:
        opts_o = [o.strip().lower() for o in optical_spin_transition]
        invalid = set(opts_o) - _VALID_OPTICAL
        if invalid:
            raise ValueError(f"Invalid optical_spin_transition(s) {invalid}. Must be one of {_VALID_OPTICAL}.")
        full_vals = [f"{o}-{o}" for o in opts_o]
        df = df[df["Optical spin transition"].str.lower().isin(full_vals)]

    # Apply numeric range filter
    if value_range is not None:
        if len(numeric_opts) != 1:
            raise ValueError("value_range only applies when a single numeric option is selected.")
        if not (isinstance(value_range, (list, tuple)) and len(value_range) == 2):
            raise ValueError("value_range must be (min, max).")
        vmin, vmax = value_range
        col = numeric_opts[0]
        df = df[(df[col] >= vmin) & (df[col] <= vmax)]

    # Save to DB if requested
    if download_db:
        name_key = '_'.join(norm_opts)
        out_name = f"hbn_defects_{name_key}.db"
        conn2 = sqlite3.connect(out_name)
        df.to_sql("updated_data", conn2, index=False, if_exists="replace")
        conn2.close()
        return df, os.path.abspath(out_name)

    return df
