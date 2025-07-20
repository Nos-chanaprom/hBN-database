import streamlit as st
import requests # for API

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
      Specifies which database columns to return. The complete set of valid keys is listed in Table \\ref{tab:db-schema}.  
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
      If set to `True`, downloads the raw SQLite database file (named like `hbn_defects_<options>.db`) to the working directory.
    """)
