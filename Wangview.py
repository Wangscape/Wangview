
# coding: utf-8

# In[ ]:

from Wangview.Display import Display
import sys


# In[ ]:

if __name__ == '__main__':
    import sys
    try:
        w = Display(*sys.argv[1:])
        w.run()
    except (IndexError, FileNotFoundError):
        print('Usage: Wangview.py [path [tile_groups.json [terrain_hypergraph.json [tileset_data.json]]]]\n')
        raise

