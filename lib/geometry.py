from __future__ import annotations

import math
import typing
from typing import Any

circle_t = typing.NewType("xyr", tuple[float, float, float])

class Pxy():
    def __init__(self, x : float | Any, y : float | None = None):
        if isinstance(x, Pxy):
            other = x
            self.x = other.x
            self.y = other.y
        else:
            self.x = x
            self.y = y

    def xdist(self, other):
        return other.x - self.x

    def ydist(self, other):
        return other.y - self.y

    def dist(self, other):
        return math.sqrt( (self.x-other.x)**2 + (self.y-other.y)**2 )

    def to_rad(self) -> Rad:
        return cart_to_rad(Pxy(0,0), self)

class Rad():
    def __init__(self, radians : float | Any, dist : float | None = None):
        if isinstance(radians, Rad):
            other = radians
            self.radians = other.radians
            self.dist = other.dist
        else:
            self.radians = radians
            self.dist = dist

    def to_cart(self) -> Pxy:
        return rad_to_cart(self.radians, self.dist)

def rad_to_cart(radians: Rad | float, dist: float | None=None, centerx: float | None=None, centery: float | None=None) -> Pxy:
    """ Radial vector (from center to North) to cartesian converter. """
    rad = radians
    if dist is not None:
        rad = Rad(radians, dist)
    x = rad.dist * math.sin(rad.radians)
    y = -rad.dist * math.cos(rad.radians)

    if centerx is not None:
        x += centerx
        if centery is not None:
            y += centery
        else:
            y += centerx

    return Pxy(x, y)

def cart_to_rad(p1: Pxy, p2: Pxy) -> Rad:
    """ Cartesian to radial vector converter.

    Radians increase clockwise
    X increases right, Y increases down
    """
    p1 = Pxy(p1)
    p2 = Pxy(p2)
    xdist = p1.xdist(p2)
    ydist = p1.ydist(p2)
    dist = p1.dist(p2)

    if (ydist == 0):
        if xdist > 0:
            radians = math.pi/2
        else:
            radians = math.pi*3/2
    elif (xdist == 0):
        if ydist > 0:
            radians = math.pi
        else:
            radians = 0
    else:
        radians = math.asin(ydist / dist) # -pi/2 to pi/2

        if xdist > 0:
            if ydist <= 0: # quadrant 1
                radians += math.pi/2
            else: # quadrant 2
                radians += math.pi/2
        else:
            if ydist > 0: # quadrant 3
                radians = math.pi*3/2 - radians
            else: # quadrant 4
                radians = math.pi*3/2 + abs(radians)

    return Rad(radians, dist)

def circle_vector_intersections(circle: circle_t, vector_radians: float, *distances) -> list[Pxy]:
    ret = []
    for d in distances:
        ret.append( rad_to_cart(vector_radians, d, circle[0], circle[1]) )
    return ret

def circle_intersections(big_circle: circle_t, small_circle: circle_t) -> tuple[Pxy, Pxy]:
    """ Calculates the intersecting points for a small circle whose center lies on the perimeter of the big circle. """
    Bx, By, Br = big_circle
    sx, sy, sr = small_circle

    # calculate an intersection for circles where the small circle is immediately above the big circle
    # xi = example intersection
    xi_radians = abs( math.asin((sr / 2) / Br) * 2 )

    # now add the radians to the position of the small circle to get the intersection points
    s_rad = cart_to_rad(Pxy(Bx,By), Pxy(sx,sy))
    i1_rad = Rad(s_rad.radians - xi_radians, Br)
    i2_rad = Rad(s_rad.radians + xi_radians, Br)
    i1 = rad_to_cart(i1_rad, centerx=Bx, centery=By)
    i2 = rad_to_cart(i2_rad, centerx=Bx, centery=By)

    return i1, i2
