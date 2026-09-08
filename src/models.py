"""Optimalizační modely nad maticí vzdáleností: TSP, SPP, CPP."""

import networkx as nx
import numpy as np
import pulp


def solve_tsp(distance_matrix: np.ndarray) -> tuple[list[int], float]:
    """Řeší problém obchodního cestujícího (TSP) jako celočíselný LP model
    (Miller-Tucker-Zemlin formulace). Vhodné pro menší instance (do cca 15-20 bodů).
    """
    n = distance_matrix.shape[0]
    prob = pulp.LpProblem("TSP", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", ((i, j) for i in range(n) for j in range(n) if i != j),
                               cat="Binary")
    u = pulp.LpVariable.dicts("u", range(n), lowBound=0, upBound=n - 1, cat="Continuous")

    prob += pulp.lpSum(distance_matrix[i][j] * x[i, j] for i in range(n) for j in range(n) if i != j)

    for i in range(n):
        prob += pulp.lpSum(x[i, j] for j in range(n) if j != i) == 1
        prob += pulp.lpSum(x[j, i] for j in range(n) if j != i) == 1

    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + n * x[i, j] <= n - 1

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    route = [0]
    current = 0
    visited = {0}
    while len(visited) < n:
        for j in range(n):
            if j != current and pulp.value(x[current, j]) == 1:
                route.append(j)
                visited.add(j)
                current = j
                break
    route.append(0)

    total_distance = pulp.value(prob.objective)
    return route, total_distance


def solve_spp(distance_matrix: np.ndarray, source: int, target: int) -> tuple[list[int], float]:
    """Řeší problém nejkratší cesty (Shortest Path Problem) pomocí Dijkstrova algoritmu."""
    n = distance_matrix.shape[0]
    graph = nx.DiGraph()
    for i in range(n):
        for j in range(n):
            if i != j and np.isfinite(distance_matrix[i][j]):
                graph.add_edge(i, j, weight=distance_matrix[i][j])

    path = nx.shortest_path(graph, source=source, target=target, weight="weight")
    length = nx.shortest_path_length(graph, source=source, target=target, weight="weight")
    return path, length


def solve_cpp(graph: nx.MultiGraph, weight: str = "length") -> tuple[list[int], float]:
    """Řeší problém čínského listonoše (Chinese Postman Problem / Route Inspection).

    Vyžaduje neorientovaný graf silniční sítě (ne matici vzdáleností), protože úloha
    spočívá v obejití všech hran, nikoli všech vrcholů.
    """
    odd_nodes = [v for v, d in graph.degree() if d % 2 == 1]

    if not odd_nodes:
        eulerian_graph = graph
    else:
        pairs_graph = nx.Graph()
        for u in odd_nodes:
            for v in odd_nodes:
                if u != v:
                    length = nx.shortest_path_length(graph, u, v, weight=weight)
                    pairs_graph.add_edge(u, v, weight=length)

        matching = nx.algorithms.matching.min_weight_matching(pairs_graph)

        eulerian_graph = nx.MultiGraph(graph)
        for u, v in matching:
            path = nx.shortest_path(graph, u, v, weight=weight)
            for a, b in zip(path[:-1], path[1:]):
                edge_data = graph.get_edge_data(a, b)
                w = list(edge_data.values())[0].get(weight, 1) if edge_data else 1
                eulerian_graph.add_edge(a, b, **{weight: w})

    circuit = list(nx.eulerian_circuit(eulerian_graph))
    total_weight = sum(
        list(graph.get_edge_data(u, v).values())[0].get(weight, 1)
        for u, v in circuit
    )
    route = [circuit[0][0]] + [v for _, v in circuit]
    return route, total_weight
