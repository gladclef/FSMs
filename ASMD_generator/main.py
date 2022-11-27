import pyperclip

from Program import Program

if __name__ == "__main__":
    program = Program("C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/current_lab/vhdl/Histo.vhd")
    sval = program.print(3)
    pyperclip.copy(sval)

    fsm_str = program.get_fsm_table()
    print(fsm_str)
    pyperclip.copy(fsm_str)