
# coding: utf-8

# In[ ]:

from functools import reduce
import random


# In[ ]:

class Hypergraph(object):
    """
    Stores data specifying which terrains can be present in a single tile,
    and uses that data to generate random terrain grids.
    """
    def __init__(self, raw_hypergraph):
        # Input data is a dict of lists of lists.
        # Convert it to a dict of frozensets of frozensets.
        self.data = {k: frozenset(map(frozenset,v))
                     for (k,v) in raw_hypergraph.items()}
    @staticmethod
    def flatten_options(options):
        """Returns the union of the all the sets contained in `options`"""
        return reduce(lambda x,y: x.union(y),
                      options,
                      frozenset())
    def terrain_options(self, *terrains):
        """
        Returns a frozenset containing the terrains which
        can legally be placed in the same tile as the
        terrains contained in `terrains`.
        """
        if len(terrains) == 0:
            # All terrains are valid
            return list(self.data.keys())
        # Start with the list of hyperedges (cliques) containing the first terrain:
        start = list(self.data[terrains[0]])
        # For each additional terrain:
        seq = terrains[1:]
        # Restrict the list of cliques to those containing this terrain
        combine = lambda options, terrain: [clique for clique in options if terrain in clique]
        # Take the union of the remaining cliques
        return self.flatten_options(reduce(combine, seq, start))
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


# In[ ]:

if __name__ == '__main__':
    th = Hypergraph({'a':[['a','b'],['c','a']],
                     'b':[['a','b'],['b','c']],
                     'c':[['b','c'],['c','a']]})
    for line in th.generate_lines(10,10):
        print(''.join(line)), 

