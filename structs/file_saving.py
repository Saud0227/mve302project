import os

from .lilypad import CircleLilypad, TriangleLilypad, AnyLilypad
from .pond import Pond, CoveragePond, AnyPond
from .run_configs import run_multiple


def check_file_size(f_name: str, size_max: int) -> str:
    size_max *= 1024**2
    if os.path.getsize(f_name) < size_max:
        return f_name
    base_name, ext = os.path.splitext(f_name)
    num = 1
    while os.path.exists(f"{base_name}_{num}{ext}"):
        num += 1
    return f"{base_name}_{num}{ext}"


def setup_file_saving(f_name: str, mb_limit: int) -> str:
    if os.path.exists(f_name):
        base_name, ext = os.path.splitext(f_name)
        num = 1
        while os.path.exists(f"{base_name}_{num}{ext}"):
            num += 1
        f_name = f"{base_name}_{num}{ext}"
        with open(f_name, "w") as _:
            pass
    else:
        with open(f_name, "w") as _:
            pass
    return check_file_size(f_name, mb_limit)

def terminal_save_run(pond_type: AnyPond, lilypad_type: AnyLilypad, side_l, batch_size: int, n_times: int, mutli_count=10):
    n_completed_runs = 0
    file_size_max = 10

    file_name = f"data_{'circle' if lilypad_type == CircleLilypad else 'triangle'}{'' if pond_type == Pond else '_full'}_s{side_l}.txt"
    file_name = setup_file_saving(file_name, 10)

    while n_times != n_completed_runs:
        data_item = {side_l: {"data": []}}
        run_multiple(data_item, batch_size, mutli_count, lilypad_type, pond_type)
        with open(file_name, "a") as f:
            for data_point in data_item[side_l]["data"]:
                f.write(f"{data_point}\n")

        file_name = check_file_size(file_name, file_size_max)
        n_completed_runs += 1

def run_range_save(pond_type: AnyPond, lilypad_type: AnyLilypad, side_l: list, batch_size: int, n_times: int, multi_count=10):
    # make dir based on list[0] and list[-1]
    dir_name = f"data_s{side_l[0]}_to_s{side_l[-1]}"
    if os.path.exists(dir_name):
        dir_index = 1
        while os.path.exists(f"{dir_name}_{dir_index}"):
            dir_index += 1
        dir_name = f"{dir_name}_{dir_index}"

    os.makedirs(dir_name)

    # change dir
    os.chdir(dir_name)

    for side in side_l:
        terminal_save_run(pond_type, lilypad_type, side, batch_size, n_times, multi_count)