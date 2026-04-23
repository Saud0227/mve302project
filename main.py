import time
import matplotlib.pyplot as plt
from structs.lilypad import CircleLilypad, Cluster
from structs.pond import Pond
import tkinter as tk
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_plot(pond: Pond, c: int = 0):
    pond.color_clusters()
    for _, x_row in pond.grid.items():
        for _, cell in x_row.items():
            for lilypad in cell:
                plt.gca().add_patch(plt.Circle((lilypad.x, lilypad.y), 1, color=lilypad.color))
    # set axis limits to the size of the pond
    plt.xlim(0, pond.side_length)
    plt.ylim(0, pond.side_length)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(f"Connected edges in {c} lilypads")
    plt.show()

def gui_draw_pond(canvas, unit, pond):
    # clear the canvas
    canvas.delete("all")
    pond.color_clusters()

    for _, x_row in pond.grid.items():
        for _, cell in x_row.items():
            for lilypad in cell:
                x, y = lilypad.get_coords()
                canvas.create_oval(x * unit - unit, y * unit - unit, x * unit + unit, y * unit + unit, fill=lilypad.color)

def run_with_gui(pond, delay_time = 1000):
    root = tk.Tk()
    root.title("Pond Simulation")

    canvas = tk.Canvas(root, width=500, height=500)
    unit = 500 / pond.side_length
    canvas.pack()

    while pond.did_last_lilypad_connect_edges():
        pond.add_lilypad()
        gui_draw_pond(canvas, unit, pond)
        root.update()
        time.sleep(delay_time/1000)

def step_run(pond, length=0):
    if length==0:
        length = len(pond.coords_list)
    for i in range(length):
        coords = pond.add_lilypad()
        print(f"New pad generated, coords: {coords}, left edge connected: {pond.last_lilypad.cluster.left_connected}, right edge connected: {pond.last_lilypad.cluster.right_connected}")
        # wait until user types something in the console before continuing
        c = True
        while c:
            signal = input("Press Enter to continue...")
            if signal == "":
                c = False
            elif signal == "p":
                generate_plot(pond)
            elif signal == "cluster":
                print(f"Pad in cluster with {len(pond.last_lilypad.cluster.get_all_lilypads())} lilypads.")
            elif signal == "c":
                return None
    return None


def run_multiple(data_set, size, multi_count=10, pad_class=CircleLilypad, timemout=1000000):
    for pond_size in data_set:
        print("Running pond size: ", pond_size)
        sum = 0

        with (ThreadPoolExecutor(max_workers=multi_count) as pool):
            futures = {pool.submit(Pond.quick_run, pond_size, pad_class, timemout): i for i in range(size)}

            for future in as_completed(futures):
                f, c = future.result()
                if not f:
                    raise TimeoutError(f"Failed to connect edges in {pond_size}x{pond_size} pond after {timemout} lilypads")
                data_set[pond_size]["data"].append(c)
                sum += c
        data_set[pond_size]["average"] = sum/size


def run_aproximation(start, step, base_steps, predict_steps, size):
    base_set = {i:{"data":[]} for i in range(start, start+base_steps*step, step)}
    run_multiple(base_set, size)
    print("Base set generated, now predicting values for larger ponds...")

    x = list(base_set.keys())
    y = list(data_item["average"] for data_item in base_set.values())
    print("Base set (x, y): ", list(zip(x, y)))
    coeffs = np.polyfit(x, y, 1)
    print(f"Linear regression line: y = {coeffs[0]}x + {coeffs[1]}")

    # get 2nd degree polynomial regression line for the base set
    coeffs2 = np.polyfit(x, y, 2)
    print(f"2nd degree polynomial regression line: y = {coeffs2[0]}x^2 + {coeffs2[1]}x + {coeffs2[2]}")

    guess_set = {i:{"linear": int(coeffs[0]*i + coeffs[1]),"quadratic": int(coeffs2[0]*i**2 + coeffs2[1]*i + coeffs2[2]), "data":[]} for i in range(start+base_steps*step, start+base_steps*step+predict_steps*step, step)}

    run_multiple(guess_set, size)

    print("Guess set generated, now comparing predictions to actual values...")
    for pond_size, data_item in guess_set.items():
        linear_error = abs(data_item["linear"] - data_item["average"])
        quadratic_error = abs(data_item["quadratic"] - data_item["average"])
        print(f"Pond size: {pond_size}, actual average: {data_item['average']}, linear prediction: {data_item['linear']} (error: {linear_error}), quadratic prediction: {data_item['quadratic']} (error: {quadratic_error})")




if __name__ == "__main__":
    Pond.cluster = Cluster
    run_aproximation(start=10, step=10, base_steps=5, predict_steps=5, size=100)


    # Pond.cluster = Cluster
    # side_l = 50
    # pond = Pond(side_l, CircleLilypad)
    # run_with_gui(pond)
    # set time
    # start_t = time.time()
    # t, c = standard_run(pond)
    # delta_t = time.time() - start_t

    # print(f'Connected edges: {'Yes' if t else 'No'}, lilypads generated: {c}, time taken: {delta_t:.2f} seconds')

    # generate_plot(pond, c)
