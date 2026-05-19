import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from structs.lilypad import CircleLilypad, TriangleLilypad, Cluster, AnyLilypad
from structs.gui import generate_plot, run_with_gui
from structs.pond import Pond, CoveragePond, AnyPond

def step_run(pond, length=0):
    if length == 0:
        length = len(pond.coords_list)
    for i in range(length):
        coords = pond.add_lilypad()
        print(
            f"New pad generated, coords: {coords}, left edge connected: {pond.last_lilypad.cluster.left_connected}, right edge connected: {pond.last_lilypad.cluster.right_connected}")
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


def run_multiple(data_set, size, multi_count=10, lilypad_class: AnyLilypad = CircleLilypad, pond_type: AnyPond = Pond,
                 timemout=1000000):
    for pond_size in data_set:
        print("Running pond size: ", pond_size)
        sum = 0

        with (ThreadPoolExecutor(max_workers=multi_count) as pool):
            futures = {pool.submit(pond_type.quick_run, pond_size, lilypad_class, timemout): i for i in range(size)}

            for future in as_completed(futures):
                f, c = future.result()
                if not f:
                    raise TimeoutError(
                        f"Failed to connect edges in {pond_size}x{pond_size} pond after {timemout} lilypads")
                data_set[pond_size]["data"].append(c)
                sum += c
        data_set[pond_size]["average"] = sum / size


def run_approximation(start, step, base_steps, predict_steps, size, multi_count=10,
                      lilypad_class: AnyLilypad = CircleLilypad, pond_type: AnyPond = Pond, timemout=1000000):
    base_set = {i: {"data": []} for i in range(start, start + base_steps * step, step)}
    run_multiple(base_set, size, multi_count, lilypad_class, pond_type, timemout)
    print("Base set generated, now predicting values for larger ponds...")

    x = list(base_set.keys())
    y = list(data_item["average"] for data_item in base_set.values())
    print("Base set (x, y): ", list(zip(x, y)))
    coeffs = np.polyfit(x, y, 1)
    print(f"Linear regression line: y = {coeffs[0]}x + {coeffs[1]}")

    # get 2nd degree polynomial regression line for the base set
    coeffs2 = np.polyfit(x, y, 2)
    print(f"2nd degree polynomial regression line: y = {coeffs2[0]}x^2 + {coeffs2[1]}x + {coeffs2[2]}")

    guess_set = {i: {"linear": int(coeffs[0] * i + coeffs[1]),
                     "quadratic": int(coeffs2[0] * i ** 2 + coeffs2[1] * i + coeffs2[2]), "data": []} for i in
                 range(start + base_steps * step, start + base_steps * step + predict_steps * step, step)}

    run_multiple(guess_set, size, multi_count, lilypad_class, pond_type, timemout)

    print("Guess set generated, now comparing predictions to actual values...")
    for pond_size, data_item in guess_set.items():
        linear_error = abs(data_item["linear"] - data_item["average"])
        quadratic_error = abs(data_item["quadratic"] - data_item["average"])
        print(
            f"Pond size: {pond_size}, actual average: {data_item['average']},"
            f"linear prediction: {data_item['linear']} (error: {linear_error}),"
            f"quadratic prediction: {data_item['quadratic']} (error: {quadratic_error})")


def main():
    Pond.cluster = Cluster

    # print(f"Running circle lilypads in regular pond...")
    # run_approximation(start=10, step=5, base_steps=5, predict_steps=3, size=100, multi_count=10,
    #                   lilypad_class=CircleLilypad, pond_type=Pond)
    # print(f"\nRunning triangle lilypads in regular pond...")
    # run_approximation(start=10, step=5, base_steps=5, predict_steps=3, size=100, multi_count=10,
    #                   lilypad_class=TriangleLilypad, pond_type=Pond)
    # print(f"\nRunning circle lilypads in coverage pond...")
    # run_approximation(start=10, step=5, base_steps=5, predict_steps=3, size=100, multi_count=10,
    #                   lilypad_class=CircleLilypad, pond_type=CoveragePond)
    run_approximation(start=10, step=5, base_steps=5, predict_steps=3, size=50, lilypad_class=TriangleLilypad, pond_type=CoveragePond)


if __name__ == "__main__":
    main()
