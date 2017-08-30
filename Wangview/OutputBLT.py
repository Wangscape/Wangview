
# coding: utf-8
from bearlibterminal import terminal as blt

class OutputBLT(object):
    def __init__(self):
        pass
    def set_size(self, width, height):
        self.width = width
        self.height = height
    def set_resolution(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
    def initialise(self):
        blt.open()
        blt.composition(True)
        config_string = "window: size={0}x{1}, cellsize={2}x{3}, title='Wangview'".format(
            self.width, self.height, self.tile_width, self.tile_height)
        blt.set(config_string)
    def load_tileset(self, offset, filename):
        config_string = "0x{0:x}: {1}, size={2}x{3}".format(
            offset, filename, self.tile_width, self.tile_height)
        blt.set(config_string)
    def put_ext(self, x,y,dx,dy,c):
        blt.put_ext(x,y,dx,dy,c)
    def refresh(self):
        blt.refresh()
    def clear(self):
        blt.clear()
    def signal(self):
        while blt.has_input():
            kp = blt.read()
            if kp in [blt.TK_CLOSE, blt.TK_ESCAPE]:
                return 'stop'
            if kp == blt.TK_SPACE:
                return 'next'
        return None
    def close(self):
        blt.close()
