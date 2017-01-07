
# coding: utf-8

# In[ ]:

from functools import reduce
import random


# In[ ]:

class Hypergraph(object):
    def __init__(self, raw_hypergraph):
        self.data = {k: frozenset(map(frozenset,v))
                     for (k,v) in raw_hypergraph.items()}
    @staticmethod
    def flatten_options(options):
        return reduce(lambda x,y: x.union(y),
                      options,
                      frozenset())
    def terrain_options(self, *terrains):
        if len(terrains) == 0:
            return list(self.data.keys())
        return self.flatten_options(reduce(
                lambda options, terrain: [clique for clique in options if terrain in clique],
                terrains[1:], list(self.data[terrains[0]])))
    def terrain_options_2(self, t_left=[], t_up=[]):
        if len(t_up) == 0:
            return self.terrain_options(*t_left)
        x = self.terrain_options(*(t_left+t_up[:2]))
        if len(t_up) == 3:
            y = self.terrain_options(*t_up[1:])
            return x.intersection(y)
        return x
    def generate_line(self, width, previous_line=None):
        new_line = []
        t_left = []
        t_up = []
        for i in range(width):
            if previous_line is not None:
                t_up = previous_line[max(0,i-1):i+2]
            options = self.terrain_options_2(t_left, t_up)
            new_line.append(random.choice(list(options)))
            t_left = [new_line[-1]]
        return new_line
    def generate_lines(self, width, height):
        line = self.generate_line(width)
        yield line
        for i in range(height):
            line = self.generate_line(width, line)
            yield line

