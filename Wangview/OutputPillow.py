
# coding: utf-8
import PIL
from PIL import ImageFile
from PIL import Image

class OutputPillow(object):
    def __init__(self, filename):
        self._tiles = {}
        self.filename = filename
    def set_size(self, width, height):
        self.width = width
        self.height = height
    def set_resolution(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
    def initialise(self):
        self.clear()
    def load_tileset(self, offset, filename):
        tileset = Image.open(filename)
        tileset_width = tileset.width//self.tile_width
        tileset_height = tileset.height//self.tile_height
        for y in range(tileset_height):
            for x in range(tileset_width):
                square =  (x*self.tile_width, y*self.tile_height,
                           (x+1)*self.tile_width, (y+1)*self.tile_height)
                tile_offset = offset + y*tileset_width + x
                self._tiles[tile_offset] = tileset.crop(square)
    def put_ext(self, x,y,dx,dy,c):
        self.image.paste(self._tiles[c], (x*self.tile_width + dx, y*self.tile_height + dy))
    def refresh(self):
        self.image.save(self.filename)
    def clear(self):
        self.image = Image.new('RGBA', (self.width*self.tile_width,
                                        self.height*self.tile_height))
    def signal(self):
        return 'stop'
    def close(self):
        pass
