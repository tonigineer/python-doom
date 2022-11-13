from collections import deque


DIRS = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if not (x == y == 0)]
# make diagonals last in list
# otherwise the enemy walks zigzag to target
DIRS = sorted(DIRS, key=lambda x: sum([abs(x[0]), abs(x[1])]))


def manhattan_dist(pos1: tuple, pos2: tuple) -> int:
    return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])


class PathFinding:

    def __init__(self, game):
        self.game = game
        self.tiles = self.game.map.tiles

        self.graph = {}
        self._create_graph()

    def _possible_moves(self, x, y):
        return [(x + dx, y + dy) for dx, dy in DIRS
                if not self.game.map.tiles[y + dy][x + dx]]

    def _create_graph(self):
        for y, row in enumerate(self.game.map.tiles):
            for x, tile in enumerate(row):
                if not tile:
                    self.graph[(x, y)] = self._possible_moves(x, y)

    def get_path(self, start, target):
        visited = self._bfs(start, target)
        path = [target]

        while path[-1] != start:
            try:
                path.append(visited[path[-1]])
            except KeyError:
                print('no path found, todo :D')
                path = [start]

        return path

    def _bfs(self, start, target):
        queue = deque([start])
        visited = {start: None}

        while queue:
            node = queue.popleft()
            if node == target:
                break
            moves = self.graph[node]

            for move in moves:
                if move in visited:
                    continue
                if move in self.game.npc_handler.npc_positions:
                    continue
                queue.append(move)
                visited[move] = node
        return visited
