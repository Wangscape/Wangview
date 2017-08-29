
# coding: utf-8
from Wangview.Display import Display
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render random landscapes using Wangscape tiles')
    parser.add_argument('path', type=str, default='.', help='Path to the folder containing the tileset and metadata')
    parser.add_argument('-g', '--tile-groups', metavar='TILE_GROUPS.json', type=str, default='tile_groups.json', help='Name of the tile groups JSON file')
    parser.add_argument('-c', '--terrain-hypergraph', metavar='TERRAIN_HYPERGRAPH.json', type=str, default='terrain_hypergraph.json', help='Name of the terrain hypergraph JSON file')
    parser.add_argument('-t', '--tileset-data', metavar='TILESET_DATA.json', type=str, default='tilesets.json', help='Name of the tileset data JSON file')
    parser.add_argument('-f', '--fps', metavar='FPS', type=int, default=30, help='Maximum frames per second')
    map_parser = parser.add_mutually_exclusive_group()
    map_parser.add_argument('-s', '--size', type=int, dest='map_mode', nargs=2, metavar=('X','Y'), help='Size of the map display')
    map_parser.add_argument('-m', '--fixed-map', metavar='FIXED_MAP.json', type=str, dest='map_mode', help='Name of a JSON file with a fixed map')
    output_parser = parser.add_argument_group()
    output_parser.add_argument('-d', '--display', dest='output_mode', action='append_const', const=True, help='Display maps in a GUI interface')
    output_parser.add_argument('-o', '--output', metavar='OUTPUT.png', dest='output_mode', action='append', type=str, help='Name of the image file to write the scene to')
    parser.set_defaults(map_mode=[30,20], output_mode=[])
    args = parser.parse_args()
    try:
        w = Display(rel_path = args.path,
                    fn_tile_groups = args.tile_groups,
                    fn_terrain_hypergraph = args.terrain_hypergraph,
                    fn_tileset_data = args.tileset_data,
                    fps = args.fps,
                    map_mode = args.map_mode,
                    output_mode = args.output_mode)
        w.run()
    except (IndexError, FileNotFoundError):
        parser.print_help()
        raise
