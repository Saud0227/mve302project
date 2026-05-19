import time

from structs.lilypad import CircleLilypad, TriangleLilypad, Cluster, AnyLilypad
from structs.gui import generate_plot, run_with_gui
from structs.pond import Pond, CoveragePond, AnyPond
from structs.file_saving import terminal_save_run

def main():
    Pond.cluster = Cluster
    # get curent time
    start_time = time.time()
    terminal_save_run(Pond, CircleLilypad, 100, 1000, 1, 15)
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
