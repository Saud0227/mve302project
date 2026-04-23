import matplotlib.pyplot as plt
import tkinter as tk
import time

from .pond import Pond, CoveragePond
from .lilypad import CircleLilypad, TriangleLilypad, Cluster


def generate_plot(pond: Pond, c: int = 0):
    pond.color_clusters()
    for _, x_row in pond.grid.items():
        for _, cell in x_row.items():
            for lilypad in cell:
                if isinstance(lilypad, CircleLilypad):
                    plt.gca().add_patch(plt.Circle((lilypad.x, lilypad.y), 1, color=lilypad.color))
                elif isinstance(lilypad, TriangleLilypad):
                    # Använd hörnkoordinaterna i self.p
                    plt.gca().add_patch(plt.Polygon(lilypad.p, color=lilypad.color))
    # set axis limits to the size of the pond
    plt.xlim(0, pond.side_length)
    plt.ylim(0, pond.side_length)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(f"Connected edges in {c} lilypads")
    plt.show()


def _gui_draw_pond(canvas, unit, pond):
    # clear the canvas
    canvas.delete("all")
    pond.color_clusters()

    for _, x_row in pond.grid.items():
        for _, cell in x_row.items():
            for lilypad in cell:
                if isinstance(lilypad, CircleLilypad):
                    x, y = lilypad.get_coords()
                    canvas.create_oval(unit*(x-1), unit*(y-1), unit*(x+1), unit*(y+1), fill=lilypad.color)
                elif isinstance(lilypad, TriangleLilypad):
                    # Rita triangel med koordinaterna från lilypad.p
                    scaled_points = []
                    for px, py in lilypad.p:
                        scaled_points.extend([px * unit, py * unit])
                    canvas.create_polygon(scaled_points, fill=lilypad.color)

def run_edges_with_gui(pond, delay_time = 1000):
    root = tk.Tk()
    root.title("Pond Simulation")

    canvas = tk.Canvas(root, width=500, height=500)
    unit = 500 / pond.side_length
    canvas.pack()

    c = 0

    while not pond.is_complete():
        pond.add_lilypad()
        c += 1
        _gui_draw_pond(canvas, unit, pond)
        root.update()
        time.sleep(delay_time/1000)

    print(f"Edges connected in {c} lilypads!")
    root.mainloop()


def run_coverage_with_gui(pond, delay_time=10):
    root = tk.Tk()
    root.title("Pond Coverage Simulation")

    canvas = tk.Canvas(root, width=500, height=500, bg="white")
    unit = 500 / pond.side_length
    canvas.pack()

    c = 0
    # Loop until the NumPy grid says 100% of points are covered
    while not pond.is_complete():
        pond.add_lilypad()
        c += 1

        # We can optimize this by only drawing the NEW lilypad instead of redrawing all of them
        lilypad = pond.last_lilypad
        x, y = lilypad.get_coords()

        # Draw the single new shape
        if isinstance(lilypad, CircleLilypad):
            canvas.create_oval(unit*(x-1), unit*(y-1), unit*(x+1), unit*(y+1), fill="green", outline="darkgreen")
        elif isinstance(lilypad, TriangleLilypad):
            scaled_points = []
            for px, py in lilypad.p:
                scaled_points.extend([px * unit, py * unit])
            canvas.create_polygon(scaled_points, fill="green", outline="darkgreen")

        # Update the window Title to show progress
        root.title(f"Coverage Simulation - {c} Lilypads dropped")

        root.update()
        time.sleep(delay_time / 1000)

    print(f"Pond fully covered in {c} lilypads!")
    root.mainloop() # Keeps the window open after it finishes


def run_with_gui(pond, delay_time=1000):
    if isinstance(pond, CoveragePond):
        run_coverage_with_gui(pond, delay_time)
    elif isinstance(pond, Pond):
        run_edges_with_gui(pond, delay_time)
    else:
        raise ValueError("Invalid pond type for GUI. Must be Pond or CoveragePond.")