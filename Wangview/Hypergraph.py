
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
        combine = lambda options, terrain: filter(lambda clique: terrain in clique, options)
        # Take the union of the remaining cliques
        return self.flatten_options(reduce(combine, seq, start))
    def terrain_options_2(self, t_left=[], t_up=[]):
        """
        Returns a frozenset containing the terrains which can legally be placed
        in a location with adjacent terrains as specified in `t_left` and `t_up`.
        
        The following graph illustrates the meaning of `t_left` and `t_up`:
        ```
        | 1.| 2. | 3. | 4. | 5.  | 6. | 
        |   |    |    | UV | UVW | UV | 
        | O | LO | LO | O  | LO  | LO | 
        ```
        `O` represents the output terrain.
        `L` represents the 0 or 1 terrains in `t_left`.
        `U`, `V`, and `W` represent the 0, 2, or 3 terrains in `t_up`.
        Cases 4, 5, and 6 are used when the output terrain must agree
        with an adjacent line.
        Cases 1, 2, and 3 are used otherwise.
        Cases 1 and 4 are used when the output terrain is the first in the line.
        There is no terrain to the left, so the only constraints come from U and V.
        In case 1, U, V, and L are all missing, so there are no constraints.
        Cases 2 and 5 are used when the output terrain is in the middle of the line.
        In case 5, the output terrain is in the corner of two different tiles,
        which impose separate constraints: UVL and VW.
        Cases 3 and 6 are used when the output terrain is the last in the line.
        With no tile to the right, the only constraints come from UVL, or just L.
        See also: `terrain_options`, `generate_line`
        """
        if len(t_up) == 0:
            # Case 1, 2, or 3.
            # Evaluate constraint L or {}
            return self.terrain_options(*t_left)
        # Case 4, 5, or 6.
        # Evaluate constraint L, UV, or UVL
        # (depending on the lengths of t_left and t_up)
        x = self.terrain_options(*(t_left+t_up[:2]))
        if len(t_up) == 3:
            # Case 5.
            # Evaluate constraint VW
            y = self.terrain_options(*t_up[1:])
            # The result is the intersection of constraints UVL and VW
            return x.intersection(y)
        # Return the unaltered constraint L, UV, or UVL
        return x
    def generate_line(self, width, previous_line=None):
        """
        Generates a line of terrain values which satisfy adjacency constraints.
        Each output terrain will agree with the adjacent terrains in the output line.
        If previous_line is a sequence of terrains,
        Each output terrain will also agree with the adjacent terrains in that line.
        """
        new_line = []
        # L in `terrain_options_2` is not present in the first row
        t_left = []
        t_up = []
        for i in range(width):
            if previous_line is not None:
                # Try to get the slice of the previous line containing indices (i-1, i, i+1).
                # These are U, V, L in `terrain_options_2`.
                # Slice indices after the end are not a problem,
                # But slice indices before the beginning must be replaced by 0.
                t_up = previous_line[max(0,i-1):i+2]
            # Get a container of possible terrains for this position
            options = self.terrain_options_2(t_left, t_up)
            # Select a random terrain from the options
            new_line.append(random.choice(list(options)))
            # Set L to the value just inserted
            t_left = [new_line[-1]]
        return new_line
    def generate_lines(self, width, height):
        """Yields each line of a grid of terrain values satisfying the ajdacency constraints"""
        # Yield a line with no constraints from a preceding line
        line = self.generate_line(width)
        yield line
        for i in range(height):
            # Yield a line with additional constraints from the previous line
            line = self.generate_line(width, line)
            yield line


# In[ ]:

if __name__ == '__main__':
    # A quick test that the class is working correctly
    th = Hypergraph({'a':[['a','b'],['c','a']],
                     'b':[['a','b'],['b','c']],
                     'c':[['b','c'],['c','a']]})
    for line in th.generate_lines(10,10):
        print(''.join(line)), 

