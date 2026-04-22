import sys
import unittest
from pathlib import Path


MINECRAFT_DIR = Path(__file__).resolve().parents[2]
if str(MINECRAFT_DIR) not in sys.path:
    sys.path.insert(0, str(MINECRAFT_DIR))

from navigation import Navigation


def make_flat_grid(x_range, z_range):
    grid = {}
    for x in x_range:
        for z in z_range:
            grid[(x, -1, z)] = "stone"
            grid[(x, 0, z)] = "air"
            grid[(x, 1, z)] = "air"
    return grid


class TestNavigation(unittest.TestCase):
    def test_normalize_block_name_removes_prefix_and_properties(self):
        self.assertEqual(Navigation.normalizeBlockName("minecraft:oak_door[facing=north]"), "oak_door")

    def test_is_passable_accepts_air(self):
        self.assertTrue(Navigation.is_passable("minecraft:air"))

    def test_is_passable_rejects_solid_block(self):
        self.assertFalse(Navigation.is_passable("minecraft:stone"))

    def test_is_safe_rejects_lava(self):
        self.assertFalse(Navigation.is_safe("minecraft:lava"))

    def test_parse_grid_maps_values_in_expected_order(self):
        grid_box = [[0, 1], [0, 0], [0, 1]]
        grid_list = ["air", "stone", "grass", "torch"]

        result = Navigation.parseGrid(grid_list, grid_box)

        self.assertEqual(result[(0, 0, 0)], "air")
        self.assertEqual(result[(1, 0, 0)], "stone")
        self.assertEqual(result[(0, 0, 1)], "grass")
        self.assertEqual(result[(1, 0, 1)], "torch")

    def test_get_neighbors_returns_walkable_adjacent_positions(self):
        grid_map = make_flat_grid(range(0, 3), range(0, 2))

        neighbors = Navigation.getNeighbors((0, 0, 0), grid_map)

        self.assertIn((1, 0, 0), neighbors)
        self.assertIn((0, 0, 1), neighbors)

    def test_astar_returns_path_in_simple_open_grid(self):
        grid_map = make_flat_grid(range(0, 3), range(0, 1))

        path = Navigation.aStar((0, 0, 0), (2, 0, 0), grid_map)

        self.assertEqual(path, [(1, 0, 0), (2, 0, 0)])

    def test_astar_returns_none_when_goal_is_missing(self):
        grid_map = make_flat_grid(range(0, 2), range(0, 1))

        path = Navigation.aStar((0, 0, 0), (5, 0, 0), grid_map)

        self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()
