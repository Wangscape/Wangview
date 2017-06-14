
# coding: utf-8
from bearlibterminal import terminal as blt
import json
from itertools import product
import random
from os import path
from .Tileset import Tileset
from .Hypergraph import Hypergraph
from .FPSLimiter import FPSLimiter
from .MapGrid import MapGrid

class Display(object):
    """
    Stores Wangscape output metadata in a suitable format,
    stores terrain and tile grids,
    and interfaces with bearlibterminal to draw a scene.
    """
    def __init__(self,
                 rel_path='.',
                 fn_tile_groups='tile_groups.json',
                 fn_terrain_hypergraph='terrain_hypergraph.json',
                 fn_tileset_data='tilesets.json',
                 fps=30):
        # Initialise file path and metadata
        self.rel_path = rel_path
        with open(path.join(rel_path, fn_tileset_data),'r') as f:
            self.init_tilesets(json.load(f))
        with open(path.join(rel_path,fn_tile_groups),'r') as f:
            self.init_tile_groups(json.load(f))
        with open(path.join(rel_path, fn_terrain_hypergraph),'r') as f:
            self.hypergraph = Hypergraph(json.load(f))
        # Initialise geometry info
        self.terminal_width = blt.state(blt.TK_WIDTH)
        self.terminal_height = blt.state(blt.TK_HEIGHT)
        # Tiles may be offset while scrolling,
        # so one extra row and column is required
        self.tile_width = self.terminal_width+1
        self.tile_height = self.terminal_height+1
        # Terrain values are specified in the corners of the graphical tiles,
        # so another extra row and column is required
        self.terrain_width = self.terminal_width+2
        self.terrain_height = self.terminal_height+2
        # Select terrain values
        self.init_terrain_map()
        # Select tile values based on terrain values
        self.init_tile_map()
        # Throttle framerate
        self.fps_limiter = FPSLimiter(fps)
    def simplify_tile(self, tile):
        """
        Converts a full specification of a tile's location in a tileset
        into the unicode codepoint where it will have been loaded.
        See also: `init_tilesets()`
        """
        tileset = self.tilesets[tile['filename']]
        return (tileset.offset +
                tileset.width*tile['y']//self.resolution[1] +
                tile['x']//self.resolution[0])
    def simplify_tile_group(self, tile_group):
        """Converts every tile in a group into a unicode codepoint"""
        return [self.simplify_tile(tile) for tile in tile_group]
    def init_tile_groups(self, raw_groups):
        """
        Converts the data the `tile_groups.json` metadata file
        into a format suitable for Wangview,
        and stores it in self.tile_groups.
        Example input:
        {"g.g.g.g": [{"filename": "g.s.png", "x":0, "y":0},
                     {"filename": "v.g.png", "x":96,"y":96}]}
        output:
        {("g", "g", "g", "g"): [0xe000, 0xe01f]}
        """
        self.tile_groups = {tuple(k.split('.')):self.simplify_tile_group(v)
                            for (k,v) in raw_groups.items()}
    def init_tilesets(self, raw_tileset_data):
        """
        Converts the data in the `tilesets.json` metadata file
        into a format suitable for Wangview,
        stores it in self.tilesets,
        and loads tilesets into bearlibterminal.
        """
        first_tileset = True
        for tileset in raw_tileset_data:
            # All tilesets specify tile resolution
            resolution = tileset['resolution']
            if first_tileset:
                # Use the first tileset's resolution
                self.resolution = resolution
                # Initialise bearlibterminal
                blt.open()
                config_string = "window: size=30x20, cellsize={0}x{1}, title='Wangview'".format(
                    self.resolution[0], self.resolution[1])
                blt.set(config_string)
                # Start tile unicode blocks in private space
                tileset_offset_counter = 0xE000
                # Initialise converted metadata
                self.tilesets = {}
                # Only run this block once
                first_tileset = False
            # Validate remaining tilesets' resolutions
            assert(self.resolution == resolution)
            # Calculate the number of tiles the tileset has in each axis
            rx = tileset['x']//self.resolution[0]
            ry = tileset['y']//self.resolution[1]
            # Add the tileset's entry to the tileset container
            filename = tileset['filename']
            self.tilesets[filename] = Tileset(
                filename, tileset_offset_counter,
                rx,ry, tuple(tileset['terrains']))
            # Load the tileset in bearlibterminal
            config_string = "0x{0:x}: {1}, size={2}x{3}".format(
                    tileset_offset_counter,
                    path.join(self.rel_path, filename),
                    self.resolution[0], self.resolution[1])
            blt.set(config_string)
            # Insert the next tileset's tiles at the correct unicode codepoint
            tileset_offset_counter += rx*ry
    def init_terrain_map(self):
        """
        Calls Hypergraph.generate_lines
        to generate a grid of terrain values,
        and formats the result as a deque of deques.
        Stores the result in self.terrain_map.
        """
        terrain_iter = self.hypergraph.generate_lines(
            self.terrain_width, self.terrain_height)
        self.terrain_map = MapGrid(self.terrain_width, self.terrain_height)
        for line in terrain_iter:
            line_list = list(line)
            self.terrain_map.add_line(line, True, False)
    def init_tile_map(self):
        """
        Generates a grid of unicode codepoints specifying graphical tiles,
        conforming to the current grid of terrain values,
        and formats it as a deque of deques.
        Stores the result in self.tile_map.
        """
        tile_iter = ((self.select_tile(self.get_tile_corners(x,y))
                      for x in range(self.tile_width))
                     for y in range(self.tile_height))
        self.tile_map = MapGrid(self.tile_width, self.tile_height)
        for line in tile_iter:
            self.tile_map.add_line(line, True, False)
    def get_tile_corners(self, x, y):
        """
        Returns a generator which iterates over the terrain values in positions
        [(x,y), (x,y+1), (x+1, y), (x+1, y+1)]
        """
        return (self.terrain_map[x,y]
                for (x,y) in
                product((x,x+1),(y,y+1)))
    def select_tile(self, corners):
        """Selects a random tile that has the specified terrain values in its corners"""
        return random.choice(self.tile_groups[tuple(corners)])
    def draw_iter(self):
        """Yields cell coordinates, offset, and character for each tile to be drawn"""
        for y, line in enumerate(self.tile_map):
            # Corner Wang tiles are offset by a quarter of a tile in each dimension.
            # Odd resolutions have the pixel at (0,0) moved by (x//2, y//2) in output tiles,
            # So this reverse translation is correct.
            dy = -(self.resolution[1]//2)
            if y == self.tile_height-1:
                # The terminal ignores characters put outside its range,
                # so one row must be drawn using composition
                y -= 1
                dy += self.resolution[1]
            for x, c in enumerate(line):
                dx = -(self.resolution[0]//2)
                if x == self.tile_width-1:
                    # One column must also be drawn using composition
                    x -= 1
                    dx += self.resolution[0]
                yield (x,y,dx,dy,c)
    def draw(self):
        """
        Draws every tile to the terminal.
        See also: `draw_iter.`
        """
        for draw_args in self.draw_iter():
            blt.put_ext(*draw_args)
    def run(self):
        """
        Draws the scene to the terminal and refreshes repeatedly.
        Quits on pressing Esc or closing the window.
        Creates a new scene on pressing Space.
        """
        stop = False
        blt.composition(True)
        while not stop:
            self.fps_limiter.wait()
            blt.clear()
            self.draw()
            blt.refresh()
            while blt.has_input():
                kp = blt.read()
                if kp == blt.TK_CLOSE:
                    stop = True
                elif kp == blt.TK_ESCAPE:
                    stop = True
                elif kp == blt.TK_SPACE:
                    self.init_terrain_map()
                    self.init_tile_map()
        blt.close()
