import numpy as np
from ...OpenGL import utils
from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate, scale, xrotate, yrotate, zrotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)

from ...osmviz import PILImageManager, OSMManager
import PIL.Image as Image

from ...OpenGL.drawing import Drawable
from ...OpenGL.utils import Logger
from ..globals import State


class Map(Drawable):
    ''' Map

    Glossary:
        - Internal Cache: Load an image into this program
        - Cache: Download OSM data and store it as an image on the HDD
        - OSM: OpenStreetMap (See [1])
        - ECEF: "Earth-centered, earth-fixed", coordinate system originating at the center of the earth
            - The magnitude of this vector should be something close to Earth's radius
        - LLA (or llh): Latitude, Longitude, Altitude (Or height); The position format accepted by OSM
        - Quaternion: A method of tracking orientation that is not subject to gimbal lock

    Design:
        - Primary render buffer contains the map image
        - Frequently reload the thing
        - Take in the position from globals
        - Use that position to manipulate the position on the map that is being drawn
        - At any given time we should probably track 4 (more?) buffers for images that need to be stitched

        - Internally cache a region about twice the size of the region that the user is in
            - Traverse that region until the user's view is close to the edge
            - When the view approaches the edge, generate a new map image centered at the current position
            - Transparently replace the map at a render-buffer swap

        - Zoom in the shaders and OSM zoom must be tied together
            -- Shader zoom has no concept of real scale
    Questions:
        - How much should we pre-load?
        - How often is too often for texture loading?

    FAQ:
        - Why aren't the view and projection matrices constant, these are UI elements, right!?
            -- THAT'S AN IMPORTANT QUESTION: THE RIFT DISTORTION REQUIRES THE ABILITY TO CHANGE PROJECTION AND POSITION

    Bibliography:
        [1] http://www.openstreetmap.org/#map=5/51.500/-0.100
        [2] ecef -> llh; llh -> ecef; llh -> geoid;
                Link: https://github.com/bistromath/gr-air-modes/blob/master/python/mlat.py

    '''

    # World Geodetic System Constants
    wgs84_a = 6378137.0
    wgs84_b = 6356752.314245
    wgs84_e2 = 0.0066943799901975848
    wgs84_a2 = wgs84_a**2
    wgs84_b2 = wgs84_b**2

    frame_vertex_shader = """
        #version 120
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        uniform vec2 map_center; // Latitude, Longitude
        uniform vec4 corners; // min_lat, min_long, max_lat, max_long

        uniform mat4 map_transform;

        uniform float zoom;
        uniform vec2 user_position; // Latitude, Longitude
        uniform float user_orientation; // Yaw, radians

        attribute vec3 vertex_position;
        attribute vec2 default_texcoord;

        varying vec2 texcoord;

        vec2 scale_between(vec2 value, vec2 minimum, vec2 maximum) {

            vec2 scaled = (value - minimum) / (maximum - minimum); // Division is element-wise
            return scaled; // now in [0, 1]
        }

        vec2 deform_tex_coords() { 
            // Uses globals
            vec2 bottom_left = corners.xy; // Of map (in lat,long)
            vec2 top_right = corners.zw; // Of map (in lat,long)

            vec2 world_offset = user_position - map_center;
            vec2 true_tex_coords = scale_between(world_offset, bottom_left, top_right) + default_texcoord;

            return true_tex_coords;
        }

        void main()
        {
            vec2 bottom_left = corners.xy; // Of map (in lat,long)
            vec2 top_right = corners.zw; // Of map (in lat,long)

            // Transform the texture coordinates
            // 1. -0.5, * 2 is for transforming to centered coordinates
            vec4 transformed_tex_coords = ((map_transform * vec4(2 * (default_texcoord.xy - 0.5), 0, 1)));
            texcoord = vec2((transformed_tex_coords.xy / 2) + 0.5) / transformed_tex_coords.w;
            mat4 T = projection * view * model;
            gl_Position = T * vec4(vertex_position, 1.0);
        }
    """
    
    frame_frag_shader = """
        #version 120
        uniform vec2 map_center; // Latitude, Longitude
        uniform vec4 corners; // min_lat, min_long, max_lat, max_long

        uniform vec2 user_position; // Latitude, Longitude
        uniform float user_orientation; // Yaw, radians

        uniform sampler2D map_texture;
        varying vec2 texcoord;
        void main()
        {
            vec4 color = texture2D(map_texture, texcoord);
            gl_FragColor = vec4(color.rgb, 1);
        }
    """

    map_vertex_shader = """
        #version 120
    """

    map_frag_shader = """
        #version 120
    """

    name = "Map"
    def __init__(self):
        '''Map drawable - contains the goddamn map
        '''
        self.projection = np.eye(4)
        self.view = np.eye(4)

        self.model = scale(np.eye(4), 0.4)
        orientation_vector = (1, 1, 0)
        unit_orientation_angle = np.array(orientation_vector) / np.linalg.norm(orientation_vector)
        rotate(self.model, -30, *unit_orientation_angle)
        translate(self.model, -0.2, -2.4, -5)
        
        height, width = 5.0, 5.0  # Meters

        # Add texture coordinates
        # Rectangle of height height
        self.vertices = np.array([
            [-width / 2, -height / 2, 0],
            [ width / 2, -height / 2, 0],
            [ width / 2,  height / 2, 0],
            [-width / 2,  height / 2, 0],
        ], dtype=np.float32)

        self.tex_coords = np.array([
            [0, 1],
            [1, 1],
            [1, 0],
            [0, 0],
        ], dtype=np.float32)

        self.indices = IndexBuffer([
            0, 1, 2,
            2, 3, 0,
        ])

        ###### TESTING
        lla = self.ecef2llh((738575.65, -5498374.10, 3136355.42))
        ###### TESTING

        self.map, self.ranges = self.get_map(lla[:2])
        self.program = Program(self.frame_vertex_shader, self.frame_frag_shader)

        default_map_transform = np.eye(4)

        self.program['vertex_position'] = self.vertices
        self.program['default_texcoord'] = self.tex_coords
        self.program['zoom'] = 1
        self.program['view'] = self.view
        self.program['model'] = self.model
        self.program['projection'] = self.projection

        self.program['map_transform'] = default_map_transform
        self.program['map_center'] = lla[:2]
        self.program['map_texture'] = self.map
        self.program['corners'] = self.ranges
        self.program['user_position'] = lla[:2]

    def update(self):
        yaw = State.yaw
        counter_yaw = 360 - np.degrees(yaw)
        # Could use optimization by subtracting current yaw from previous yaw
        map_transform = np.eye(4)
        map_transform = zrotate(map_transform, 0)
        scale(map_transform, 0.8)
        
        self.program['map_transform'] = map_transform

        # Convert Forrest's ecef position to lla
        position_lla = self.ecef2llh(State.position_ecef)[:2]
        self.program['user_position'] = position_lla

    def draw(self):        
        # Disable depth test - UI element
        set_state(depth_test=False)
        self.program.draw('triangles', self.indices)
        set_state(depth_test=True)

    @classmethod
    def get_map(self, (latitude, longitude), zoom=9, region_size=1):
        '''Map.get_map((latitude, longitude), zoom=9, region_size=1): -> image, lat_range, long_range

        latitude and longitude define the center position of the user
        zoom: Lower -> closer to ground
        region_size: size in degrees of region 

        Snippet for region size determination:
        >>> half_size = region_size / 2
        >>> region = (
        ...     latitude - half_size, 
        ...     latitude + half_size,
        ...     longitude - half_size,
        ...     longitude + half_size,
        ... )

        '''
        imgr = PILImageManager('RGB')
        osm = OSMManager(image_manager=imgr)

        half_size = region_size / 2.0
        region = (
            latitude - half_size, 
            latitude + half_size,
            longitude - half_size,
            longitude + half_size,
        )

        image, bounds = osm.createOSMImage(region, zoom)

        # wh_ratio = float(image.size[0]) / image.size[1]
        # image2 = image.resize( (int(800 * wh_ratio), 800), Image.ANTIALIAS )
        map_image = np.asarray(image)

        # Book-keeping
        min_lat, max_lat, min_long, max_long = bounds
        # lat_range = (min_lat, max_lat)
        # long_range = (min_long, max_long)
        # corner_left = np.array((min_lat, min_long))
        # corner_right = np.array((max_lat, max_long))

        # The second return is the 'corners' used in the map shaders
        return map_image, np.array((min_lat, min_long, max_lat, max_long))

    @classmethod
    def ecef2llh(self, (x, y, z)):
        '''Convert ECEF to lat/lon/alt without geoid correction
        Returns alt in meters
        '''

        ep = np.sqrt((self.wgs84_a2 - self.wgs84_b2) / self.wgs84_b2)
        p = np.sqrt(x**2 + y**2)
        th = np.arctan2(self.wgs84_a * z, self.wgs84_b * p)
        lon = np.arctan2(y, x)
        lat = np.arctan2(z + ep**2 * self.wgs84_b * np.sin(th)**3, p - self.wgs84_e2 * self.wgs84_a * np.cos(th)**3)
        N = self.wgs84_a / np.sqrt(1 - self.wgs84_e2 * np.sin(lat)**2)
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
