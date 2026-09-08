"""Výpočet matice vzdáleností mezi body na základě OpenStreetMap (osmnx/networkx)."""

import networkx as nx
import numpy as np
import osmnx as ox


def download_road_network(place: str, network_type: str = "drive") -> nx.MultiDiGraph:
    """Stáhne silniční síť pro dané místo (např. 'Praha, Česko')."""
    graph = ox.graph_from_place(place, network_type=network_type)
    return graph


def download_road_network_bbox(north: float, south: float, east: float, west: float,
                                network_type: str = "drive") -> nx.MultiDiGraph:
    """Stáhne silniční síť pro zadaný ohraničující obdélník (bounding box)."""
    graph = ox.graph_from_bbox((north, south, east, west), network_type=network_type)
    return graph


def nearest_nodes(graph: nx.MultiDiGraph, lats: list[float], lons: list[float]) -> list[int]:
    """Najde nejbližší uzly grafu pro zadané body (lat, lon)."""
    return list(ox.distance.nearest_nodes(graph, X=lons, Y=lats))


def build_distance_matrix(graph: nx.MultiDiGraph, node_ids: list[int],
                           weight: str = "length") -> np.ndarray:
    """Vytvoří čtvercovou matici vzdáleností mezi body pomocí nejkratších cest v grafu.

    weight: 'length' pro metry, 'travel_time' pokud jsou hrany obohaceny o čas.
    """
    n = len(node_ids)
    matrix = np.zeros((n, n))

    for i, source in enumerate(node_ids):
        lengths = nx.single_source_dijkstra_path_length(graph, source, weight=weight)
        for j, target in enumerate(node_ids):
            if i == j:
                continue
            matrix[i, j] = lengths.get(target, np.inf)

    return matrix
