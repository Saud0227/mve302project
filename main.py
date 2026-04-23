from structs.lilypad import CircleLilypad, TriangleLilypad, Cluster
from structs.gui import generate_plot, run_with_gui
from structs.pond import Pond, CoveragePond
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def run_approximation(start, step, base_steps, predict_steps, size, lillypad_class=CircleLilypad):
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

def main():
    Pond.cluster = Cluster

    # Use a small pond (Area n=100) so it doesn't take all day to animate!
    pond_side = 10
    print((CircleLilypad is CircleLilypad))
    # my_pond = Pond(pond_side, CircleLilypad)
    my_pond = CoveragePond(pond_side, CircleLilypad)

    run_coverage_with_gui(my_pond)


    # run_approximation(10, 10, 5, 5, 100, CircleLilypad)

    # pond = Pond(50, TriangleLilypad)
    pond = Pond(20, CircleLilypad)
    run_with_gui(pond, 100)



if __name__ == "__main__":
    main()