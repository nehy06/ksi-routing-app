# Routing Streamlit – architektura a postup vývoje

Tento dokument popisuje zamýšlenou architekturu projektu a doporučený postup
implementace. Aplikaci píše uživatelka sama, Claude slouží jako průvodce
a konzultant, ne jako primární autor kódu.

## Aktuální stav (naposledy aktualizováno 2026-09-09)

**Hotovo a otestováno:**
- `src/distance_matrix.py`:
  - `download_road_network(place, network_type)` – stažení sítě podle názvu místa
  - `download_road_network_bbox(...)` – stažení sítě podle bbox souřadnic
  - `get_or_download_graph(place, network_type, cache_dir)` – obalí
    `download_road_network` vlastní lokální cache (`data/cache/graphs/*.graphml`,
    přes `ox.save_graphml`/`ox.load_graphml`), odlišnou od interní hashované
    cache `osmnx` v `data/cache/`
  - `prepare_graph_for_weight(graph, mode)` – `mode="time"` doplní
    `add_edge_speeds`/`add_edge_travel_times` a vrátí `weight="travel_time"`,
    jinak `weight="length"`
  - `nearest_nodes(graph, lats, lons)` – vyžaduje `scikit-learn`
    (doinstalováno, viz `requirements.txt`)
  - `build_distance_matrix(graph, node_ids, weight)` – Dijkstra matice,
    `np.inf` pro nedosažitelné body
- `tests/test_distance_matrix.py` – ruční ověřovací skript, ověřil celou
  pipeline (stažení → cache → nearest_nodes → matice metry i čas) na
  reálných datech (`place='Praha 6'`)
- Přechod na `pytest` odsouhlasen jako směr pro formální testy (`assert`
  místo `print()`), zatím ale ještě nejsou napsané – ve `requirements.txt`
  je `pytest` doinstalovaný, princip (fixture pro graf, testy jako funkce
  `test_*`) byl probraný, ale uživatelka to zatím nechtěla rozepisovat.

**Rozpracováno / další krok (k rozhodnutí):**
- `src/models.py` – kostra existuje (TSP/SPP/CPP), ale zatím netestovaná
  na reálných datech z `distance_matrix.py`
- `pages/1_Matice_vzdalenosti.py` – stále jen prázdný stub, UI zatím vůbec
  nepropojené s `src/`
- Doporučený další krok byl SPP (`src/models.py`) přímo nad již ověřenou
  maticí, než se sahá na UI – uživatelka se ještě nerozhodla mezi touto
  variantou (B) a propojením UI (A).

**Poznámka k závislostem:** za běhu vyšlo najevo, že `requirements.txt`
z počátku scaffoldu chybělo `scikit-learn` (vyžaduje `nearest_nodes` na
nezprojektovaném grafu). Doplněno, spolu s `rich` (barevný/tabulkový výstup
v testech) a `pytest`.

## Branch strategie a deploy (od 2026-09-11)

- `main` – deploy/produkční branch. Nasazuje se z ní na Streamlit Cloud.
  Obsahuje jen funkční, odzkoušené části. Stránky nedokončených solverů
  (`pages/2_TSP.py`, `pages/3_SPP.py`, `pages/4_CPP.py`) v ní záměrně
  nejsou, dokud nejsou hotové – `pages/1_Matice_vzdalenosti.py` v `main`
  zůstává.
- `dev` – pracovní branch, kde vzniká veškerý rozpracovaný kód (včetně
  solver stránek). Běžná práce probíhá zde.
- Postup, jak dostat hotovou věc z `dev` do `main`: **necouvat celý branch
  merge** (`git merge dev` by vrátil zpět i nedokončené solver stránky,
  protože v `dev` stále existují). Místo toho přenášet jednotlivé hotové
  soubory:
  ```
  git checkout main
  git checkout dev -- pages/2_TSP.py
  git commit -m "..."
  git push
  ```

## Cíl aplikace

Streamlit aplikace, která:

1. umožní zadat body zájmu (adresy nebo souřadnice),
2. stáhne odpovídající silniční síť z OpenStreetMap,
3. vypočte matici vzdáleností (nebo časů) mezi body,
4. nad touto maticí vyřeší vybraný model operačního výzkumu:
   - **TSP** (problém obchodního cestujícího) – okružní trasa přes všechny body,
   - **SPP** (problém nejkratší cesty) – trasa mezi dvěma body,
   - **CPP** (problém čínského listonoše) – trasa pokrývající všechny hrany sítě,
5. výsledek zobrazí na mapě a jako tabulku/report.

## Vrstvy architektury

Doporučené oddělení odpovědností do tří vrstev, ať zůstává kód přehledný
a testovatelný nezávisle na Streamlit UI:

```
UI vrstva        app.py, pages/*.py       – jen vstupy, volání funkcí, zobrazení výstupu
Datová vrstva     src/distance_matrix.py   – OSM data, geokódování, matice vzdáleností
Modelová vrstva   src/models.py            – TSP/SPP/CPP jako čisté funkce nad maticí/grafem
Testovací vrstva  tests/test_*.py          – ruční i automatické ověření funkcí z src/
```

