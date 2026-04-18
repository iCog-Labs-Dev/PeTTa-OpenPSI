import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


MINECRAFT_DIR = Path(__file__).resolve().parents[1]
if str(MINECRAFT_DIR) not in sys.path:
    sys.path.insert(0, str(MINECRAFT_DIR))

import inventory


class TestInventory(unittest.TestCase):
    def test_find_edible_inventory_item_returns_none_when_no_edible_item_exists(self):
        items = [{"type": "minecraft:stone", "quantity": 5, "index": 0}]
        self.assertIsNone(inventory.findEdibleInventoryItem(items))

    def test_find_edible_inventory_item_ignores_zero_quantity_food(self):
        items = [{"type": "minecraft:apple", "quantity": 0, "index": 0}]
        self.assertIsNone(inventory.findEdibleInventoryItem(items))

    def test_find_edible_inventory_item_prefers_index_zero(self):
        items = [
            {"type": "minecraft:bread", "quantity": 2, "index": 3},
            {"type": "minecraft:apple", "quantity": 1, "index": 0},
        ]
        self.assertEqual(inventory.findEdibleInventoryItem(items), items[1])

    def test_find_edible_inventory_item_uses_random_choice_when_needed(self):
        items = [
            {"type": "minecraft:bread", "quantity": 2, "index": 3},
            {"type": "minecraft:apple", "quantity": 1, "index": 2},
        ]
        with patch("inventory.random.choice", return_value=items[0]) as mocked_choice:
            result = inventory.findEdibleInventoryItem(items)
        self.assertEqual(result, items[0])
        mocked_choice.assert_called_once()

    def test_get_current_item_index_returns_none_when_env_has_no_mc(self):
        env = SimpleNamespace(mc=None)
        self.assertIsNone(inventory.getCurrentItemIndex(env))

    def test_get_current_item_index_reads_value_from_mc_observe(self):
        fake_observe = MagicMock()
        fake_observe.get.return_value = {"currentItemIndex": 4}
        env = SimpleNamespace(mc=SimpleNamespace(observe=fake_observe, agentId="agent-1"))

        self.assertEqual(inventory.getCurrentItemIndex(env), 4)


if __name__ == "__main__":
    unittest.main()
