import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


MINECRAFT_DIR = Path(__file__).resolve().parents[2]
if str(MINECRAFT_DIR) not in sys.path:
    sys.path.insert(0, str(MINECRAFT_DIR))

import shelter


class TestShelter(unittest.TestCase):
    def test_shelter_plan_returns_expected_structures(self):
        floor, walls, roof, torches, doorway, outside_button, inside_pressure_plate, bed = shelter.shelterPlan(0, 64, 0)

        self.assertTrue(len(floor) > 0)
        self.assertTrue(len(walls) > 0)
        self.assertTrue(len(roof) > 0)
        self.assertEqual(len(torches), 4)
        self.assertEqual(doorway, (0, 64, -shelter.SHELTER_RADIUS))
        self.assertEqual(len(bed), 2)
        self.assertEqual(outside_button[2], doorway[2] - 1)
        self.assertEqual(inside_pressure_plate[2], doorway[2] + 1)

    def test_has_nearby_hostile_observation_detects_close_hostile(self):
        obs = SimpleNamespace(
            nearbyEntities=[
                {"type": "minecraft:zombie", "distance": 5.0},
                {"type": "minecraft:cow", "distance": 2.0},
            ]
        )
        self.assertTrue(shelter._hasNearbyHostileObservation(obs))

    def test_has_nearby_hostile_observation_ignores_non_hostiles(self):
        obs = SimpleNamespace(
            nearbyEntities=[
                {"type": "minecraft:cow", "distance": 3.0},
                {"type": "minecraft:pig", "distance": 4.0},
            ]
        )
        self.assertFalse(shelter._hasNearbyHostileObservation(obs))

    def test_has_shelter_checks_shelter_state(self):
        self.assertTrue(shelter.hasShelter(SimpleNamespace(shelterState={"center": (0, 64, 0)})))
        self.assertFalse(shelter.hasShelter(SimpleNamespace(shelterState=None)))


if __name__ == "__main__":
    unittest.main()
