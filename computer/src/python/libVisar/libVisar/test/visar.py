import unittest
from libVisar.visar.drawables import Map
from libVisar.visar.drawables import Drawable, Context
from libVisar.visar.globals import Paths

import numpy as np

class TestVisar(unittest.TestCase):
    '''
    Functions:
        ecef2llh((x,y,z)):
        llh2ecef((lat, lon, alt)):
        llh2geoid((lat, lon, alt)):
    '''

    def setUp(self):
        '''Prepare for unit testing'''
        self.fpath = os.path.dirname(os.path.realpath(__file__))

    def test_ecef2latlong(self):
        position = (738575.65, -5498374.10, 3136355.42)

        o_position = Map.ecef2llh(position)
        exp_position = np.array([29.646265015740656, -82.34947101109631, 0.003318880684673786])
        self.assertTrue(np.all(o_position == exp_position))

    def test_file_path(self):
        self.assertEqual(Paths.get_file_path(__file__), self.fpath)

    def test_visar_path(self):
        self.assertEqual(Paths.get_visar_path(), self.fpath)

if __name__ == '__main__':
    unittest.main()
