import math as m
import numpy as np
from typing import Tuple


class Lilypad:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.left_connected = None
        self.right_connected = None
        self.cluster = None
        self.part_of_path = False

    def _check_edge_connections(self, edge_x: float ) -> None:
        raise NotImplementedError("This method should be overridden by subclasses")

    def is_touching(self, other) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_coords(self) -> Tuple[float, float]:
        return self.x, self.y

    def smart_edge_check(self, edge_x: float) -> None:
        # only check edge connections if cluster isn't already connected to that edge
        if self.cluster is None:
            raise ValueError("Lilypad must be part of a cluster to check edge connections")
        l_checked = False
        if not self.cluster.left_connected:
            self._check_edge_connections(edge_x)
            self.cluster.left_connected = self.left_connected
            l_checked = True
        if not self.cluster.right_connected:
            if not l_checked:
                self._check_edge_connections(edge_x)
            self.cluster.right_connected = self.right_connected


class CircleLilypad(Lilypad):

    radius = 1

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        # radius is 1, so area is pi

    def is_touching(self, other) -> bool:
        if isinstance(other, CircleLilypad):
            return (self.x - other.x)**2 + (self.y - other.y)**2 <= (self.radius*2)**2
        else:
            raise NotImplementedError("This method should be overridden by subclasses")

    def _check_edge_connections(self, edge_x: float) -> None:
        self.left_connected = self.x - self.radius <= 0
        self.right_connected = self.x + self.radius >= edge_x



class TriangleLilypad(Lilypad):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.area = m.pi
        self.height = (m.pi*3**0.5)**0.5
        self.side = (m.pi*4/(3**0.5))**0.5
        self.axes = ((0,1),(3**0.5/2,0.5),(-3**0.5/2,0.5))
        self.p = [(self.x, self.y+2/3*self.height),(self.x-self.side/2, self.y-1/3*self.height),(self.x+self.side/2, self.y-1/3*self.height)]

    def is_touching(self, other):
        dist_sq = (self.x-other.x)**2 + (self.y-other.y)**2
        if dist_sq > (2 * 2/3*self.height)**2: 
            return False
        for axis in self.axes:
            proj1 = np.dot(self.p, axis)
            proj2 = np.dot(other.p, axis)

            min1, max1 = np.min(proj1), np.max(proj1)
            min2, max2 = np.min(proj2), np.max(proj2)

            if max1 < min2 or max2 < min1:
                return False
        return True
        
    def _check_edge_connections(self, edge_x: float) -> None:
        self.left_connected = self.p[1][1] <= 0
        self.right_connected = self.p[2][1] >= edge_x
class Cluster:

    @classmethod
    def merge_clusters(cls, *clusters) -> Cluster:
        merged_cluster = cls()
        left_connected = False
        right_connected = False
        for cluster in clusters:
            left_connected = left_connected or cluster.left_connected
            right_connected = right_connected or cluster.right_connected
            cluster.parent_cluster = merged_cluster

        merged_cluster.child_clusters = clusters
        merged_cluster.left_connected = left_connected
        merged_cluster.right_connected = right_connected

        return merged_cluster

    def __init__(self):
        self.lilypads = []
        self.parent_cluster = None
        self.child_clusters = []
        self.left_connected = False
        self.right_connected = False

    def get_top(self) -> Cluster:
        if self.parent_cluster is not None:
            return self.parent_cluster.get_top()
        return self

    def add_lilypad(self, lilypad: Lilypad) -> None:
        self.lilypads.append(lilypad)



if __name__ == "__main__":
    l1 = CircleLilypad(0.39621173766017204, 2.37483489464707)
    l2 = CircleLilypad(0.04982293800321058, 3.7744942608968146)

    l1x, l1y = l1.get_coords()
    l2x, l2y = l2.get_coords()
    print((l1x-l2x)**2 + (l1y-l2y)**2)

    print(l1.is_touching(l2))

t1 = TriangleLilypad(0.51212, 3.342)
t2 = TriangleLilypad(0.80002, 5.6702)
print(t1.is_touching(t2))
print(t1._check_edge_connections(5.02))