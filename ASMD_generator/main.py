from PIL import Image

from Program import Program

if __name__ == "__main__":
    program = Program("C:/Users/gladc/Documents/School/UNM/ECE_595_intermediate_logic_design/project/vhdl/RenderText.vhd")
    program.print(0)

    # img = Image.new( 'RGB', (255,255), "white") # Create a new black image
    # pixels = img.load() # Create the pixel map
    # img.show()