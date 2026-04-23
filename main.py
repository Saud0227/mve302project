import numpy as np
import os
from queue import Queue, Empty
from threading import Thread
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

_input_queue = Queue()

def _stdin_listener():
    while True:
        try:
            _input_queue.put(input().strip().lower())
        except EOFError:
            break


def start_input_listener():
    t = Thread(target=_stdin_listener, daemon=True)
    t.start()


def stop_requested() -> bool:
    global input_queue
    pressed_stop = False
    while True:
        try:
            cmd = _input_queue.get_nowait()
        except Empty:
            break
        if cmd == "c":
            pressed_stop = True
    return pressed_stop


def terminal_run():
    print("Welcome to the Pond Simulation!")
    side_length = float(input("Enter the side length of the pond: "))
    lilypad_type = input("Enter the type of lilypad (circle/triangle): ").strip().lower()
    if lilypad_type == "circle":
        lilypad_class = CircleLilypad
    elif lilypad_type == "triangle":
        lilypad_class = TriangleLilypad
    else:
        print("Invalid lilypad type, defaulting to circle.")
        lilypad_class = CircleLilypad

    pond_type_input = input("Enter the type of pond (regular/coverage): ").strip().lower()
    if pond_type_input == "regular":
        pond_type = Pond
    elif pond_type_input == "coverage":
        pond_type = CoveragePond
    else:
        print("Invalid pond type, defaulting to regular.")
        pond_type = Pond

    if pond_type == CoveragePond and lilypad_class == TriangleLilypad:
        print("Triangle lilypads are not supported in coverage ponds. Defaulting to circle lilypads.")
        lilypad_class = CircleLilypad

    pop_size = int(input("Enter the number of simulations to run. If infinite, enter 0: "))

    if pop_size != 0:
        data_item = {side_length: {"data": []}}
        run_multiple(data_item, pop_size, lilypad_class=lilypad_class, pond_type=pond_type)
        print(f"Average number of lilypads needed to connect edges: {len(data_item["data"])}")
        return

    file_name = f"data_{'circle' if lilypad_class == CircleLilypad else 'triangle'}{'' if pond_type == Pond else '_full'}.txt"

    if not os.path.exists(file_name):
        with open(file_name, "w") as _:
            pass
    if os.path.getsize(file_name) > 100 * 1024 * 102:
        base_name, ext = os.path.splitext(file_name)
        num = 1
        while os.path.exists(f"{base_name}_{num}{ext}"):
            num += 1
        file_name = f"{base_name}_{num}{ext}"

    print(f"Running simulation with infinite population size. Data will be saved to {file_name}")
    pop_size = int(input(f"How many runs before saving data: (NOTE: Larger numbers should have less runs before saving) "))
    print("Press C to stop the simulation. It will exit when next saving point is reached. ctrl-c  will exit immediately without saving.")
    start_input_listener()

    # if data.txt doesn't exist, create it, no content


    while True:
        data_item = {side_length: {"data": []}}
        run_multiple(data_item, pop_size, lilypad_class=lilypad_class, pond_type=pond_type)
        with open(file_name, "a") as f:
            for data_point in data_item[side_length]["data"]:
                f.write(f"{side_length}:{data_point}\n")
        # if file is larger than 100mb, create a new file with an incremented number at the end
        if os.path.getsize(file_name) > 100 * 1024 * 102:
            base_name, ext = os.path.splitext(file_name)
            num = 1
            while os.path.exists(f"{base_name}_{num}{ext}"):
                num += 1
            file_name = f"{base_name}_{num}{ext}"
            print(f"File size exceeded 100mb, switching to new file: {file_name}")

        if stop_requested():
            print("Stopping simulation...")
            break








def main():
    Pond.cluster = Cluster

    terminal_run()

    # print(f"Running circle lilypads in regular pond...")
    # run_approximation(start=10, step=5, base_steps=5, predict_steps=3, size=100, multi_count=10,
    #                   lilypad_class=CircleLilypad, pond_type=Pond)
    # print(f"\nRunning triangle lilypads in regular pond...")
    # run_approximation(start=10, step=5, base_steps=5, predict_steps=3, size=100, multi_count=10,
    #                   lilypad_class=TriangleLilypad, pond_type=Pond)
    # print(f"\nRunning circle lilypads in coverage pond...")
    # run_approximation(start=10, step=5, base_steps=5, predict_steps=3, size=100, multi_count=10,
    #                   lilypad_class=CircleLilypad, pond_type=CoveragePond)


if __name__ == "__main__":
    main()
