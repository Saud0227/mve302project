import os
from collections.abc import Callable
from queue import Queue, Empty
from threading import Thread
from typing import Optional, Tuple

from .lilypad import CircleLilypad, TriangleLilypad, AnyLilypad
from .pond import Pond, CoveragePond, AnyPond
from .run_configs import run_multiple

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

def terminal_dialog():
    """
    Prompts user to enter data needed to do a non-gui run.
    :return:
    """
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
        # do method call
        return

    print(f"Running simulation with infinite population size. Data will be saved to {file_name}")
    pop_size = int(
        input(f"How many runs before saving data: (NOTE: Larger numbers should have less runs before saving) "))
    print(
        "Press C to stop the simulation. It will exit when next saving point is reached. ctrl-c  will exit immediately without saving.")

class CustomFileHandler:


    def __init(self, f_name):
        pass

    def get_new_path

def check_file_size(f_name: str, size_max: int) -> str:
    if os.path.getsize(f_name) < 100 * 1024 * 102:
        return f_name
    base_name, ext = os.path.splitext(f_name)
    num = 1
    while os.path.exists(f"{base_name}_{num}{ext}"):
        num += 1
    return f"{base_name}_{num}{ext}"


def setup_file_saving(f_name: str) -> Callable[Tuple[int, int], None]:
    if os.path.exists(f_name):
        base_name, ext = os.path.splitext(f_name)
        num = 1
        while os.path.exists(f"{base_name}_{num}{ext}"):
            num += 1
        f_name = f"{base_name}_{num}{ext}"

    if os.path.getsize(f_name) > 100 * 1024 * 102:
        base_name, ext = os.path.splitext(f_name)
        num = 1
        while os.path.exists(f"{base_name}_{num}{ext}"):
            num += 1
        file_name = f"{base_name}_{num}{ext}"



def terminal_run(pond_type: AnyPond, lilypad_type: AnyLilypad, side_l, batch_size: int, n_times: Optional[int], file_saving: bool, progress_bar: bool):
    n_completed_runs = 0
    if n_times is None:
        start_input_listener()

    if file_saving:
        file_name = f"data_{'circle' if lilypad_type == CircleLilypad else 'triangle'}{'' if pond_type == Pond else '_full'}.txt"

        if not os.path.exists(file_name):
            with open(file_name, "w") as _:
                pass
        if os.path.getsize(file_name) > 100 * 1024 * 102:
            base_name, ext = os.path.splitext(file_name)
            num = 1
            while os.path.exists(f"{base_name}_{num}{ext}"):
                num += 1
            file_name = f"{base_name}_{num}{ext}"

    while n_times != n_completed_runs:
        data_item = {side_l: {"data": []}}
        run_multiple(data_item, pop_size, lilypad_class=lilypad_class, pond_type=pond_type)
        if file_saving:
            with open(file_name, "a") as f:
                for data_point in data_item[side_l]["data"]:
                    f.write(f"{side_l}:{data_point}\n")
        # if file is larger than 100mb, create a new file with an incremented number at the end
        if file_saving and os.path.getsize(file_name) > 100 * 1024 * 102:
            base_name, ext = os.path.splitext(file_name)
            num = 1
            while os.path.exists(f"{base_name}_{num}{ext}"):
                num += 1
            file_name = f"{base_name}_{num}{ext}"
            print(f"File size exceeded 100mb, switching to new file: {file_name}")

        if n_times is None and stop_requested():
            print("Stopping simulation...")
            break
        elif n_times is not None:
            n_completed_runs += 1