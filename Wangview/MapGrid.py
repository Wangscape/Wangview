
# coding: utf-8
from collections import deque

class MapGrid(object):
    """Stores terrain and tile information for display."""
    def __init__(self, *size):
        self._columns, self._rows = (0, 0)
        self._columns_max, self._rows_max = size
        self._grid = deque(maxlen=self._rows_max)
    def full(self):
        """Returns True if the MapGrid is at full capacity, False otherwise."""
        return self._rows == self._rows_max and self._columns == self._columns_max
    def _make_row(self, sequence):
        """Converts a sequence into a row object compatible with the MapGrid."""
        return deque(sequence, maxlen=self._columns_max)
    def iter_border(self, horizontal, top_left):
        """Returns an iterator which yields values from one of the MapGrid's four borders."""
        if horizontal:
            return self.row(0 if top_left else self._rows-1)
        else:
            return self.column(0 if top_left else self._columns-1)
    def add_line(self, line, horizontal, top_left):
        """Appends a row or column to the MapGrid, rotating or growing as necessary."""
        line = list(line)
        append = deque.appendleft if top_left else deque.append
        if horizontal:
            if self._columns == 0:
                assert len(line) <= self._columns_max, "first row too long"
                self._columns = len(line)
            else:
                assert len(line) == self._columns, "wrong length row added"
            self._rows = min(self._rows+1, self._rows_max)
            append(self._grid, self._make_row(line))
        else:
            if self._rows == 0:
                assert len(line) <= self._rows_max, "first column too long"
                self._rows = len(line)
                for _ in range(len(line)):
                    self._grid.append(self._make_row([]))
            else:
                assert len(line) == self._rows, "wrong length column added"
            self._columns = min(self._columns+1, self._columns_max)
            for terrain, row in zip(line, self._grid):
                append(row,terrain)
    def row(self, y):
        """Returns an iterator for the specified row."""
        return iter(self._grid[y])
    def column(self, x):
        """Returns an iterator for the specified column."""
        return (line[x] for line in self._grid)
    def __iter__(self):
        """Returns an iterator of row iterators."""
        for row in self._grid:
            yield iter(row)
    def __getitem__(self, xy):
        """Returns the value at the given coordinates."""
        x,y = xy
        return self._grid[y][x]
    def __str__(self):
        """Returns a string representation of the MapGrid's contents."""
        return '\n'.join(' '.join(map(str,row)) for row in self._grid)
