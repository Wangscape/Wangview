
# coding: utf-8
import json
import random

class TileGroups(object):
    def __init__(self, tilesets):
        self.tilesets = tilesets
        self.tile_groups = {}
    
    @classmethod
    def from_data(cls, tilesets, raw_groups):
        tg = cls(tilesets)
        tg.init_tile_groups(raw_groups)
        return tg
    
    @classmethod
    def from_file(cls, tilesets, filename):
        tg = cls(tilesets)
        tg.load(filename)
        return tg
        
    def load(self, filename):
        with open(filename, 'r') as f:
            raw_tile_groups = json.load(f)
        self.init_tile_groups(raw_tile_groups)
    
    def simplify_tile_group(self, tile_group):
        """Converts every tile in a group into a unicode codepoint"""
        return [self.tilesets.simplify_tile(tile) for tile in tile_group]
    
    def init_tile_groups(self, raw_tile_groups):
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
                            for (k,v) in raw_tile_groups.items()}
        
    def select_tile(self, corners):
        """Selects a random tile that has the specified terrain values in its corners"""
        return random.choice(self.tile_groups[tuple(corners)])
