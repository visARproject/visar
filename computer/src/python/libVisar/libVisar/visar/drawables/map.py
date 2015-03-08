import numpy as np
from ...OpenGL import utils
from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)

from ..drawables import Drawable
from ...OpenGL.utils import Logger


class Map(Drawable):
    ''' Map

    Design:
        - Primary render buffer contains the map image
        - Frequently reload the thing
        - Take in the position from globals
        - Use that position to manipulate the position on the map that is being drawn
        - At any given time we should probably track 4 (more?) buffers for images that need to be stitched

    Questions:
        - How much should we pre-load?
        - How often is too often for texture loading?

    '''
    wgs84_a = 6378137.0
    wgs84_b = 6356752.314245
    wgs84_e2 = 0.0066943799901975848
    wgs84_a2 = wgs84_a**2  # To speed things up a bit
    wgs84_b2 = wgs84_b**2

    def __init__(self):
        '''Map drawable - contains the goddamn map

        Bibliography:

            [1] ecef -> llh, llh -> ecef, llh -> geoid ;
                https://github.com/bistromath/gr-air-modes/blob/master/python/mlat.py
        '''
        pass

    @classmethod
    def ecef2llh(self, (x, y, z)):
        '''Convert ECEF to lat/lon/alt without geoid correction
        Returns alt in meters
        '''

        ep  = np.sqrt((self.wgs84_a2 - self.wgs84_b2) / self.wgs84_b2)
        p   = np.sqrt(x**2 + y**2)
        th  = np.arctan2(self.wgs84_a * z, self.wgs84_b * p)
        lon = np.arctan2(y, x)
        lat = np.arctan2(z + ep**2 * self.wgs84_b * np.sin(th)**3, p - self.wgs84_e2 * self.wgs84_a * np.cos(th)**3)
        N   = self.wgs84_a / np.sqrt(1 - self.wgs84_e2 * np.sin(lat)**2)
        alt = p / np.cos(lat) - N
        
        lon *= (180. / np.pi)
        lat *= (180. / np.pi)
        
        return np.array([lat, lon, alt])

    @classmethod
    def llh2ecef(self, (lat, lon, alt)):
        '''Convert lat/lon/alt coords to ECEF without geoid correction, WGS84 model
        Remember that alt is in meters
        '''

        lat *= (np.pi / 180.0)
        lon *= (np.pi / 180.0)
        
        n = lambda x: self.wgs84_a / np.sqrt(1 - self.wgs84_e2 * (np.sin(x)**2))
        
        x = (n(lat) + alt) * np.cos(lat) * np.cos(lon)
        y = (n(lat) + alt) * np.cos(lat) * np.sin(lon)
        z = (n(lat) * (1 - self.wgs84_e2) + alt) * np.sin(lat)
        
        return np.array([x, y, z])
        
    @classmethod
    def llh2geoid(self, (lat, lon, alt)):
        '''do both of the above to get a geoid-corrected x,y,z position'''
        (x, y, z) = llh2ecef((lat, lon, alt + self.wgs84_height(lat, lon)))
        return np.array([x, y, z])
