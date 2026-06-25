import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


MINECRAFT_DIR = Path(__file__).resolve().parents[2]
if str(MINECRAFT_DIR) not in sys.path:
    sys.path.insert(0, str(MINECRAFT_DIR))

import utils
from type import Observation


class TestMinecraftUtils(unittest.TestCase):
    def tearDown(self):
        utils.currentEnv = None

    def test_to_symbol_normalizes_text(self):
        self.assertEqual(utils.toSymbol("Minecraft:Oak Door!"), "oak_door_")

    def test_to_symbol_returns_unknown_for_none(self):
        self.assertEqual(utils.toSymbol(None), "unknown")

    def test_sort_entities_orders_by_last_value(self):
        entities = [(10, 64, 10, 5.0), (1, 64, 1, 1.2), (2, 64, 2, 3.0)]
        self.assertEqual(utils.sortEntities(entities), [(1, 64, 1, 1.2), (2, 64, 2, 3.0), (10, 64, 10, 5.0)])

    def test_sort_entities_returns_original_data_when_sorting_fails(self):
        broken_entities = [{"distance": 2}, {"distance": 1}]
        self.assertEqual(utils.sortEntities(broken_entities), broken_entities)

    def test_observation_to_metta_serializes_core_fields(self):
        obs = Observation(
            position=(1.5, 64.0, -2.0),
            yaw=90.0,
            pitch=0.0,
            health=18.0,
            hunger=7.0,
            isDay=True,
            timeOfDay=6000,
            inventory=[{"item": "minecraft:apple", "count": 3}],
            nearbyEntities=[{"type": "minecraft:zombie", "distance": 4.0, "position": [2, 64, -1]}],
            nearbyBlocks=[{"type": "stone"}],
            lineOfSight={"inRange": True},
            air=250.0,
            onGround=False,
            actionStatus={"move forward": 1.0},
            lineOfSightType="minecraft:oak_log",
            lineOfSightDistance=3.5,
            lineOfSightHitType="block",
        )

        atoms = utils.observationToMetta(obs)

        self.assertIn("(at 1.5 64.0 -2.0)", atoms)
        self.assertIn("(health 18.0)", atoms)
        self.assertIn("(hunger 7.0)", atoms)
        self.assertIn("(isDay True)", atoms)
        self.assertIn("(air 250.0)", atoms)
        self.assertIn("(onGround False)", atoms)
        self.assertIn("(actionStatus move_forward 1.0)", atoms)
        self.assertIn("(nearEntity zombie 4.0 2 64 -1)", atoms)
        self.assertIn("(hasItem apple 3)", atoms)
        self.assertIn("(lineOfSightType oak_log)", atoms)
        self.assertIn("(lineOfSightDistance 3.5)", atoms)
        self.assertIn("(lineOfSightHitType block)", atoms)
        self.assertIn("(lineOfSightInRange True)", atoms)

    def test_server_command_updates_time_offset_and_sends_chat_command(self):
        fake_mc = SimpleNamespace(sendCommand=MagicMock())
        utils.currentEnv = SimpleNamespace(mc=fake_mc, timeAddOffset=0)

        result = utils.serverCommand("/time add 1000")

        self.assertEqual(result, "/time add 1000")
        self.assertEqual(utils.currentEnv.timeAddOffset, 1000)
        fake_mc.sendCommand.assert_called_once_with("chat /time add 1000")

    def test_server_command_returns_empty_when_no_environment_is_connected(self):
        utils.currentEnv = None
        self.assertEqual(utils.serverCommand("time add 1000"), [])

    def test_sleep_seconds_clamps_invalid_input_and_returns_ok(self):
        with patch("utils.time.sleep") as mocked_sleep:
            result = utils.sleepSeconds("not-a-number")

        self.assertEqual(result, "ok")
        mocked_sleep.assert_called_once_with(0.3)


if __name__ == "__main__":
    unittest.main()
