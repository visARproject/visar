import unittest
from libVisar.visar.drawables import Map
from libVisar.visar.drawables import Drawable, Context
import numpy as np

class TestVisar(unittest.TestCase):
    '''
    Functions:
        ecef2llh((x,y,z)):
        llh2ecef((lat, lon, alt)):
        llh2geoid((lat, lon, alt)):
    '''

    def setUp(self):
        '''No need for additional setup'''
        pass

    def test_ecef2latlong(self):
        position = (738575.65, -5498374.10, 3136355.42)

        o_position = Map.ecef2llh(position)
        exp_position = np.array([29.646265015740656, -82.34947101109631, 0.003318880684673786])
        self.assertTrue(np.all(o_position == exp_position))


if __name__ == '__main__':
    unittest.main()
