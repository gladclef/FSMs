import math
import typing

xy_t = typing.NewType("xy", tuple[int, int])
rd_t = typing.NewType("rd", tuple[float, int])
circle_t = typing.NewType("xyr", tuple[int, int, float])

def rad_to_cart(radians, dist, centerx=None, centery=None) -> xy_t:
    """ Radial vector (from center to North) to cartesian converter. """
    radians += math.pi
    x = int(dist * math.sin(radians))
    y = int(dist * math.cos(radians))
    if centerx is not None:
        x += centerx
        if centery is not None:
            y += centery
        else:
            y += centerx
    return x, y

def cart_to_rad(p1: xy_t, p2: xy_t) -> rd_t:
    """ Cartesian to radial vector (from p1 to North) converter. """
    xdist = (p2[0]-p1[0])
    ydist = (p2[1]-p1[1])
    dist = math.sqrt( xdist**2 + ydist**2 )

    if (ydist == 0):
        if xdist > 0:
            radians = math.pi / 2
        else:
            radians = -math.pi / 2
    elif (xdist == 0):
        if ydist > 0:
            radians = math.pi
        else:
            radians = 0
    else:
        radians = math.asin(xdist / dist)

    return radians, dist

def circle_vector_intersections(circle: circle_t, vector_radians: float, *distances) -> list[xy_t]:
    ret = []
    for d in distances:
        ret.append( rad_to_cart(vector_radians, d, circle[0], circle[1]) )
    return ret

def circle_intersections(big_circle: circle_t, small_circle: circle_t) -> tuple[xy_t, xy_t]:
    """ Calculates the intersecting points for a small circle whose center lies on the perimeter of the big circle. """
    Bx, By, Br = big_circle
    sx, sy, sr = small_circle

    # calculate an intersection for circles where the small circle is immediately above the big circle
    # xi = example intersection
    xi_radians = math.asin((sr / 2) / Br) * 2

    # now add the radians to the position of the small circle to get the intersection points
    s_radians, _ = cart_to_rad([Bx,By], [sx,sy])
    i1_radians = s_radians - xi_radians
    i2_radians = s_radians + xi_radians
    i1 = rad_to_cart(i1_radians, Br, Bx, By)
    i2 = rad_to_cart(i2_radians, Br, Bx, By)

    return i1, i2