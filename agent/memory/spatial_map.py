class SpatialMap:
    CELL_SIZE = 500
    WORLD_MIN = -10000
    WORLD_MAX = 10000

    def __init__(self):
        self.grid = {}    # (cx, cy) -> "explored"
        self.objects = {} # (cx, cy) -> obj_name

    def _world_to_cell(self, x, y):
        cx = int((x - self.WORLD_MIN) // self.CELL_SIZE)
        cy = int((y - self.WORLD_MIN) // self.CELL_SIZE)
        return cx, cy

    def _cell_to_world_center(self, cx, cy):
        x = self.WORLD_MIN + cx * self.CELL_SIZE + self.CELL_SIZE / 2
        y = self.WORLD_MIN + cy * self.CELL_SIZE + self.CELL_SIZE / 2
        return x, y

    def mark_explored(self, x, y):
        cell = self._world_to_cell(x, y)
        self.grid[cell] = "explored"

    def mark_object(self, x, y, obj_name):
        cell = self._world_to_cell(x, y)
        self.objects[cell] = obj_name
        self.grid[cell] = "explored"

    def get_explore_target(self, agent_x, agent_y):
        agent_cell = self._world_to_cell(agent_x, agent_y)
        grid_size = int((self.WORLD_MAX - self.WORLD_MIN) // self.CELL_SIZE)

        best = None
        best_dist = float('inf')

        for cx in range(grid_size):
            for cy in range(grid_size):
                if (cx, cy) not in self.grid:
                    dx = cx - agent_cell[0]
                    dy = cy - agent_cell[1]
                    dist = dx * dx + dy * dy
                    if dist < best_dist:
                        best_dist = dist
                        best = (cx, cy)

        if best:
            return self._cell_to_world_center(*best)
        return None

    def get_explored_count(self):
        return len(self.grid)

    def get_total_cells(self):
        grid_size = int((self.WORLD_MAX - self.WORLD_MIN) // self.CELL_SIZE)
        return grid_size * grid_size

    def to_dict(self):
        return {
            "grid": {f"{k[0]},{k[1]}": v for k, v in self.grid.items()},
            "objects": {f"{k[0]},{k[1]}": v for k, v in self.objects.items()}
        }

    @staticmethod
    def from_dict(data):
        sm = SpatialMap()
        for key, val in data.get("grid", {}).items():
            cx, cy = map(int, key.split(","))
            sm.grid[(cx, cy)] = val
        for key, val in data.get("objects", {}).items():
            cx, cy = map(int, key.split(","))
            sm.objects[(cx, cy)] = val
        return sm