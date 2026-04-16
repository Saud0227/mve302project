import matplotlib.pyplot as plt
from structs.lilypad import CircleLilypad, Cluster
from structs.pond import Pond
import tkinter as tk

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
                plt.gca().add_patch(plt.Circle((lilypad.x, lilypad.y), 1, color=color))
    # set axis limits to the size of the pond
    plt.xlim(0, pond.side_length)
    plt.ylim(0, pond.side_length)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(f"Connected edges in {c} lilypads")
    plt.show()


def run_with_gui(pond):
    root = tk.Tk()
    root.title("Pond Simulation")

    canvas = tk.Canvas(root, width=500, height=500)
    canvas.pack()

    def draw_pond(lillypad):
        # clear the canvas
        canvas.delete("all")
        if lillypad.part_of_path:
            color_for_special = "purple"
        else:
            # temporary set part_of_path to true to make it visible, then set it back to false
            set_is_path(lillypad.cluster.get_top())
            color_for_special = "green"
        for _, x_row in pond.grid.items():
            for _, cell in x_row.items():
                for lilypad in cell:
                    color = color_for_special if lilypad.part_of_path else "blue"
                    x, y = lilypad.get_coords()
                    # if you click the lilypad, print it
                    def on_click(event, lilypad=lilypad):
                        print(f"Clicked on lilypad at coords {lilypad.get_coords()}, part of path: {lilypad.part_of_path}")
                    canvas.tag_bind(canvas.create_oval(x*100-100, y*100-100, x*100+100, y*100+100, fill=color), "<Button-1>", on_click)

        if color_for_special == "green":
            set_is_path(lillypad.cluster.get_top(), False)






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
    while not pond.did_last_lilypad_connect_edges() and c < 100:
        pond.add_lilypad()
        c += 1

    # mark all lilypads in the cluster that connects the edges as part of the path
    set_is_path(pond.last_lilypad.cluster.get_top())



if __name__ == "__main__":


    Pond.cluster = Cluster
    side_l = 5
    pond = Pond(side_l, CircleLilypad)

    run_with_gui(pond)

    generate_plot(pond)


# (0.39621173766017204, 2.37483489464707)
# (0.04982293800321058, 3.7744942608968146)