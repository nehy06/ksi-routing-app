"""ReadMe se základními informaci o applikaci + feedback"""

# ==== importy====
# ================
import streamlit as st
from src.ui import render_footer, render_header, render_steps_sidebar


# === Hlavička stránky a spol ===
# ===============================
render_header()
render_steps_sidebar()
st.divider()


# === Základní informace a texty o appce ===
# ==========================================
st.markdown(
    """
    Aplikace pro __plánování a optimalizaci tras nad reálnou dopravní sítí__.

    Vzniká na __Katedře systémového inženýrství PEF ČZU__ jako podpora výuky
    a výzkumu v oblasti operačního výzkumu.

    Aplikace využívá knihovnu __[Streamlit](https://streamlit.io/)__.

    ## K čemu appka slouží

    Uživatel zadá body zájmu (adresy nebo souřadnice), aplikace stáhne
    odpovídající silniční síť z __OpenStreetMap__ a spočítá mezi body __vzdálenosti__
    nebo __časy__ jízdy chůze. Na výběr je z různýc typů map:
    - silniční síť,
    - pěší,
    - cyklotrasy.
    
    Nad touto maticí lze řešit vybrané úlohy operačního
    výzkumu – najít nejkratší cestu mezi dvěma body, okružní trasu přes
    všechny body a tak dále.

    ## Aktuální stav

    Aplikace je *ve vývoji.*
    Hotové a funkční je zadání bodů a výpočet matice vzdáleností/časů. 

    ## Další rozvoj
    - implementace výpočtu vybraných problémú OR
    - zobrazení výsledků v mapách
    - možnost stažený výsledků ve vhodných formátech

    ## Plánované využití

    - podpora výuky operačního výzkumu a lineárního programování,
    - názorná demonstrace reálných úloh (rozvoz, okružní trasy) na skutečné
    silniční síti,
    - případně open-source nástroj pro širší použití na katedře.

    """
)


# === Button formuláře pro feedback ===
# =====================================
st.write(
    """
    ## Zpětná vazba a nápady na další funkce

    Níže naleznete odkaz na formulář, kde mi můžete zanechat jakoukoli zpětnou vazbu _(co vám funguje, nefunguje, nápady na vylepšení)_ nebo návrhy na nově funkce.
    """
)
st.link_button("Formulář pro zpětnou vazbu a hlášení chyb", url="https://forms.cloud.microsoft/e/KjGdWCZhE4")


# === Patička stránky a spol ===
# ===============================
render_footer()