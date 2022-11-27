import os

from PIL import Image


# Get the pixels values from an image.
# from https://www.folkstalk.com/tech/python-how-to-get-pixel-values-from-image-with-code-examples/
def get_pixels(image_path: str) -> tuple[int, int, list[tuple[int,int,int,int]]]:
    image = Image.open(image_path)
    pixel_values = list(image.getdata())
    return image.width, image.height, pixel_values

def get_bitmask(width: int, height: int, pixels: list[tuple[int,int,int,int]]) -> list[list[bool]]:
    ret = []
    for y in range(height):
        ret.append([])
        for x in range(width):
            ret[y].append(pixels[x+y*width][3] > 0)
    return ret

def get_bitmask_1D(width: int, height: int, pixels: list[tuple[int,int,int,int]]) -> list[bool]:
    ret_2d = get_bitmask(width, height, pixels)
    ret = []
    for row in ret_2d:
        ret += row
    return ret

def write_bitmask(vhd_path, pixels: list[list[int]]):
    height = len(pixels)
    width = len(pixels[0])
    dirname, filename = os.path.split(vhd_path)
    filename, ext = os.path.splitext(filename)

    lines = []
    lines.append(f"variable {filename}: std_logic_vector(0 to {width*height-1});\n")

    # generate single line
    single_line = []
    for row in pixels:
        single_line += [str(b) for b in row]
    lines.append(filename + " := \"" + "".join(single_line) + "\"\n")

    # generate multiple lines "pixel art"
    prefix = " " * (len(filename) + 4)
    lines.append(filename + " := \"" + "".join([str(b) for b in pixels[0]]) + "\" &\n")
    for y in range(1, height):
        ampersand = " &" if y < height-1 else ";"
        lines.append(prefix + "\"" + "".join([str(b) for b in pixels[y]]) + f"\"{ampersand}\n")

    with open(vhd_path, "w") as fout:
        fout.writelines(lines)


def write_csv(csv_path: str, pixels: list[list[int]]):
    height = len(pixels)
    width = len(pixels[0])

    with open(csv_path, "w") as fout:
        for y in range(height):
            comma = "," if y < height-1 else ""
            fout.write(", ".join([str(b) for b in pixels[y]]) + comma + "\n")


def write_pixels(image_path: str, pixels: list[list[int]]):
    height = len(pixels)
    width = len(pixels[0])

    image = Image.new("L", (width,height), color=(0))
    for x in range(width):
        for y in range(height):
            if pixels[y][x]:
                image.putpixel((x,y), (255))
    with open(image_path, "wb") as fout:
        image.save(fout, "png")

if __name__ == "__main__":
    pic = "C:/Users/gladc/Documents/School/UNM/ECE_595_intermediate_logic_design/project/media/rocket"
    width, height, pixels = get_pixels(pic+".png")
    bitmask = get_bitmask(width, height, pixels)
    bitmask = [[int(b) for b in row] for row in bitmask]

    write_bitmask(pic+".vhd", bitmask)
    write_csv(pic+".csv", bitmask)
    write_pixels(pic+"_bitmask.png", bitmask)
