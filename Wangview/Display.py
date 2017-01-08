
# coding: utf-8

# In[ ]:

from bearlibterminal import terminal as blt
import json
from collections import deque
from itertools import product
import random
from os import path
from .Tileset import Tileset
from .Hypergraph import Hypergraph


# In[ ]:

class Display(object):
    def __init__(self,
                 rel_path='.',
                 fn_tile_groups='tile_groups.json',
                 fn_terrain_hypergraph='terrain_hypergraph.json',
                 fn_tileset_data='tilesets.json'):
        self.rel_path = rel_path
        with open(path.join(rel_path, fn_tileset_data),'r') as f:
            self.init_tilesets(json.load(f))
        with open(path.join(rel_path,fn_tile_groups),'r') as f:
            self.init_tile_groups(json.load(f))
        with open(path.join(rel_path, fn_terrain_hypergraph),'r') as f:
            self.hypergraph = Hypergraph(json.load(f))
        self.terminal_width = blt.state(blt.TK_WIDTH)
        self.terminal_height = blt.state(blt.TK_HEIGHT)
        self.terrain_width = self.terminal_width+2
        self.terrain_height = self.terminal_height+2
        self.tile_width = self.terminal_width+1
        self.tile_height = self.terminal_height+1
        self.init_terrain_map()
        self.init_tile_map()
    def simplify_tile(self, tile):
        tileset = self.tilesets[tile['filename']]
        return (tileset.offset +
                tileset.width*tile['y']//self.resolution +
                tile['x']//self.resolution)
    def simplify_tile_group(self, tile_group):
        return [self.simplify_tile(tile) for tile in tile_group]
    def init_tile_groups(self, raw_groups):
        self.tile_groups = {tuple(k.split('.')):self.simplify_tile_group(v)
                            for (k,v) in raw_groups.items()}
    def init_tilesets(self, raw_tileset_data):
        first_tileset = True
        for tileset in raw_tileset_data:
            resolution = tileset['resolution']
            if first_tileset:
                self.resolution = resolution
                blt.open()
                config_string = "window: size=30x20, cellsize={0}x{0}, title='Wangview'".format(
                    self.resolution)
                blt.set(config_string)
                tileset_offset_counter = 0xE000
                self.tilesets = {}
                first_tileset = False
            assert(self.resolution == resolution)
            rx = tileset['x']//self.resolution
            ry = tileset['y']//self.resolution
            filename = tileset['filename']
            self.tilesets[filename] = Tileset(
                filename, tileset_offset_counter,
                rx,ry, tuple(tileset['terrains']))
            config_string = "0x{0:x}: {1}, size={2}x{2}".format(
                    tileset_offset_counter,
                    path.join(self.rel_path, filename),
                    self.resolution)
            blt.set(config_string)
            tileset_offset_counter += rx*ry
    def init_terrain_map(self):
        terrain_iter = self.hypergraph.generate_lines(
            self.terrain_width, self.terrain_height)
        terrain_deque_iter = (deque(line, self.terrain_width)
                              for line in terrain_iter)
        self.terrain_map = deque(terrain_deque_iter, self.terrain_height)
    def init_tile_map(self):
        tile_iter = ((self.select_tile(self.get_tile_corners(x,y))
                      for x in range(self.tile_width))
                     for y in range(self.tile_height))
        tile_deque_iter = (deque(line, self.tile_width) for line in tile_iter)
        self.tile_map = deque(tile_deque_iter, self.tile_height)
    def get_tile_corners(self, x, y):
        return (self.terrain_map[y][x]
                for (x,y) in
                product((x,x+1),(y,y+1)))
    def select_tile(self, corners):
        return random.choice(self.tile_groups[tuple(corners)])
    def draw_iter(self):
        for y, line in enumerate(self.tile_map):
            dy =-self.resolution//2
            if y == self.tile_height-1:
                y -= 1
                dy += self.resolution
            for x, c in enumerate(line):
                dx = -self.resolution//2
                if x == self.tile_width-1:
                    x -= 1
                    dx += self.resolution
                yield (x,y,dx,dy,c)
    def draw(self):
        for draw_args in self.draw_iter():
            blt.put_ext(*draw_args)
    def run(self):
        stop = False
        blt.composition(True)
        while not stop:
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

