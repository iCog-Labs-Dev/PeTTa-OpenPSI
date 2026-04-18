import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch


MINECRAFT_DIR = Path(__file__).resolve().parents[1]
if str(MINECRAFT_DIR) not in sys.path:
    sys.path.insert(0, str(MINECRAFT_DIR))

import network_utils


class TestNetworkUtils(unittest.TestCase):
    def test_is_wsl_true_when_proc_file_mentions_microsoft(self):
        with patch("builtins.open", mock_open(read_data="5.15.90-microsoft-standard-WSL2")):
            with patch.dict(os.environ, {}, clear=True):
                self.assertTrue(network_utils.is_wsl())

    def test_is_wsl_true_when_wsl_distro_name_is_set(self):
        with patch("builtins.open", side_effect=OSError):
            with patch.dict(os.environ, {"WSL_DISTRO_NAME": "Ubuntu"}, clear=True):
                self.assertTrue(network_utils.is_wsl())

    def test_is_wsl_false_when_no_signal_exists(self):
        with patch("builtins.open", side_effect=OSError):
            with patch.dict(os.environ, {}, clear=True):
                self.assertFalse(network_utils.is_wsl())

    def test_detect_wsl_host_ip_returns_gateway_ip(self):
        fake_result = MagicMock(returncode=0, stdout="default via 172.19.176.1 dev eth0\n")
        with patch("subprocess.run", return_value=fake_result):
            self.assertEqual(network_utils.detect_wsl_host_ip(), "172.19.176.1")

    def test_detect_wsl_host_ip_returns_none_on_failed_command(self):
        fake_result = MagicMock(returncode=1, stdout="")
        with patch("subprocess.run", return_value=fake_result):
            self.assertIsNone(network_utils.detect_wsl_host_ip())

    def test_detect_wsl_host_ip_returns_none_when_subprocess_raises(self):
        with patch("subprocess.run", side_effect=subprocess.SubprocessError):
            self.assertIsNone(network_utils.detect_wsl_host_ip())

    def test_resolve_client_ip_prefers_env_override(self):
        with patch.dict(os.environ, {"OPENPSI_MINECRAFT_CLIENT_IP": "10.0.0.55"}, clear=True):
            with patch("builtins.print"):
                self.assertEqual(network_utils.resolveClientIp(), "10.0.0.55")

    def test_resolve_client_ip_uses_detected_host_ip_under_wsl(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(network_utils, "is_wsl", return_value=True):
                with patch.object(network_utils, "detect_wsl_host_ip", return_value="172.19.176.1"):
                    with patch("builtins.print"):
                        self.assertEqual(network_utils.resolveClientIp(), "172.19.176.1")

    def test_resolve_client_ip_defaults_to_loopback_for_normal_linux(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(network_utils, "is_wsl", return_value=False):
                self.assertEqual(network_utils.resolveClientIp(), "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
