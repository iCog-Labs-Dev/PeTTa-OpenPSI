import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


MINECRAFT_DIR = Path(__file__).resolve().parents[1]
if str(MINECRAFT_DIR) not in sys.path:
    sys.path.insert(0, str(MINECRAFT_DIR))

import observation


class FakeRob:
    def __init__(self, cache):
        self.cache = cache
        self.observe_called = False

    def observeProcCached(self):
        self.observe_called = True

    def getCachedObserve(self, key):
        return self.cache.get(key)


class FakeMc:
    def __init__(self, stats, action_status):
        self.stats = stats
        self.action_status = action_status

    def getFullStat(self, key):
        return self.stats.get(key)

    def getActionStatus(self):
        return self.action_status


class TestObservation(unittest.TestCase):
    def test_get_default_observation_has_safe_defaults(self):
        obs = observation.getDefaultObservation()

        self.assertEqual(obs.position, (0, 0, 0))
        self.assertEqual(obs.health, 0)
        self.assertEqual(obs.hunger, 0.0)
        self.assertEqual(obs.air, 300.0)
        self.assertTrue(obs.onGround)
        self.assertEqual(obs.actionStatus, "unknown")

    def test_build_observation_returns_defaults_when_disconnected(self):
        env = SimpleNamespace(connected=False, rob=None)
        obs = observation.buildObservation(env)

        self.assertEqual(obs.position, (0, 0, 0))
        self.assertEqual(obs.air, 300.0)

    def test_build_observation_uses_fake_env_data(self):
        cache = {
            "getAgentPos": [10.0, 65.0, -4.0, 12.0, 90.0],
            "getLife": 18.0,
            "getAir": 240.0,
            "getOnGround": False,
            "getNearEntities": [
                {"name": "Zombie", "x": 13.0, "y": 65.0, "z": -4.0},
                {"name": "Cow", "x": 10.0, "y": 65.0, "z": -1.0},
            ],
            "getInventory": [
                {"type": "minecraft:apple", "quantity": 3},
                {"type": "minecraft:stone", "quantity": 10},
            ],
            "getLineOfSights": {"type": "minecraft:oak_log", "distance": 2.5, "hitType": "block"},
        }
        env = SimpleNamespace(
            connected=True,
            rob=FakeRob(cache),
            mc=FakeMc({"Food": 7.0, "WorldTime": 14000}, {"move": 1.0}),
            mission=SimpleNamespace(
                serverSection=SimpleNamespace(
                    initial_conditions=SimpleNamespace(time_start="0")
                )
            ),
            timeAddOffset=0,
        )

        obs = observation.buildObservation(env)

        self.assertTrue(env.rob.observe_called)
        self.assertEqual(obs.position, (10.0, 65.0, -4.0))
        self.assertEqual(obs.yaw, 90.0)
        self.assertEqual(obs.pitch, 12.0)
        self.assertEqual(obs.health, 18.0)
        self.assertEqual(obs.hunger, 7.0)
        self.assertEqual(obs.air, 240.0)
        self.assertFalse(obs.onGround)
        self.assertFalse(obs.isDay)
        self.assertEqual(obs.timeOfDay, 14000)
        self.assertEqual(obs.actionStatus, {"move": 1.0})
        self.assertEqual(obs.inventory[0], {"item": "minecraft:apple", "count": 3})
        self.assertEqual(obs.lineOfSightType, "minecraft:oak_log")
        self.assertEqual(obs.lineOfSightDistance, 2.5)
        self.assertEqual(obs.lineOfSightHitType, "block")
        self.assertEqual(len(obs.nearbyEntities), 2)
        self.assertAlmostEqual(obs.nearbyEntities[0]["distance"], 3.0)


if __name__ == "__main__":
    unittest.main()
