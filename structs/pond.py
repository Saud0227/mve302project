import math as m
import random
from typing import Dict, Tuple
import numpy as np

from structs.lilypad import Cluster, CircleLilypad, TriangleLilypad, AnyLilypad

type AnyPond = Pond | CoveragePond

class Pond:

    cluster = None
    color_list = ["green", "blue", "purple", "orange", "yellow", "cyan", "magenta", "red"]

    @classmethod
    def quick_run(cls, side: float, lilypad_class: AnyLilypad, timeout=1000000):
        pond = cls(side, lilypad_class)
        return pond.run(timeout)

    @classmethod
    def new_from_area(cls, area: int, lilypad_class: AnyLilypad, test_points_per_cell: int = 0):
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

    def __init__(self, side: float, lilypad_class: AnyLilypad):
        self.side_length = side
        self.grid: Dict[int, Dict[int, list]] = {}
        self.lilypad_class = lilypad_class
        self.last_lilypad = None
        self.all_clusters = []
        self.coords_list = []
        self.save_coords = False

    def add_lilypad(self):
        x, y = self.get_coords()
        lilypad = self.lilypad_class(x, y)

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

        return x, y

    def add_to_cell(self, lilypad: AnyLilypad):
        x, y = lilypad.get_coords()
        t_x, t_y = m.floor(x), m.floor(y)
        self._add_to_cell(lilypad, t_x, t_y)

    def _add_to_cell(self, lilypad: AnyLilypad, x, y):
        if x not in self.grid:
            self.grid[x] = {}
        if y not in self.grid[x]:
            self.grid[x][y] = []
        self.grid[x][y].append(lilypad)

    def _get_cell(self, x: int, y: int) -> list:
        return self.grid.get(x, {}).get(y, [])

    def _get_cell_w_adjacent(self, t_x: int, t_y: int) -> list:
        out = []
        for x in range(t_x - 2, t_x + 3):
            # NOTE: We don't care about out of bounds here because _get_cell will just return an empty list
            for y in range(t_y - 2, t_y + 3):
                out += self._get_cell(x, y)
        return out

    def get_cell_from_coords(self, x: float, y: float) -> list:
        if not 0 < x < self.side_length or not 0 < y < self.side_length:
            raise ValueError("Coords out of bounds")
        cell_x, cell_y = m.floor(x), m.floor(y)
        return self._get_cell(cell_x, cell_y)

    def get_cell_with_adjacent(self, x: float, y: float) -> list:
        if not 0 < x < self.side_length or not 0 < y < self.side_length:
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

    def is_complete(self) -> bool:
        if self.last_lilypad is None:
            return False
        cluster = self.last_lilypad.cluster.get_top()
        return cluster.left_connected and cluster.right_connected

    def run(self, timeout: int = 1000000) -> Tuple[bool, int]:
        if self.cluster is None:
            raise ValueError("Pond must have a cluster class to run")
        c = 0
        while not self.is_complete() and c < timeout:
            self.add_lilypad()
            c += 1
        return self.is_complete(), c

class CoveragePond(Pond):

    def __init__(self, side: float, lilypad_class: AnyLilypad, points_per_unit: int = 10):
        # Tillåt nu både CircleLilypad och TriangleLilypad
        if lilypad_class not in [CircleLilypad, TriangleLilypad]:
            raise NotImplementedError("CoveragePond stöder endast CircleLilypad eller TriangleLilypad")
        super().__init__(side, lilypad_class)

        self.resolution = points_per_unit
        self.grid_size = int(self.side_length * self.resolution)

        # 2D array av True (uncovered). När en punkt täcks blir den False.
        self.uncovered_grid = np.ones((self.grid_size, self.grid_size), dtype=bool)
        self.uncovered_count = self.grid_size * self.grid_size

        # För-kalkylera geometriska koordinater
        x_coords = np.linspace(0, self.side_length, self.grid_size)
        y_coords = np.linspace(0, self.side_length, self.grid_size)
        self.grid_x, self.grid_y = np.meshgrid(x_coords, y_coords)

    def add_lilypad(self):
        """
        Uppdaterar boolean-rutnätet när ett liljeblad (cirkel eller triangel) släpps.
        """
        x, y = self.get_coords()
        lilypad = self.lilypad_class(x, y)
        self.last_lilypad = lilypad

        # 1. Bestäm bounding box (omfång) baserat på lilypad-typ
        if isinstance(lilypad, CircleLilypad):
            r = lilypad.radius
            min_x, max_x = x - r, x + r
            min_y, max_y = y - r, y + r
        elif isinstance(lilypad, TriangleLilypad):
            # Hämta x- och y-koordinater från triangelns hörn (.p)
            pts = np.array(lilypad.p)
            min_x, max_x = np.min(pts[:, 0]), np.max(pts[:, 0])
            min_y, max_y = np.min(pts[:, 1]), np.max(pts[:, 1])
        else:
            raise TypeError("Okänd lilypad-typ")

        # Översätt till matrisindex (clampa mot dammens gränser)
        min_x_idx = max(0, int(min_x * self.resolution))
        max_x_idx = min(self.grid_size, int(max_x * self.resolution) + 1)
        min_y_idx = max(0, int(min_y * self.resolution))
        max_y_idx = min(self.grid_size, int(max_y * self.resolution) + 1)

        # Skapa sub-grids för det drabbade området
        sub_x = self.grid_x[min_y_idx:max_y_idx, min_x_idx:max_x_idx]
        sub_y = self.grid_y[min_y_idx:max_y_idx, min_x_idx:max_x_idx]
        sub_uncovered = self.uncovered_grid[min_y_idx:max_y_idx, min_x_idx:max_x_idx]

        # 2. Skapa mask för övertäckning (Beror på form)
        if isinstance(lilypad, CircleLilypad):
            dist_sq = (sub_x - x) ** 2 + (sub_y - y) ** 2
            covered_mask = dist_sq <= lilypad.radius ** 2
            
        elif isinstance(lilypad, TriangleLilypad):
            # Hämta de tre hörnpunkterna
            p0, p1, p2 = lilypad.p
            
            # Algoritm för punkt-i-triangel via 2D-korsprodukt (Edge function)
            # En punkt är inuti om den ligger på samma "sida" om alla tre linjesegment.
            def sign(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
                return (p1_x - p3_x) * (p2_y - p3_y) - (p2_x - p3_x) * (p1_y - p3_y)

            # Kör vektoralgebran direkt på NumPy-matriserna för snabb beräkning
            d1 = sign(sub_x, sub_y, p0[0], p0[1], p1[0], p1[1])
            d2 = sign(sub_x, sub_y, p1[0], p1[1], p2[0], p2[1])
            d3 = sign(sub_x, sub_y, p2[0], p2[1], p0[0], p0[1])

            # Kolla om tecknen är likadana (antingen alla >= 0 eller alla <= 0)
            has_neg = (d1 < 0) | (d2 < 0) | (d3 < 0)
            has_pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
            
            covered_mask = ~(has_neg & has_pos)

        # 3. Räkna nya täckta punkter & Uppdatera matrisen
        newly_covered = sub_uncovered & covered_mask
        self.uncovered_count -= np.sum(newly_covered)
        sub_uncovered[covered_mask] = False

    def is_complete(self) -> bool:
        return self.uncovered_count <= 0
