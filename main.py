
from structs.lilypad import CircleLilypad, TriangleLilypad, Cluster, AnyLilypad
from structs.gui import generate_plot, run_with_gui
from structs.pond import Pond, CoveragePond, AnyPond
from structs.terminal import terminal_run

def main():
    Pond.cluster = Cluster

    terminal_run()


if __name__ == "__main__":
    main()
