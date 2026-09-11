"""Stránka: zadání míst a výpočet matice vzdáleností z OpenStreetMap."""

# importy
import streamlit as st
import pandas as pd
from src.distance_matrix import (
    get_or_download_graph,
    prepare_graph_for_weight,
    nearest_nodes,
    build_distance_matrix,
    parse_cooridnates_text,
    check_place_exists,
)

from src.ui import render_header, render_footer, render_steps_sidebar

# === Hlavička stránky a spol ===
# ===============================
render_header()
render_steps_sidebar()

st.header('Matrix GENERATOR')

st.markdown(
    """
    Generování matic vzdáleností pro různé "Transportation problems"

    ---

    """
)

# ==== zadávání parametrů matice ===
# ==================================
st.subheader('Zadání parametrů matice')

with st.form("matrix_form", border=False):

    # oblast mapy, která se má stáhnout
    st.markdown(
        """
        Je potřeba zadat oblast mapy, která se má stáhnout pro vygenerování matice.

        _Např. pokud budete zadávat souřadnice z Prahy, zadejte "Praha", lze i konkrétní pražšké části, jako "Praha 6"._
        """
    )

    st.warning(
        """
        **POZOR:** čím větší oblast bude, tím déle se bude oblast stahovat. Silniční mapa České republiky zabere řádově a žněkolik desítek minut.
        """
    )
    place = st.text_input(
        label="Oblast mapy pro generování",
        value="Praha 6",
    )

    # zadávání souřadnic:
    st.info(
        """
        Aby generování matice fungovalo, je potřeba zadat souřadnice ve formátu: zeměpisná šířka, zeměpisná délka; vždy jeden bod na řádek.

        _Tip: U bodů v ČR je šířka vždy menší číslo (~50) než délka (~14)._
        """
    )
    coordinates_input = st.text_area(
        label='Souřadnice',
        value="50.1024, 14.3935\n50.0975, 14.3985\n50.0819, 14.3644\n50.0917, 14.3557\n50.1057, 14.3766",
    )

    # jednotky matice
    st.text("Zvolte jednotku ohodnocení hran:")
    units = st.segmented_control(
        'Jednotky: ',
        options=['Vzdálenost', 'Čas'],
        default="Vzdálenost",
    )

    st.text("Zvolte typ dopravní sítě:")
    network_type_label = st.selectbox(
        "Typ sítě",
        options=["Automobilová doprava", "Pěší", "Cyklo", "Vše"],
    )

    # dict pro namapování vybrané silniční sítě na osmnx terminologii
    network_type_map = {
        "Automobilová doprava": "drive",
        "Pěší": "walk",
        "Cyklo": "bike",
        "Vše": "all",
    }
    network_type = network_type_map[network_type_label]

    # protože ve funkci `prepare_graph_for_weight` se určuje ohodnocení hran pomocí "mode", zde je převod
    mode = "time" if units == "Čas" else "length"

    submitted = st.form_submit_button("Odeslat a generovat matici")

# výpočetní logika po odeslání formuláře
if submitted:
    # check existence místa
    if not check_place_exists(place):
        # kód v podmínce nastane pouze tehdy, pokud check_place_exists() vrátí False
        st.error(f"Místo '{place}' se nepodařilo najít. Zkontrolujte název.")
        st.stop()  # pokud zadaná oblast neexistuje, zastaví se další generování

    lats, lons = parse_cooridnates_text(coordinates_input)

    # matice dává smysl jen pro alespoň 2 body
    if len(lats) < 2:
        st.error("Zadejte alespoň 2 body, jinak nelze matici vzdáleností spočítat.")
        st.stop()

    # náhled zadaných bodů na mapě, ještě před (pomalejším) stažením sítě
    st.subheader("Náhled zadaných bodů")
    points_df = pd.DataFrame({"lat": lats, "lon": lons})
    st.map(points_df)

    with st.spinner("Stahuji silniční síť, může to chvíli trvat..."):
        road_network = get_or_download_graph(place, network_type)

    graph, weight = prepare_graph_for_weight(road_network, mode)
    nodes = nearest_nodes(graph, lats, lons)
    matrix = build_distance_matrix(graph, nodes, weight)

    labels = [f"{lat:.4f}, {lon:.4f}" for lat, lon in zip(lats, lons)]
    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels)

    st.subheader("Matice vzdáleností")
    st.dataframe(matrix_df)

    st.download_button(
        label="Stáhnout matici jako CSV",
        data=matrix_df.to_csv().encode("utf-8"),
        file_name="matice_vzdalenosti.csv",
        mime="text/csv",
    )

# ==== Patička ===
# ================
render_footer()
