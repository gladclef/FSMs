import pathlib
import shutil
import time
from datetime import datetime
import winsound
import psutil

def get_mod_time(fname, default=0):
    try:
        return pathlib.Path(fname).stat().st_mtime
    except FileNotFoundError:
        return default

if __name__ == "__main__":
    file_pairs = [
        [ "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/vitis/KMeans/Debug/KMeans.elf",
          "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/BITSTREAMS/current_lab.elf" ],
        [ "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/BITSTREAMS/design_1_wrapper.xsa",
          None ],
        [ "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/C_code/c_algo.c",
          "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/vitis/KMeans/src/c_algo.c" ],
        [ "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/C_code/c_algo.h",
          "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/vitis/KMeans/src/c_algo.h" ],
        [ "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/C_code/kmeans_codesign_starter.c",
          "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/project/vitis/KMeans/src/kmeans_codesign_starter.c" ]
    ]
    last_mod_times = [0 for fp in file_pairs]

    while True:
        for i, fp in enumerate(file_pairs):
            file_a_name, file_b_name = fp
            curr_mod_time = get_mod_time(file_a_name, last_mod_times[i])

            if curr_mod_time != last_mod_times[i]:
                while curr_mod_time != last_mod_times[i]:
                    last_mod_times[i] = curr_mod_time
                    time.sleep(0.15)
                    curr_mod_time = get_mod_time(file_a_name, last_mod_times[i]+1)

                if file_b_name != None:
                    print(f"({datetime.now()}) Updating file\n    from: {file_a_name}\n    to:   {file_b_name}")
                    shutil.copyfile(file_a_name, file_b_name)
                    winsound.PlaySound('ding.wav', winsound.SND_FILENAME)
                else:
                    print(f"({datetime.now()}) File changed: {file_a_name}")
                    winsound.PlaySound('ding.wav', winsound.SND_FILENAME)

        #print("%02d " % psutil.cpu_percent(1), end="")
        time.sleep(0.25)