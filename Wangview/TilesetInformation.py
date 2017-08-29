
# coding: utf-8
from .Tileset import Tileset

import json
from os import path

class TilesetInformation(object):
    def __init__(self, outputs=[]):
        self.outputs = list(outputs)
    
    def set_rel_path(self, rel_path):
        self.rel_path = rel_path
        
    def set_resolution(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
        for output in self.outputs:
            output.set_resolution(tile_width, tile_height)
            output.initialise()
            
    def load_tilesets(self, filename):
        with open(filename, 'r') as f:
            raw_tileset_data = json.load(f)
        self.init_tilesets(raw_tileset_data)
            
    def init_tilesets(self, raw_tileset_data):
        first_tileset = True
        for tileset in raw_tileset_data:
            self.load_tileset(tileset, first_tileset)
            first_tileset = False
            
    def load_tileset(self, tileset, is_first):
        # All tilesets specify tile resolution
        resolution = tileset['resolution']
        if is_first:
            # Use the first tileset's resolution
            self.set_resolution(*resolution)
            # Start tile unicode blocks in private space
            self.tileset_offset_counter = 0xE000
            # Initialise converted metadata
            self.tilesets = {}
        # Validate tileset's resolution
        assert tuple(resolution) == (self.tile_width, self.tile_height)
        # Calculate the number of tiles the tileset has in each axis
        rx = tileset['x']//self.tile_width
        ry = tileset['y']//self.tile_height
        # Add the tileset's entry to the tileset container
        filename = tileset['filename']
        self.tilesets[filename] = Tileset(
            filename, self.tileset_offset_counter,
            rx,ry, tuple(tileset['terrains']))
        # Load the tileset in the output modules
        for output in self.outputs:
            output.load_tileset(self.tileset_offset_counter,
                                path.join(self.rel_path, filename))
        # Insert the next tileset's tiles at the correct unicode codepoint
        self.tileset_offset_counter += rx*ry
        
    def simplify_tile(self, tile):
        """
        Converts a full specification of a tile's location in a tileset
        into the unicode codepoint where it will have been loaded.
        See also: `init_tilesets()`
        """
        tileset = self.tilesets[tile['filename']]
        return (tileset.offset +
                tileset.width*tile['y']//self.tile_height +
                tile['x']//self.tile_width)
    
