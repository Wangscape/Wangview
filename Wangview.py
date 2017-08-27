
# coding: utf-8
from Wangview.Display import Display
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Render random landscapes using Wangscape tiles")
    parser.add_argument("path", type=str, default=".", help="Path to the folder containing the tileset and metadata")
    parser.add_argument("--tile-groups", type=str, default="tile_groups.json", help="Name of the tile groups JSON file")
    parser.add_argument("--terrain-hypergraph", type=str, default="terrain_hypergraph.json", help="Name of the terrain hypergraph JSON file")
    parser.add_argument("--tileset-data", type=str, default="tilesets.json", help="Name of the tileset data JSON file")
    parser.add_argument("--fps", type=int, default=30, help="Maximum frames per second")
    parser.add_argument("--size", type=int, nargs=2, metavar=("x","y"), default=(30,20), help="Size of the map display")
    # parser.add_argument("--map", type=str, default=None, help="Name of a JSON file with a fixed map")
    args = parser.parse_args()
    print(args)
    try:
        w = Display(args.path, args.tile_groups, args.terrain_hypergraph, args.tileset_data, args.fps, args.size)
        w.run()
    except (IndexError, FileNotFoundError):
        parser.print_help()
        raise
