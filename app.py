"""Streamlit aplikace: tvorba matic vzdáleností z OpenStreetMap
pro výpočet modelů TSP, SPP, CPP a dalších úloh operačního výzkumu.
"""

import streamlit as st
from src.ui import render_header, render_footer, render_steps_sidebar

st.set_page_config(page_title="Routing – matice vzdáleností", layout="centered")

render_header()
render_steps_sidebar()

st.markdown(
    """
    Aplikace pro tvorbu matic vzdáleností z dat OpenStreetMap
    a jejich využití ve vybraných úlohách operačního výzkumu:

    - **Matrix gen** - generátor matic vzdáleností
    - **TSP** – problém obchodního cestujícího
    - **SPP** – problém nejkratší cesty
    - **CPP** – problém čínského listonoše
    """
)

render_footer()
