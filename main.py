import matplotlib.pyplot as plt
from structs.lilypad import CircleLilypad, TriangleLilypad, Cluster
from structs.pond import Pond
import tkinter as tk
import time

def set_is_path(cluster: Cluster, to_set=True):
    for item in cluster.lilypads:
        item.part_of_path = to_set
    for item in cluster.child_clusters:
        set_is_path(item, to_set)


def generate_plot(pond: Pond, c: int = 0):
    for _, x_row in pond.grid.items():
        for _, cell in x_row.items():
            for lilypad in cell:
                color = "green" if lilypad.part_of_path else "blue"
                #plt.gca().add_patch(plt.Circle((lilypad.x, lilypad.y), 1, color=color))
                if isinstance(lilypad, CircleLilypad):
                    plt.gca().add_patch(plt.Circle((lilypad.x, lilypad.y), 1, color=color))
                elif isinstance(lilypad, TriangleLilypad):
                    # Använd hörnkoordinaterna i self.p
                    plt.gca().add_patch(plt.Polygon(lilypad.p, color=color))
    # set axis limits to the size of the pond
    plt.xlim(0, pond.side_length)
    plt.ylim(0, pond.side_length)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(f"Connected edges in {c} lilypads")
    plt.show()


def run_with_gui(pond):
    root = tk.Tk()
    root.title("Pond Simulation")

    canvas_size = 500
    canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
    canvas.pack()
    
    scale = canvas_size / pond.side_length  

    

    def draw_pond(lillypad):
        canvas.delete("all")
        scale = 500 / pond.side_length # Dynamisk skala
    
    # Bestäm färg för det vinnande klustret
        top_cluster = lillypad.cluster.get_top()
        is_winning = top_cluster.left_connected and top_cluster.right_connected
        color_for_cluster = "green" if is_winning else "blue"

        for _, x_row in pond.grid.items():
            for _, cell in x_row.items():
                for lp in cell:
                # Markera path eller använd klusterfärg
                    color = "purple" if lp.part_of_path else color_for_cluster
                
                    if isinstance(lp, CircleLilypad):
                    # Rita cirkel (x, y är centrum, radius=1)
                        canvas.create_oval(
                            (lp.x - 1) * scale, (lp.y - 1) * scale,
                            (lp.x + 1) * scale, (lp.y + 1) * scale,
                            fill=color, outline="white"
                        )
                    elif isinstance(lp, TriangleLilypad):
                        # Rita triangel med koordinaterna från lp.p
                        scaled_points = []
                        for px, py in lp.p:
                            scaled_points.extend([px * scale, py * scale])
                        canvas.create_polygon(scaled_points, fill=color, outline="white")
    

    # def draw_pond(lillypad):
    #     # clear the canvas
    #     canvas.delete("all")
    #     if lillypad.part_of_path:
    #         color_for_special = "purple"
    #     else:
    #         # temporary set part_of_path to true to make it visible, then set it back to false
    #         set_is_path(lillypad.cluster.get_top())
    #         color_for_special = "green"
    #     for _, x_row in pond.grid.items():
    #         for _, cell in x_row.items():
    #             for lilypad in cell:
    #                 color = color_for_special if lilypad.part_of_path else "blue"
    #                 x, y = lilypad.get_coords()
    #                 # if you click the lilypad, print it
    #                 def on_click(event, lilypad=lilypad):
    #                     print(f"Clicked on lilypad at coords {lilypad.get_coords()}, part of path: {lilypad.part_of_path}")
    #                     canvas.tag_bind(canvas.create_oval(x*100-100, y*100-100, x*100+100, y*100+100, fill=color), "<Button-1>", on_click)

    #     if color_for_special == "green":
    #         set_is_path(lillypad.cluster.get_top(), False)






    def add_lilypad_and_draw():
        pond.add_lilypad()
        draw_pond(pond.last_lilypad)
        if not pond.did_last_lilypad_connect_edges():
            # print(f"Left edge connected: {pond.last_lilypad.cluster.left_connected}, Right edge connected: {pond.last_lilypad.cluster.right_connected}")
            root.after(1000, add_lilypad_and_draw)
        else:
            set_is_path(pond.last_lilypad.cluster.get_top())
            draw_pond(pond.last_lilypad)

    add_lilypad_and_draw()
    root.mainloop()


def standard_run(pond):
    c = 0
    while not pond.did_last_lilypad_connect_edges() and c < 5000:
        pond.add_lilypad()
        c += 1

        if pond.last_lilypad:
            top = pond.last_lilypad.cluster.get_top()
        if top.left_connected and top.right_connected:
            set_is_path(top)
            print(c)

    # mark all lilypads in the cluster that connects the edges as part of the path
    set_is_path(pond.last_lilypad.cluster.get_top())



if __name__ == "__main__":
    

    Pond.cluster = Cluster
    side_l = 100
    #pond = Pond(side_l, CircleLilypad)
    pond = Pond(side_l, TriangleLilypad)

    #run_with_gui(pond)
    standard_run(pond)

    generate_plot(pond, len(pond.grid))
        


# (0.39621173766017204, 2.37483489464707)
# (0.04982293800321058, 3.7744942608968146)