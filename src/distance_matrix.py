"""Výpočet matice vzdáleností mezi body na základě OpenStreetMap (osmnx/networkx)."""

import os

import networkx as nx
import numpy as np
import osmnx as ox


# ----- Definice funkce pro stažení grafu pro zvolenou oblast -----
def download_road_network(place: str, network_type: str = "drive") -> nx.MultiDiGraph:
    """
    Stáhne silniční síť pro dané místo (např. 'Praha, Česko').
    """
    # vytvoří graf podle zadaného místa - `place`, atribut `network_type` udává, zda se má jednat o silnice, chodníky, cyklostezky atp
    graph = ox.graph_from_place(place, network_type=network_type)
    return graph


# ----- Definice funkce pro stažení grafu pro oblast vytyčenou pomocí "čtverce" určeného pomocí souřadnic.-----
def download_road_network_bbox(north: float, south: float, east: float, west: float, network_type: str = "drive") -> nx.MultiDiGraph:
    """
    Stáhne silniční síť pro zadaný ohraničující obdélník (bounding box - bbox).
    Může zahrnout výrazně menší nebo větší oblast, než je potřeba.
    """
    # vytvoří graf pomocí zadaných souřadnic, které tvoří ohraničující obdélník zadané oblasti.
    graph = ox.graph_from_bbox((north, south, east, west), network_type=network_type)
    return graph

# ----- Definice funkce pro uložení/načtení grafu z lokální cache -----
def _cache_path(cache_key: str, cache_dir: str = "data/cache/graphs") -> str:
    """Sestaví cestu k souboru v cache podle zadaného klíče (např. názvu místa)."""
    # nahradí znaky, které nejsou vhodné do názvu souboru (mezery, čárky, ...) podtržítkem
    safe_key = "".join(c if c.isalnum() else "_" for c in cache_key.lower())
    return os.path.join(cache_dir, f"{safe_key}.graphml")


def get_or_download_graph(place: str, network_type: str = "drive",
                           cache_dir: str = "data/cache/graphs") -> nx.MultiDiGraph:
    """Vrátí silniční síť pro dané místo — z lokální cache, pokud tam už je,
    jinak ji stáhne z OSM a uloží pro příští použití.

    Args:
        place: Název místa (např. 'Praha, Dejvice'), stejně jako u
            download_road_network.
        network_type: Typ sítě ('drive', 'walk', 'bike', ...).
        cache_dir: Složka, do které se ukládají grafy staené touto funkcí.
            Odlišná od interní cache osmnx (ta ukládá syrové odpovědi
            z Overpass API pod hashovanými názvy, tohle jsou čitelně
            pojmenované, kompletně zpracované grafy).

    Returns:
        Silniční síť jako networkx.MultiDiGraph.
    """
    # cache klíč zohledňuje i network_type, aby se 'drive' a 'walk' pro stejné
    # místo neuložily pod stejný soubor
    cache_key = f"{place}_{network_type}"
    path = _cache_path(cache_key, cache_dir)

    if os.path.exists(path):
        # graf už je uložený lokálně, stažení z OSM se přeskočí
        graph = ox.load_graphml(path)
        return graph

    # graf zatím v cache není, stáhne se z OSM
    graph = download_road_network(place, network_type=network_type)

    # ujistí se, že cílová složka existuje (i kdyby šlo o víceúrovňovou cestu)
    os.makedirs(cache_dir, exist_ok=True)
    ox.save_graphml(graph, path)

    return graph


