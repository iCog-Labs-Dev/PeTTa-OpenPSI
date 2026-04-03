# Minecraft OpenPsi Agent

An embodied cognitive agent for Minecraft, powered by OpenPsi and MeTTa.

## Overview

This use-case connects OpenPsi's cognitive architecture to Minecraft via Vereya, enabling an agent whose behavior **emerges from internal needs** (hunger, safety, curiosity) rather than scripted logic.


## Requirements

- **Windows users should run the Python / MeTTa side from WSL** while Minecraft itself runs on Windows.
- **Linux users** can run everything natively.
- **Minecraft Java Edition** (Version 1.21).
- **Fabric Loader** (Version 1.21).
- **Python** 3.10+ installed on your system.
- **PeTTa runtime** available in your environment.
- **Vereya requires Fabric Loader and Fabric API**:
  - https://fabricmc.net/use/installer/
  - https://www.curseforge.com/minecraft/mc-mods/fabric-api

---

## 1. Create a Virtual Environment

Run the setup commands in Linux. If you are on Windows, open your WSL terminal first.

```bash
cd /path/to/PeTTa-OpenPSI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## 2. Install Python Requirements

Install the project requirements plus the Minecraft-specific packages:

```bash
pip install git+https://github.com/trueagi-io/minecraft-demo.git
pip install numpy
pip install dearpygui
```

Notes:
- `dearpygui` is required for the dashboard UI.
- `minecraft-demo` provides the `tagilmo` / Vereya Python integration used by this use-case.

## 3. Install the Minecraft Mods

1. Install **Fabric Loader 1.21**.
2. Go to your Minecraft `mods` folder.
3. Add these two files:
   - `fabric-api-[version]+1.21.jar`
   - `vereya-fabric-[version].jar`

## 4. Configure IP Address

For native Linux, keep the default connection behavior.

If you are using Windows, run the agent inside WSL. In that setup, `127.0.0.1` will not reach Minecraft because WSL is network-isolated from the Windows host. The agent must use the Windows host IP instead.

### WSL only: find the Windows host IP

```bash
ip route show default | awk '{print $3}'
```

(Example output: `172.19.176.1`)

Then set the override before starting the agent:

```bash
export OPENPSI_MINECRAFT_CLIENT_IP=$(ip route show default | awk '{print $3}')
```

The code keeps the default connection for native Linux, auto-detects the Windows host IP under WSL, and lets you override it with `OPENPSI_MINECRAFT_CLIENT_IP` when needed.

## 5. Start the Dashboard

Run the dashboard in a separate terminal with the same virtual environment activated:

```bash
python3 use-cases/minecraft/dashboard/progress_dashboard.py
```

By default, the dashboard listens on `127.0.0.1:5001`.

Optional override:

```bash
export OPENPSI_DASHBOARD_HOST=127.0.0.1
export OPENPSI_DASHBOARD_PORT=5001
python use-cases/minecraft/dashboard/progress_dashboard.py
```

## 6. Start Minecraft

1. Launch **Minecraft Java Edition** on the host machine.
2. Use the **Fabric Loader 1.21** profile.
3. Make sure the `fabric-api` and `vereya-fabric` jars are present in the `mods` folder.

## 7. Run the Agent

For a quick connection test:

```bash
source .venv/bin/activate
python use-cases/minecraft/vereya-api-test.py
```

To run the full OpenPsi Minecraft agent:

```bash
source .venv/bin/activate
metta use-cases/minecraft/main.metta
```

The dashboard should begin showing demand and action updates while the agent is running.
