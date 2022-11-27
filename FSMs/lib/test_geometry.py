import math
from unittest import TestCase

from lib.geometry import cart_to_rad, rad_to_cart, Pxy


class Test(TestCase):
    def test_cart_to_rad(self):
        # 0, 90, 180, and 270 degrees
        self.assertAlmostEqual(0,               cart_to_rad(Pxy(0, 0), Pxy(0, -1)).radians, delta=math.pi / 180)
        self.assertAlmostEqual(math.pi / 2,     cart_to_rad(Pxy(0, 0), Pxy(1, 0)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(math.pi,         cart_to_rad(Pxy(0, 0), Pxy(0, 1)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(3 * math.pi / 2, cart_to_rad(Pxy(0, 0), Pxy(-1, 0)).radians, delta=math.pi / 180)

        # 45, 135, 225, 315 degrees
        self.assertAlmostEqual(math.pi / 4,     cart_to_rad(Pxy(0, 0), Pxy(1, -1)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(3 * math.pi / 4, cart_to_rad(Pxy(0, 0), Pxy(1, 1)).radians,   delta=math.pi / 180)
        self.assertAlmostEqual(5 * math.pi / 4, cart_to_rad(Pxy(0, 0), Pxy(-1, 1)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(7 * math.pi / 4, cart_to_rad(Pxy(0, 0), Pxy(-1, -1)).radians, delta=math.pi / 180)

        # 30, 120, 210, 300 degrees
        self.assertAlmostEqual(math.pi / 6,      cart_to_rad(Pxy(0, 0), Pxy(1, -1.732)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(4 * math.pi / 6,  cart_to_rad(Pxy(0, 0), Pxy(1.732, 1)).radians,   delta=math.pi / 180)
        self.assertAlmostEqual(7 * math.pi / 6,  cart_to_rad(Pxy(0, 0), Pxy(-1, 1.732)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(10 * math.pi / 6, cart_to_rad(Pxy(0, 0), Pxy(-1.732, -1)).radians, delta=math.pi / 180)

        # 60, 150, 240, 330 degrees
        self.assertAlmostEqual(2 * math.pi / 6,  cart_to_rad(Pxy(0, 0), Pxy(1.732, -1)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(5 * math.pi / 6,  cart_to_rad(Pxy(0, 0), Pxy(1, 1.732)).radians,   delta=math.pi / 180)
        self.assertAlmostEqual(8 * math.pi / 6,  cart_to_rad(Pxy(0, 0), Pxy(-1.732, 1)).radians,  delta=math.pi / 180)
        self.assertAlmostEqual(11 * math.pi / 6, cart_to_rad(Pxy(0, 0), Pxy(-1, -1.732)).radians, delta=math.pi / 180)

    def test_rad_to_cart(self):
        # 0, 90, 180, and 270 degrees
        self.assertAlmostEqual(0,  rad_to_cart(0, 1).x, delta=0.01)
        self.assertAlmostEqual(-1, rad_to_cart(0, 1).y, delta=0.01)
        self.assertAlmostEqual(1,  rad_to_cart(math.pi/2, 1).x, delta=0.01)
        self.assertAlmostEqual(0,  rad_to_cart(math.pi/2, 1).y, delta=0.01)
        self.assertAlmostEqual(0,  rad_to_cart(math.pi, 1).x, delta=0.01)
        self.assertAlmostEqual(1,  rad_to_cart(math.pi, 1).y, delta=0.01)
        self.assertAlmostEqual(-1, rad_to_cart(math.pi*3/2, 1).x, delta=0.01)
        self.assertAlmostEqual(0,  rad_to_cart(math.pi*3/2, 1).y, delta=0.01)

        # 45, 135, 225, 315 degrees
        self.assertAlmostEqual(1,  rad_to_cart(math.pi/4, 1.414).x, delta=0.01)
        self.assertAlmostEqual(-1, rad_to_cart(math.pi/4, 1.414).y, delta=0.01)
        self.assertAlmostEqual(1,  rad_to_cart(math.pi*3/4, 1.414).x, delta=0.01)
        self.assertAlmostEqual(1,  rad_to_cart(math.pi*3/4, 1.414).y, delta=0.01)
        self.assertAlmostEqual(-1, rad_to_cart(math.pi*5/4, 1.414).x, delta=0.01)
        self.assertAlmostEqual(1,  rad_to_cart(math.pi*5/4, 1.414).y, delta=0.01)
        self.assertAlmostEqual(-1, rad_to_cart(math.pi*7/4, 1.414).x, delta=0.01)
        self.assertAlmostEqual(-1, rad_to_cart(math.pi*7/4, 1.414).y, delta=0.01)

        # 30, 120, 210, 300 degrees
        self.assertAlmostEqual(1,      rad_to_cart(math.pi/6, 2).x, delta=0.01)
        self.assertAlmostEqual(-1.732, rad_to_cart(math.pi/6, 2).y, delta=0.01)
        self.assertAlmostEqual(1.732,  rad_to_cart(math.pi*4/6, 2).x, delta=0.01)
        self.assertAlmostEqual(1,      rad_to_cart(math.pi*4/6, 2).y, delta=0.01)
        self.assertAlmostEqual(-1,     rad_to_cart(math.pi*7/6, 2).x, delta=0.01)
        self.assertAlmostEqual(1.732,  rad_to_cart(math.pi*7/6, 2).y, delta=0.01)
        self.assertAlmostEqual(-1.732, rad_to_cart(math.pi*10/6, 2).x, delta=0.01)
        self.assertAlmostEqual(-1,     rad_to_cart(math.pi*10/6, 2).y, delta=0.01)