def get_or_download_graph_bbox(north: float, south: float, east: float, west: float,
                                network_type: str = "drive",
                                cache_dir: str = "data/cache/graphs") -> nx.MultiDiGraph:
    """Vrátí silniční síť pro daný bbox — z lokální cache, pokud tam už je,
    jinak ji stáhne z OSM a uloží pro příští použití.

    Args:
        north, south, east, west: Souřadnice ohraničujícího obdélníku,
            stejně jako u download_road_network_bbox.
        network_type: Typ sítě ('drive', 'walk', 'bike', ...).
        cache_dir: Složka, do které se ukládají grafy stažené touto funkcí.

    Returns:
        Silniční síť jako networkx.MultiDiGraph.
    """
    # souřadnice se před sestavením klíče zaokrouhlí, aby mírně odlišné
    # zadání (setiny stupně) neplýtvalo cache novým souborem pro prakticky
    # stejnou oblast
    cache_key = f"{round(north, 4)}_{round(south, 4)}_{round(east, 4)}_{round(west, 4)}_{network_type}"
    path = _cache_path(cache_key, cache_dir)

    if os.path.exists(path):
        # graf už je uložený lokálně, stažení z OSM se přeskočí
        graph = ox.load_graphml(path)
        return graph

    # graf zatím v cache není, stáhne se z OSM
    graph = download_road_network_bbox(north, south, east, west, network_type=network_type)

    # ujistí se, že cílová složka existuje (i kdyby šlo o víceúrovňovou cestu)
    os.makedirs(cache_dir, exist_ok=True)
    ox.save_graphml(graph, path)

    return graph


# ----- Definice funkce pro nastavení typu ohodnocení hran -----
def prepare_graph_for_weight(graph, mode: str):
    """
    Mode určuje, zda vzdálenosti ve výslendé matici budou ve formátu času (time) nebo vzdáleností (length)
    Pokud jsou hodnoty vzdáleností v grafu čas cesty mezi jednotlivými uzly, jedná se o odhadovanou dobu, nikoli o přesný čas strávený na hraně grafu např. v případě dopravní zácpy atp.
    """
    # podmínka pro určení, zda se graf bude vracet jako časová vzdáleost nebo "metrová"
    if mode == "time":
        # ke každé hraně se přidá atribut speed_kph (km/h)
        # pokud data pro hranu obsahuji tag maxspeed, použije se tato hodnota
        # pokud tag maxspeed chybí, osmnx dopočítá rychlost jako průměr zjištěných rychlostí ostatních hran stejného typu silnice v rámci staženého grafu)

        graph = ox.add_edge_speeds(graph)
        # ke každé hraně přidá atribut travel_time v sekundách dopočítaný jako travel_time = length / speed_kph

        graph = ox.add_edge_travel_times(graph)

        #nastaví název atributu, který se bude používat při tvorbě matice vzdáleností, alg bude počítat s hodnotou travel time
        weight = "travel_time"

    else:
        weight = "length"    
    return graph, weight

# ----- Definice funkce pro tvorbu uzlů a hran ze zadaných souřadnic-----
def nearest_nodes(graph: nx.MultiDiGraph, lats: list[float], lons: list[float]) -> list[int]:
    """Najde nejbližší uzly grafu pro zadané body.

        Pro každou dvojici souřadnic (lat, lon) najde ID nejbližšího uzlu
        v silniční síti podle vzdušné vzdálenosti. Slouží k "přichycení"
        libovolných bodů zájmu na uzly grafu, se kterými dál pracuje
        build_distance_matrix.

        Args:
            graph: Silniční síť stažená pomocí download_road_network nebo
                download_road_network_bbox.
            lats: Zeměpisné šířky bodů zájmu.
            lons: Zeměpisné délky bodů zájmu. Musí mít stejnou délku jako lats
                a stejné pořadí (lats[i], lons[i] tvoří jeden bod).

        Returns:
            Seznam ID uzlů grafu, ve stejném pořadí jako vstupní body.
            node_ids[i] je nejbližší uzel k bodu (lats[i], lons[i]).

        Raises:
            ValueError: pokud lats a lons nemají stejnou délku.
        """
    # vrátí seznam ID nejbližších uzlů, ve stejném pořadí jako vstupní body
    return list(ox.distance.nearest_nodes(graph, X=lons, Y=lats)) 

