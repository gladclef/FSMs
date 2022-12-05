import pathlib
import shutil
import time
from datetime import datetime
import winsound

def get_mod_time(fname, default=0):
    try:
        return pathlib.Path(file_a_name).stat().st_mtime
    except FileNotFoundError:
        return default

if __name__ == "__main__":
    file_a_name = "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/current_lab/vitis/current_lab/Debug/current_lab.elf"
    file_b_name = "C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/current_lab/exports/current_lab.elf"
    last_mod_time = get_mod_time(file_a_name)

    while True:
        curr_mod_time = get_mod_time(file_a_name, last_mod_time)

        if curr_mod_time != last_mod_time:
            while curr_mod_time != last_mod_time:
                last_mod_time = curr_mod_time
                time.sleep(0.15)
                curr_mod_time = get_mod_time(file_a_name, last_mod_time+1)

            print(f"({datetime.now()}) Updating file\n    from: {file_a_name}\n    to:   {file_b_name}")
            shutil.copyfile(file_a_name, file_b_name)
            winsound.PlaySound('ding.wav', winsound.SND_FILENAME)

        time.sleep(0.25)