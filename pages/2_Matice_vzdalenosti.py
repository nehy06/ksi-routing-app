"""Stránka: zadání míst a výpočet matice vzdáleností z OpenStreetMap."""

# importy
import streamlit as st
import pandas as pd
from src.distance_matrix import (
    get_or_download_graph,          # stažení/cache silniční sítě podle názvu místa
    get_or_download_graph_bbox,     # stažení/cache silniční sítě podle bbox souřadnic
    prepare_graph_for_weight,       # doplní graf o rychlosti/časy, pokud se počítá s jednotkou "čas"
    nearest_nodes,                  # najde nejbližší uzly grafu pro zadané souřadnice
    build_distance_matrix,          # spočítá matici nejkratších cest (Dijkstra) mezi uzly
    parse_cooridnates_text,         # rozparsuje textový vstup souřadnic na dva seznamy (lats, lons)
    check_place_exists,             # ověří, že název místa existuje v OSM
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

# Přepínač typu oblasti (název vs. bbox) je záměrně MIMO formulář.
# Widgety uvnitř st.form() nevyvolají okamžitý rerun aplikace při změně -
# UI by se přepnulo až po odeslání formuláře. Mimo formulář se přepne hned.
place_type = st.segmented_control(
    'Typ určení oblasti mapového podkladu:',
    options=['Název oblasti', 'Čtverec vytyčený souřadnicemi'],
    default="Název oblasti"
)

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

    # podle zvoleného place_type (viz výše, mimo formulář) se zobrazí buď
    # textové pole pro název místa, nebo 4 pole pro souřadnice bbox
    if place_type == 'Název oblasti':
        place = st.text_input(
            label="Oblast mapy pro generování",
            value="Praha 6",
        )
    else:
        st.write(
            """
            Zde bude popis toho, jak tohle funguje
            """
        )
        # value=None -> dokud uživatel nic nezadá, vrací se None (ne 0.0),
        # jde tak rozeznat "nevyplněno" od skutečně zadané nuly
        north = st.number_input("Zadejte severní roh:", value=None)
        south = st.number_input("Zadejte jižní roh:", value=None)
        east = st.number_input("Zadejte východní roh:", value=None)
        west = st.number_input("Zadejte západní roh:", value=None)

    # zadávání souřadnic:
    st.info(
        """
        Aby generování matice fungovalo, je potřeba zadat souřadnice ve formátu:

            `zeměpisná šířka, zeměpisná délka`

        Každý bod vždy jeden bod na řádek.

        _Tip: U bodů v ČR je šířka vždy ~50 a délka ~14._
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

    # tlačítko musí být uvnitř `with st.form(...)`, jinak Streamlit
    # nepozná, ke kterému formuláři patří
    submitted = st.form_submit_button("Odeslat a generovat matici")

# výpočetní logika po odeslání formuláře
if submitted:

    # větev pro zadání oblasti podle názvu místa
    if place_type == "Název oblasti":
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

        # stažení (nebo načtení z cache) silniční sítě podle názvu místa
        with st.spinner("Stahuji silniční síť, může to chvíli trvat..."):
            road_network = get_or_download_graph(place, network_type)

    # větev pro zadání oblasti pomocí bbox souřadnic (severní/jižní/východní/západní roh)
    else:

        # kontrola, že žádná ze 4 souřadnic není nevyplněná (None)
        # musí být PRVNÍ kontrola - další podmínky porovnávají čísla
        # (-90 <= None <= 90 by spadlo na TypeError, kdyby None prošlo dál)
        if north is None or south is None or east is None or west is None:
            st.error("Jedna ze souřadnic je prázdná - doplňte")
            st.stop()

        # kontrola platného rozsahu zeměpisné šířky (-90 až 90)
        if not (-90 <= north <= 90 and -90 <= south <= 90):
            st.error("Zeměpisná šířka musí být mezi -90 a 90.")
            st.stop()

        # kontrola platného rozsahu zeměpisné délky (-180 až 180)
        if not (-180 <= east <= 180 and -180 <= west <= 180):
            st.error("Zeměpisná délka musí být mezi -180 a 180.")
            st.stop()

        # kontrola, že obdélník dává logicky smysl (severní roh nad jižním atd.)
        if north <= south or east <= west:
            st.error("Neplatný obdélník – severní roh musí být nad jižním, východní vpravo od západního.")
            st.stop()

        lats, lons = parse_cooridnates_text(coordinates_input)

        # náhled zadaných bodů na mapě, ještě před (pomalejším) stažením sítě
        st.subheader("Náhled zadaných bodů")
        points_df = pd.DataFrame({"lat": lats, "lon": lons})
        st.map(points_df)

        # stažení (nebo načtení z cache) silniční sítě podle bbox souřadnic
        with st.spinner("Stahuji silniční síť, může to chvíli trvat..."):
            road_network = get_or_download_graph_bbox(north, south, east, west, network_type=network_type)

    # od tohoto místa je postup společný pro obě větve (název i bbox) -
    # road_network, lats a lons jsou v obou případech už nastavené

    # doplní graf o rychlosti/časy (pokud mode == "time") a vrátí název
    # atributu hrany, podle kterého se bude počítat matice ("length"/"travel_time")
    graph, weight = prepare_graph_for_weight(road_network, mode)

    # najde nejbližší uzly grafu pro zadané body zájmu
    nodes = nearest_nodes(graph, lats, lons)

    # spočítá čtvercovou matici nejkratších cest (Dijkstra) mezi uzly
    matrix = build_distance_matrix(graph, nodes, weight)

    # popisky řádků/sloupců výsledné matice - souřadnice zaokrouhlené na 4 desetinná místa
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