def build_distance_matrix(graph: nx.MultiDiGraph, node_ids: list[int], weight: str = "length") -> np.ndarray:
    """Vytvoří čtvercovou matici vzdáleností mezi body pomocí nejkratších cest v grafu.

    Pro každou dvojici bodů spočítá nejkratší cestu v silniční síti pomocí
    Dijkstrova algoritmu (ne vzdušnou vzdálenost). Vstupem musí být ID uzlů
    grafu, ne libovolné souřadnice — viz nearest_nodes.

    Args:
        graph: Silniční síť stažená pomocí download_road_network nebo
            download_road_network_bbox. Pokud weight="travel_time", musí
            mít hrany předem doplněné atributy travel_time (viz
            prepare_graph_for_weight).
        node_ids: ID uzlů grafu, mezi kterými se má matice počítat.
            Typicky výstup z nearest_nodes. Pořadí určuje pořadí
            řádků/sloupců výsledné matice.
        weight: Název atributu hrany, podle kterého se počítá nejkratší
            cesta. "length" = metry, "travel_time" = sekundy (vyžaduje
            předchozí obohacení grafu). Výchozí hodnota je "length".

    Returns:
        Čtvercová matice tvaru (n, n), kde n = len(node_ids).
        matrix[i, j] je vzdálenost/čas nejkratší cesty z node_ids[i]
        do node_ids[j]. Prvky na diagonále jsou 0. Pokud mezi dvěma
        body neexistuje cesta (např. různé nepropojené komponenty
        grafu), hodnota je np.inf.
    """
    n = len(node_ids) # zjistí se počet bodů, pro které se matice počítá
    matrix = np.zeros((n, n)) # vytvoří prázdnou čtvercovou matici (vyplněná nulami) o rozměru n x n, do matice se postupně zapisují zjištěné vzdálenosti

    for i, source in enumerate(node_ids): # postupně projde každý bod v listu id uzlů
        lengths = nx.single_source_dijkstra_path_length(graph, source, weight=weight) # vytvoří vzdálenosti ze zdrojového uzlu `source` do všech ostatních ve zdrojovém grafu, ne jen pro mé body zájmu, a tyto vzdálenosti zapíše do `lengths`, vrací slovník klíš je ID uzlu, hodnoty jsou vzdálenosti k danému uzlu 
        for j, target in enumerate(node_ids): # všechy body zadané jako node_ids projde jako cílové a zvdálenosti source -> target zapíše do matice matrix
            if i == j: 
                continue # přeskakuje uzly na hlavní diagonále matice
            matrix[i, j] = lengths.get(target, np.inf) # vzdálenost z `lengths` zapíše do matice. pokud target v `lengths` není, tzn. cesta po silnici neexistuje, zapíše nekonečno `np.inf`

    return matrix 


# ----- Práce se vstupem uživatele - zadávání souřadnic jako textu -----
def parse_cooridnates_text(coordinates: str) -> tuple[list[float], list[float]]:
    """Rozdělí textový vstup se souřeadnicemi na 2 listy - latitudes, longitutes

    Args:
        coordinates (str): Vstupní text, řádky oddělené znakem \\n,
            každý řádek ve formátu "lat, lon".

    Returns:
         tuple[list[float], list[float]]: Dvojice listů (lats, lons).

    Raises:
        ValueError: Pokud některý řádek nejde rozdělit na dvě čísla.
    """
    coordinates_split = coordinates.split('\n')
    
    lats = []
    lons = []

    for coordinate in coordinates_split:
        try:
            lat, lon = coordinate.split(',')

            lats.append(float(lat))
            lons.append(float(lon))
        except ValueError:
            raise ValueError(f"Neplatný řádek se souřadnicemi: '{coordinate}'")
            
    return lats, lons


# kontrola existence oblasti před generováním matice

def check_place_exists(place: str) -> bool:
    """Ověří, že zadané místo lze v OpenStreetMap nalézt.

    Args:
        place: Název místa/oblasti, stejně jako u download_road_network.

    Returns:
        True, pokud OSM místo najde, jinak False.
    """
    try: 
        # jednoduchý skript na kontrolu existence místa / oblasti v mapách
        ox.geocode_to_gdf(place)
        return True
    except Exception:
        return False