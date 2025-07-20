import streamlit as st

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

st.title("Contact")

with st.container(border=False):
  st.markdown("""
  For requesting additional data and other feature functionalities, please contact h-bn@qcs.cit.tum.de 
  """)
