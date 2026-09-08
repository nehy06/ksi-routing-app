"""Streamlit aplikace: tvorba matic vzdáleností z OpenStreetMap
pro výpočet modelů TSP, SPP, CPP a dalších úloh operačního výzkumu.
"""

import streamlit as st

st.set_page_config(page_title="Routing – matice vzdáleností", layout="wide")

st.title("Routing Streamlit")
st.markdown(
    """
    Aplikace pro tvorbu matic vzdáleností z dat OpenStreetMap
    a jejich využití ve vybraných úlohách operačního výzkumu:

    - **TSP** – problém obchodního cestujícího
    - **SPP** – problém nejkratší cesty
    - **CPP** – problém čínského listonoše

    Jednotlivé kroky (zadání míst, stažení sítě, výpočet matice, řešení modelu)
    najdete v levém menu (stránky aplikace).
    """
)
