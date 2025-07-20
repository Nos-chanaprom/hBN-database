import streamlit as st


st.set_page_config(page_title="Imprint",layout="wide")
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

st.title("Impressum")

st.subheader("Herausgeber")
with st.container(border=False):
  st.markdown('''
  Technical University of Munich  
  Arcisstraße 21  
  80333 Munich  
  Telefon: +4989289-01  
  poststelle@tum.de
  ''')

  st.subheader("Rechtsform und Vertretung")
  with st.container(border=False):
    st.markdown('''
      Die Technische Universität München ist eine Körperschaft des Öffentlichen Rechts und \
      staatliche Einrichtung (Art. 11 Abs. 1 BayHSchG). Sie wird gesetzlich vertreten durch \
      den Präsidenten Prof. Dr. Thomas F. Hofmann.
    ''')

  st.subheader("Zuständige Aufsichtsbehörde")
  with st.container(border=False):
    st.markdown('''
      Bayerisches Staatsministerium für Wissenschaft und Kunst
    ''')

  st.subheader("Umsatzsteueridentifikationsnummer")
  with st.container(border=False):
    st.markdown('''
      DE811193231 (gemäß § 27a Umsatzsteuergesetz )
    ''')

  st.subheader("Inhaltlich verantwortlich")
  with st.container(border=False):
    st.markdown('''
      Prof. Dr. Tobias Vogl  
      Karlstr. 45-47  
      80333 Munich  
      Email: tobias.vogl(at)tum.de  
      Namentlich gekennzeichnete Internetseiten geben die Auffassungen und Erkenntnisse der genannten Personen wieder.
    ''')

  st.subheader("Technische Umsetzung")
  with st.container(border=False):
    st.markdown('''
      Ansprechpartner für technischen Fragen erreichbar unter h-bn@qcs.cit.tum.de .      
    ''')

  st.subheader("Nutzungsbedingungen")
  with st.container(border=False):
    st.markdown('''
      Texte, Bilder, Grafiken sowie die Gestaltung dieses Webauftritts können dem Urheberrecht \
      unterliegen. Nicht urheberrechtlich geschützt sind nach § 5 des Urheberrechtsgesetz (UrhG)

      * Gesetze, Verordnungen, amtliche Erlasse und Bekanntmachungen sowie Entscheidungen und \
      amtlich verfasste Leitsätze zu Entscheidungen und

      * andere amtliche Werke, die im amtlichen Interesse zur allgemeinen Kenntnisnahme veröffentlicht \
      worden sind, mit der Einschränkung, dass die Bestimmungen über Änderungsverbot und Quellenangabe \
      in § 62 Abs. 1 bis 3 und § 63 Abs. 1 und 2 UrhG entsprechend anzuwenden sind.

      Als Privatperson dürfen Sie urheberrechtlich geschütztes Material zum privaten und sonstigen \
      eigenen Gebrauch im Rahmen des § 53 UrhG verwenden. Eine Vervielfältigung oder Verwendung \
      urheberrechtlich geschützten Materials dieser Seiten oder Teilen davon in anderen elektronischen \
      oder gedruckten Publikationen und deren Veröffentlichung ist nur mit unserer Einwilligung gestattet. \
      Diese Einwilligung erteilen auf Anfrage die für den Inhalt Verantwortlichen. Der Nachdruck und die \
      Auswertung von Pressemitteilungen und Reden sind mit Quellenangabe allgemein gestattet.

      Weiterhin können Texte, Bilder, Grafiken und sonstige Dateien ganz oder teilweise dem Urheberrecht \
      Dritter unterliegen. Auch über das Bestehen möglicher Rechte Dritter geben Ihnen die für den Inhalt \
      Verantwortlichen nähere Auskünfte.      
    ''')

  st.subheader("License")
  with st.container(border=False):
    st.markdown('''
      CC BY 4.0 Deed | Attribution 4.0 International | Creative Commons      
    ''')

  st.subheader("Haftungsausschluss")
  with st.container(border=False):
    st.markdown('''
      Alle in diesem Webauftritt bereitgestellten Informationen haben wir nach bestem Wissen und Gewissen \
      erarbeitet und geprüft. Eine Gewähr für die jederzeitige Aktualität, Richtigkeit, Vollständigkeit \
      und Verfügbarkeit der bereit gestellten Informationen können wir allerdings nicht übernehmen. Ein \
      Vertragsverhältnis mit den Nutzern des Webauftritts kommt nicht zustande.

      Wir haften nicht für Schäden, die durch die Nutzung dieses Webauftritts entstehen. Dieser \
      Haftungsausschluss gilt nicht, soweit die Vorschriften des § 839 BGB (Haftung bei Amtspflichtverletzung) \
      einschlägig sind. Für etwaige Schäden, die beim Aufrufen oder Herunterladen von Daten durch \
      Schadsoftware oder der Installation oder Nutzung von Software verursacht werden, übernehmen wir keine Haftung.    
    ''')
  st.subheader("Links")
  with st.container(border=False):
    st.markdown('''
      Von unseren eigenen Inhalten sind Querverweise („Links“) auf die Webseiten anderer Anbieter zu unterscheiden. \
      Durch diese Links ermöglichen wir lediglich den Zugang zur Nutzung fremder Inhalte nach § 8 Telemediengesetz. \
      Bei der erstmaligen Verknüpfung mit diesen Internetangeboten haben wir diese fremden Inhalte daraufhin \
      überprüft, ob durch sie eine mögliche zivilrechtliche oder strafrechtliche Verantwortlichkeit ausgelöst \
      wird. Wir können diese fremden Inhalte aber nicht ständig auf Veränderungen überprüfen und daher auch \
      keine Verantwortung dafür übernehmen. Für illegale, fehlerhafte oder unvollständige Inhalte und insbesondere \
      für Schäden, die aus der Nutzung oder Nichtnutzung von Informationen Dritter entstehen, haftet allein der \
      jeweilige Anbieter der Seite.
    ''')

st.write("--")