Pravidlo: stránky v `pages/` by neměly obsahovat žádnou výpočetní logiku,
jen volat funkce z `src/` a stavět UI. Usnadní to ladění i případné testy.

Testy patří do `tests/`, ne do kořenové složky vedle `app.py` – udržuje to
kořen projektu přehledný a odpovídá běžné konvenci v Pythonu. Soubory
pojmenované `test_*.py` jde spustit i přes `pytest`, i když zatím jde jen
o ruční ověřovací skripty s `print()`, ne o formální testy s `assert`.

## Klíčové knihovny a jejich role

| Knihovna | K čemu slouží zde |
|---|---|
| `osmnx` | stažení silniční sítě z OpenStreetMap jako graf (`networkx`) |
| `networkx` | práce s grafem, nejkratší cesty (Dijkstra), Eulerovský okruh pro CPP |
| `geopy` | geokódování adres na souřadnice (lat/lon), pokud se nezadávají body přímo na mapě |
| `folium` + `streamlit-folium` | interaktivní mapa – zadávání bodů kliknutím, zobrazení trasy |
| `pulp` | LP/ILP formulace pro TSP (a případně jiné modely řešitelné jako LP) |
| `pandas` / `numpy` | práce s maticí vzdáleností jako s tabulkou/polem |

## Doporučené pořadí implementace

Postupovat po malých, samostatně ověřitelných krocích – po každém kroku
by mělo jít aplikaci spustit a vidět výsledek.

1. **Zadání bodů**
   - Nejjednodušší varianta: textový vstup souřadnic nebo adres do tabulky.
   - Pokročilejší varianta: interaktivní mapa (`streamlit-folium`), kam se body
     zadávají kliknutím – řešit až ve druhém kole.

2. **Stažení silniční sítě z OSM**
   - `osmnx.graph_from_place()` nebo `graph_from_bbox()`.
   - Doporučeno cachovat stažený graf lokálně (`data/cache/`), stahování je pomalé
     a opakované volání OSM zbytečně zatěžuje jejich servery.

3. **Výpočet matice vzdáleností**
   - Najít nejbližší uzly grafu pro zadané body (`ox.distance.nearest_nodes`).
   - Spočítat nejkratší cesty mezi všemi dvojicemi bodů (Dijkstra z `networkx`).
   - Výstupem je čtvercová matice (`numpy.ndarray` nebo `pandas.DataFrame`
     s popisky bodů).

4. **Zobrazení matice a základní kontrola**
   - Vypsat matici jako tabulku ve Streamlitu – užitečné pro ověření správnosti
     ještě před přidáním optimalizačních modelů.
   - **Přepínač metry / čas**: UI má nabízet volbu jednotky matice.
     `build_distance_matrix` již přijímá `weight="length"` (metry) nebo
     `weight="travel_time"` (sekundy). Pro variantu s časem je ale nutné graf
     před výpočtem obohatit: `ox.add_edge_speeds(graph)` a
     `ox.add_edge_travel_times(graph)` – jinak hrany `travel_time` nemají.
     Tento krok volat jen když si uživatel zvolí čas (zbytečně nezatěžovat
     výpočet, když stačí metry).

5. **SPP (nejkratší cesta)**
   - Nejjednodušší model na start – přímé využití `networkx.shortest_path`.
   - Dobrý krok pro ověření, že matice/graf dávají smysl, než se přidá TSP.

6. **TSP**
   - Pro malé instence (do ~15–20 bodů) ILP formulace přes `pulp` (Miller–Tucker–Zemlin).
   - Pro větší instance zvážit heuristiku (např. nearest neighbor + 2-opt) –
     řešit až pokud LP formulace přestane stačit časově.

7. **CPP (čínský listonoš)**
   - Nejnáročnější na pochopení – pracuje se s grafem silniční sítě přímo
     (ne s maticí vzdáleností mezi body), protože cílem je projít všechny hrany.
   - Postup: najít vrcholy s lichým stupněm → najít minimální párování mezi nimi
     → zdvojit odpovídající hrany → najít Eulerovský okruh.

8. **Vizualizace výsledné trasy na mapě**
   - Po zvládnutí modelů: vykreslit vypočtenou trasu pomocí `folium`
     (jako polyline nad skutečnými silnicemi, ne jen rovné čáry mezi body).

## Poznámky k designu rozhraní

- Multipage Streamlit (`pages/`) odpovídá krokům 1–7 výše – každá stránka
  jeden krok procesu.
- Mezikroky (stažený graf, spočítaná matice, zadané body) předávat mezi
  stránkami přes `st.session_state`, aby uživatel nemusel opakovat kroky
  při přechodu mezi stránkami.

## Co zatím NENÍ potřeba řešit

- Autentizace/uživatelské účty.
- Podpora více současných uživatelů / škálování.
- Optimalizace výkonu pro velké instance (stovky bodů) – řešit až bude
  základní verze funkční.
