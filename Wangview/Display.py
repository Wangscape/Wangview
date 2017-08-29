
# coding: utf-8
from bearlibterminal import terminal as blt
import json
from itertools import product
from os import path
from .Hypergraph import Hypergraph
from .FPSLimiter import FPSLimiter
from .MapGrid import MapGrid
from .TilesetInformation import TilesetInformation
from .TileGroups import TileGroups

class Display(object):
    """
    Stores Wangscape output metadata in a suitable format,
    stores terrain and tile grids,
    and interfaces with bearlibterminal to draw a scene,
    or with pillow to write one to file.
    """
    def __init__(self,
                 rel_path='.',
                 fn_tile_groups='tile_groups.json',
                 fn_terrain_hypergraph='terrain_hypergraph.json',
                 fn_tileset_data='tilesets.json',
                 fps=30,
                 map_mode=[30,20],
                 output_mode=[]):
        # Initialise base path
        self.rel_path = rel_path
        # Read map size or fixed map and prepare storage
        self.init_map(map_mode)
        self.init_output(output_mode)
        self.init_tilesets(path.join(rel_path, fn_tileset_data))
        self.tile_groups = TileGroups.from_file(self.tilesets,
                                                path.join(rel_path, fn_tile_groups))
        self.hypergraph = Hypergraph.from_file(path.join(rel_path, fn_terrain_hypergraph))
        self.update_map()
        # Throttle framerate
        self.fps_limiter = FPSLimiter(fps)

    def init_map(self, map_mode):
        if type(map_mode) is str:
            # Initialise fixed map and use its size
            self.use_fixed_map = True
            fn_fixed_map = map_mode
            self.init_fixed_map(fn_fixed_map)
        else:
            # Use random maps of the given size
            self.use_fixed_map = False
            size = tuple(map_mode)
            self.init_sizes(size)
        self.terrain_map = MapGrid(self.terrain_map_width, self.terrain_map_height)
        self.tile_map = MapGrid(self.tile_map_width, self.tile_map_height)
            
    def init_fixed_map(self, fn_fixed_map):
        with open(path.join(self.rel_path, fn_fixed_map),'r') as f:
            fixed_map_data = json.load(f)
        self.fixed_map = fixed_map_data["map"]
        self.init_sizes(fixed_map_data["size"])
        
    def init_sizes(self, size):
        # The size of the scene in tiles
        self.display_width = size[0]
        self.display_height = size[1]
        # Tiles are not aligned with display boundaries,
        # so one extra row and column is required
        self.tile_map_width = self.display_width + 1
        self.tile_map_height = self.display_height + 1
        # Terrain values are specified in the corners of the graphical tiles,
        # so another extra row and column is required
        self.terrain_map_width = self.tile_map_width + 1
        self.terrain_map_height = self.tile_map_height + 1
        
    def add_blt_output(self):
        from .OutputBLT import OutputBLT
        self.outputs.append(OutputBLT())
        self.use_blt = True
        
    def add_pillow_output(self, filename):
        from .OutputPillow import OutputPillow
        self.outputs.append(OutputPillow(filename))
        self.use_pillow = True
        
    def init_output(self, output_mode):
        self.outputs = []
        for item in output_mode:
            if item is True:
                self.add_blt_output()
            else:
                self.add_pillow_output(item)
        if self.outputs == []:
            self.add_blt_output()
        for output in self.outputs:
            output.set_size(self.display_width, self.display_height)
            
    def init_tilesets(self, filename):
        """
        Converts the data in the `tilesets.json` metadata file
        into a format suitable for Wangview,
        stores it in self.tilesets,
        and loads tilesets into bearlibterminal.
        """
        self.tilesets = TilesetInformation(self.outputs)
        self.tilesets.set_rel_path(self.rel_path)
        self.tilesets.load_tilesets(filename)
        
    def update_map(self):
        if self.use_fixed_map:
            self.terrain_map.empty()
            for line in self.fixed_map:
                self.terrain_map.add_line(line, True, False)
        else:
            self.generate_terrain_map()
        self.generate_tile_map()
    def generate_terrain_map(self):
        self.terrain_map.empty()
        for line in self.hypergraph.generate_lines(self.terrain_map_width,
                                                   self.terrain_map_height):
            self.terrain_map.add_line(line, True, False)
    
    def generate_tile_map(self):
        tile_iter = ((self.tile_groups.select_tile(self.get_tile_corners(x,y))
                      for x in range(self.tile_map_width))
                     for y in range(self.tile_map_height))
        self.tile_map.empty()
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
    
    def draw_iter(self):
        """Yields cell coordinates, offset, and character for each tile to be drawn"""
        for y, line in enumerate(self.tile_map):
            # Corner Wang tiles are offset by a quarter of a tile in each dimension.
            # Odd resolutions have the pixel at (0,0) moved by (x//2, y//2) in output tiles,
            # So this reverse translation is correct.
            dy = -(self.tilesets.tile_height//2)
            if y == self.tile_map_height-1:
                # The terminal ignores characters put outside its range,
                # so one row must be drawn using composition
                y -= 1
                dy += self.tilesets.tile_height
            for x, c in enumerate(line):
                dx = -(self.tilesets.tile_width//2)
                if x == self.tile_map_width-1:
                    # One column must also be drawn using composition
                    x -= 1
                    dx += self.tilesets.tile_width
                yield (x,y,dx,dy,c)
    
    def draw(self):
        """
        Draws every tile to the outputs.
        See also: `draw_iter.`
        """
        for output in self.outputs:
            output.clear()
        for draw_args in self.draw_iter():
            for output in self.outputs:
                output.put_ext(*draw_args)
        for output in self.outputs:
            output.refresh()
    def run(self):
        """
        Draws the scene to the terminal and refreshes repeatedly.
        Quits on pressing Esc or closing the window.
        Creates a new scene on pressing Space.
        """
        while True:
            self.fps_limiter.wait()
            self.draw()
            signals = [output.signal() for output in self.outputs]
            if all(signal == 'stop' for signal in signals):
                break
            if 'next' in signals:
                self.update_map()
        for output in self.outputs:
            output.close()

class NotDisplay(object):
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
                 fps=30,
                 map_mode=[30,20],
                 output_mode=[]):
        # Initialise base path
        self.rel_path = rel_path
        # Initialise fixed map and use its size, if it exists
        if type(map_mode) is str:
            fn_fixed_map = map_mode
            self.init_fixed_map(fn_fixed_map)
        else:
            size = tuple(map_mode)
            self.init_sizes(size)
        with open(path.join(rel_path, fn_tileset_data),'r') as f:
            self.init_tilesets(json.load(f))
        with open(path.join(rel_path,fn_tile_groups),'r') as f:
            self.init_tile_groups(json.load(f))
        with open(path.join(rel_path, fn_terrain_hypergraph),'r') as f:
            self.hypergraph = Hypergraph(json.load(f))
        # Select terrain values
        self.init_terrain_map()
        # Select tile values based on terrain values
        self.init_tile_map()
        # Throttle framerate
        self.fps_limiter = FPSLimiter(fps)
    def init_sizes(self, size):
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
                config_string = "window: size={0}x{1}, cellsize={2}x{3}, title='Wangview'".format(
                    self.size[0], self.size[1], self.resolution[0], self.resolution[1])
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
    def init_fixed_map(self, fn_fixed_map):
        with open(path.join(rel_path, fn_fixed_map),'r') as f:
            fixed_map_data = json.load(f)
        self.fixed_map = fixed_map["map"]
        self.size = tuple(fixed_map["size"])
    def init_terrain_map(self):
        """
        Calls Hypergraph.generate_lines
        to generate a grid of terrain values,
        and formats the result as a deque of deques.
        Stores the result in self.terrain_map.
        If fixed_map is defined, a fixed map is used instead.
        """
        self.terrain_map = MapGrid(self.terrain_width, self.terrain_height)
        if self.fixed_map is not None:
            assert len(self.fixed_map) == self.terrain_height
            for line in self.fixed_map:
                assert len(line) == self.terrain_width
                self.terrain_map.add_line(line, True, False)
        else:
            terrain_iter = self.hypergraph.generate_lines(
                self.terrain_width, self.terrain_height)
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
