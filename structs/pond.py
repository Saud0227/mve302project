import math as m
import random
from typing import Dict, Tuple

from structs.lilypad import Cluster


class Pond:

    cluster = None
    color_list = ["green", "blue", "purple", "orange", "yellow", "cyan", "magenta", "red"]

    @classmethod
    def quick_run(cls, side: float, lilypad_class, timeout = 1000000):
        pond = cls(side, lilypad_class)
        return pond.run(timeout)

    @classmethod
    def new_from_area(cls, area: int, lilypad_class, test_points_per_cell: int = 0):
        side_l = area**0.5
        cls(side_l, lilypad_class, test_points_per_cell)

    def purge_clusters(self):
        unique_clusters = set()
        for cluster in self.all_clusters:
            cluster_top = cluster.get_top()
            if cluster_top not in unique_clusters:
                unique_clusters.add(cluster_top)
        self.all_clusters = list(unique_clusters)

    def color_clusters(self):
        self.purge_clusters()
        for color_i, cluster in enumerate(self.all_clusters):
            cluster.set_color(self.color_list[color_i % len(self.color_list)])


    def __init__(self, side: float, lilypad_class, test_points_per_cell: int = 0):
        self.side_length = side
        self.grid: Dict[int, Dict[int, list]] = {}
        self.lilypad_class = lilypad_class
        self.last_lilypad = None
        self.all_clusters = []
        self.coords_list = []
        self.save_coords = False

    def add_lilypad(self):
        coords = self.get_coords()
        lilypad = self.lilypad_class(*coords)
        x, y = lilypad.get_coords()

        # check if the lilypad is touching any other lilypads in the same cell or adjacent cells
        clusters_touched = set()
        for other in self.get_cell_with_adjacent(x, y):
            target_cluster = other.cluster.get_top()
            if target_cluster in clusters_touched:
                # print("Dubble from same cluster")
                continue
            if lilypad.is_touching(other):
                # print("Touching")
                clusters_touched.add(target_cluster)
            else:
                # print("Not touching")
                pass
        if len(clusters_touched) == 0:
            # if the lilypad isn't touching any other lilypads, create a new cluster for it
            lilypad.cluster = self.cluster()
            self.all_clusters.append(lilypad.cluster)
            lilypad.cluster.add_lilypad(lilypad)
        elif len(clusters_touched) == 1:
            # if the lilypad is only touching one cluster, add it to that cluster
            cluster = clusters_touched.pop()
            cluster.add_lilypad(lilypad)
            lilypad.cluster = cluster
        else:
            # if the lilypad is touching multiple clusters, merge those clusters and add the lilypad to the merged cluster
            merged_cluster = self.cluster.merge_clusters(*clusters_touched)
            merged_cluster.add_lilypad(lilypad)
            lilypad.cluster = merged_cluster

        lilypad.smart_edge_check(self.side_length)

        self.add_to_cell(lilypad)
        self.last_lilypad = lilypad

        return coords

    def add_to_cell(self, lilypad: object):
        x, y = lilypad.get_coords()
        t_x, t_y = m.floor(x), m.floor(y)
        self._add_to_cell(lilypad, t_x, t_y)

    def _add_to_cell(self, lilypad: object, x, y):
        if x not in self.grid:
            self.grid[x] = {}
        if y not in self.grid[x]:
            self.grid[x][y] = []
        self.grid[x][y].append(lilypad)

    def _get_cell(self, x:int, y:int) -> list:
        return self.grid.get(x, {}).get(y, [])

    def _get_cell_w_adjacent(self, t_x:int, t_y:int) -> list:
        out = []
        for x in range(t_x-2, t_x+3):
            # NOTE: We don't care about out of bounds here because _get_cell will just return an empty list
            for y in range(t_y-2, t_y+3):
                out += self._get_cell(x, y)
        return out

    def get_cell_from_coords(self, x:float, y:float) -> list:
        if not 0<x<self.side_length or not 0<y<self.side_length:
            raise ValueError("Coords out of bounds")
        cell_x, cell_y = m.floor(x), m.floor(y)
        return self._get_cell(cell_x, cell_y)

    def get_cell_with_adjacent(self, x:float, y:float) -> list:
        if not 0<x<self.side_length or not 0<y<self.side_length:
            raise ValueError("Coords out of bounds")
        cell_x, cell_y = m.floor(x), m.floor(y)
        return self._get_cell_w_adjacent(cell_x, cell_y)

    def get_coords(self) -> Tuple[float, float]:
        if len(self.coords_list) == 0 or self.save_coords:
            coord = self.generate_random_coords()
            if self.save_coords:
                self.coords_list.append(coord)
            return coord
        return self.coords_list.pop(0)

    def generate_random_coords(self) -> Tuple[float, float]:
        return random.uniform(0, self.side_length), random.uniform(0, self.side_length)

    def did_last_lilypad_connect_edges(self) -> bool:
        if self.last_lilypad is None:
            return False
        cluster = self.last_lilypad.cluster.get_top()
        return cluster.left_connected and cluster.right_connected

    def run(self, timeout = 1000000) -> Tuple[bool, int]:
        if self.cluster is None:
            raise ValueError("Pond must have a cluster class to run")
        c = 0
        while not self.did_last_lilypad_connect_edges() and c < timeout:
            self.add_lilypad()
            c += 1
        return self.did_last_lilypad_connect_edges(), c
