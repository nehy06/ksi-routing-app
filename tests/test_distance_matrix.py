# spuštění testovacího skriptu
# python -m tests.test_distance_matrix

# ----- import funkcí z distance_matrix.py -----
# ------------------------------------------------------------
from src.distance_matrix import get_or_download_graph, nearest_nodes, build_distance_matrix, prepare_graph_for_weight

# importy rich pro formátování výpisů v conosli
from rich import print
from rich.table import Table
from rich.console import Console

# formátovací funkce pro výpis matice
def print_matrix_table(matrix, node_ids, title=""):
    table = Table(title=title)
    table.add_column("")  # roh tabulky, prázdný popisek
    for node_id in node_ids:
        table.add_column(str(node_id))

    for i, row_id in enumerate(node_ids):
        row_values = []
        for j in range(len(node_ids)):
            value = matrix[i, j]
            if value == float("inf"):
                row_values.append("[red]inf[/red]")
            else:
                row_values.append(f"{value:.1f}")
        table.add_row(str(row_id), *row_values)

    Console().print(table)

# ----- Proměnné pro testování funkčnosti -----
# ------------------------------------------------------------

place = 'Praha 6' # místo pro testování stažení road_network
network_type = 'drive' # chci silnice

lats = [
    50.1331786,
    50.1013983,
    50.1036575
] # zemepisná šířka bodů
lons = [
    14.3774844, 
    14.3949794,
    14.4085283
] # zeměpisná délka bodů


# ----- Základní testovací výpisy -----
# ------------------------------------------------------------

print('\n ===== [bold green]Základní charakteristiky grafu[/bold green] =====')
graph = get_or_download_graph(place=place, network_type=network_type)
print(graph)

# informace o uzlech
print('\n ===== [bold gray]Informace o náhodném uzlu grafu[/bold gray] =====')
node_id = list(graph.nodes)[0]
print(f'Souřadnice x/y uzlu [0]: \n node_id: {node_id}, atributy x,y: {graph.nodes[node_id]}')

# informace o  hranách
print('\n ===== [bold gray]Atributy hrany grafu[/bold gray] =====')
print(f'Atributy hrany [0]: {list(graph.edges(data=True))[0]}')

# Test správnost nastavení weight - čili jestli graf bude ve vzdálenostech nebo v čase
print('\n ===== [bold gray]Nastavení grafu pro vzdálenosti[/bold gray] =====')
graph_len, weight_len = prepare_graph_for_weight(graph=graph, mode='distance')
print(f'Graf bude mít hrany ohodnocené: {weight_len}, očekáváme "length" ')

print('\n ===== [bold gray]Nastavení grafu pro čas[/bold gray] =====')
graph_time, weight_time = prepare_graph_for_weight(graph=graph, mode='time')
print(f'Graf bude mít hrany ohodnocené: {weight_time}, očekáváme "travel_time" ')

# Informace o zjištěných skutečných uzlech
print('\n===== [bold gray]Seznam reálných uzlů nalezených v mapě[/bold gray] =====')
nodes = nearest_nodes(graph=graph, lats=lats, lons=lons)
print(f'Seznam uzlů: {nodes}')
if len(nodes) == len(lats):
    print(f"Počet skutečnýh uzlů se rovná počtu zadaných uzlů.")
else:
    print("[bold red]CHYBA![/bold red] Počet skutečných uzlů se nerovná počtu zadaných uzlů.")

# Informace o samotné matici vzdáleností, která se vygenerovala pro vzdálenosti
print('\n ===== Matice se vzdálenostmi =====')
matrix_len = build_distance_matrix(graph=graph_len, node_ids=nodes, weight=weight_len)
print_matrix_table(matrix_len, nodes, title="Matice vzdáleností (m)")

print('\n ===== Matice s časem =====')
# Informace o samotné matici vzdáleností, která se vygenerovala pr očas
matrix_time = build_distance_matrix(graph=graph_time, node_ids=nodes, weight=weight_time)
print_matrix_table(matrix_time, nodes, title="Matice časů (s)")

