import os
import subprocess

def is_wsl():
    try:
        with open("/proc/sys/kernel/osrelease", "r") as f:
            if "microsoft" in f.read().lower():
                return True
    except OSError:
        pass
    return "WSL_DISTRO_NAME" in os.environ

def detect_wsl_host_ip():
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return None

    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        parts = line.split()
        if "via" in parts:
            via_index = parts.index("via")
            if via_index + 1 < len(parts):
                return parts[via_index + 1]
    return None


def resolveClientIp():
    env_client_ip = os.getenv("OPENPSI_MINECRAFT_CLIENT_IP")
    if env_client_ip:
        print(f"Environment variable OPENPSI_MINECRAFT_CLIENT_IP: {env_client_ip}")
        return env_client_ip.strip()

    if is_wsl():
        detected_ip = detect_wsl_host_ip()
        print(f"WSL detected. Auto-detected Windows host IP: {detected_ip}")
        if detected_ip:
            return detected_ip
        raise RuntimeError(
            "WSL detected but the Windows host IP could not be auto-detected. "
            "Set OPENPSI_MINECRAFT_CLIENT_IP to your Windows host IP."
        )

    # Default (Linux / Windows)
    return "127.0.0.1"
