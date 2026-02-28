from heapq import heappop, heappush
import math

class Navigation:
    walkableBlocks = {
        "air", "cave_air", "void_air", "grass", "tall_grass", 
        "poppy", "dandelion", "cornflower", "torch", "wall_torch",
        "oak_sapling", "wheat", "sugar_cane", "lever", "redstone_torch",
        "redstone_wire", "tripwire", "tripwire_hook", "rail"
    }
    dangerBlocks = {"lava", "fire", "magma_block", "cactus", "sweet_berry_bush"}
    @staticmethod
    def is_passable(blockType):
        return blockType in Navigation.walkableBlocks or "flower" in blockType or "fern" in blockType

    @staticmethod
    def is_safe(blockType):
        return blockType not in Navigation.dangerBlocks
    
    @staticmethod
    def getNeighbors(pos, gridMap):
        x, y, z = pos
        neighbors = []
        for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, nz = x + dx, z + dz
            
            for dy in [0, 1, -1]:
                ny = y + dy
                target = (nx, ny, nz)
                target_head = (nx, ny + 1, nz)
                block_below_target = (nx, ny - 1, nz)
                
                if target not in gridMap or target_head not in gridMap or block_below_target not in gridMap or Navigation.is_passable(gridMap[block_below_target]):
                    continue

                if not (Navigation.is_passable(gridMap[target]) and Navigation.is_passable(gridMap[target_head])):
                    continue
                
                if not Navigation.is_safe(gridMap[target]):
                    continue


                if dy == 1: 
                    nextHeadPosition = (x, y + 2, z)
                    if nextHeadPosition in gridMap and not Navigation.is_passable(gridMap[nextHeadPosition]):
                        continue
                
                neighbors.append(target)
                
        return neighbors

    @staticmethod
    def aStar(start, goal, grid_map):
        if start not in grid_map or goal not in grid_map:
            return None
        
        def heuristic(a, b):
            return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

        heap = []
        heappush(heap, (0, start))
        
        visited = {}
        g_score = {start: 0}
        uniformCost = 1
        
        iterations = 0
        MAX_ITER = 5000
        while heap:
            iterations += 1
            
            if iterations > MAX_ITER:
                print("Pathfinding timed out.")
                return None

            _, current = heappop(heap)

            if current == goal:
                path = []
                while current in visited:
                    path.append(current)
                    current = visited[current]

                return path[::-1]

            for neighbor in Navigation.getNeighbors(current, grid_map):
                current_g_cost = g_score[current] + uniformCost
                
                if neighbor not in g_score or current_g_cost < g_score[neighbor]:
                    visited[neighbor] = current
                    g_score[neighbor] = current_g_cost
                    f_score = current_g_cost + heuristic(neighbor, goal)
                    heappush(heap, (f_score, neighbor))
        
        return None

    @staticmethod
    def parseGrid(grid_list, grid_box):
        grid_map = {}
        x_min, x_max = grid_box[0]
        y_min, y_max = grid_box[1]
        z_min, z_max = grid_box[2]
        
        sz_x = x_max - x_min + 1
        sz_y = y_max - y_min + 1
        sz_z = z_max - z_min + 1
        
        idx = 0
        N = len(grid_list)
        for y_off in range(sz_y):
            for z_off in range(sz_z):
                for x_off in range(sz_x):
                    if idx < N:
                        pos = (x_min + x_off, y_min + y_off, z_min + z_off)
                        block_name = grid_list[idx].replace("minecraft:", "")
                        grid_map[pos] = block_name
                        idx += 1
        return grid_map