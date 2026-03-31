import math
import re
import time
from typing import Optional

from type import ActionType, Observation
from vereya_env import VereyaEnvironment, VEREYA_AVAILABLE


currentEnv = None


def toSymbol(value) -> str:
    if value is None:
        return "unknown"
    text = str(value).strip().lower()
    text = text.replace("minecraft:", "")
    text = re.sub(r"[^a-z0-9_]", "_", text)
    text = re.sub(r"_+", "_", text)
    return text if text else "unknown"

def connectToMinecraft() -> str:
    global currentEnv
    
    if VEREYA_AVAILABLE:
        try:
            env = VereyaEnvironment()
            if env.connect():
                currentEnv = env
                return "Connected to Vereya Minecraft"
        except Exception as e:
            print(f"Vereya connection failed: {e}")
    return "Failed to connect to Minecraft. Ensure Vereya mod is installed and Minecraft is running."

def disconnectFromMinecraft() -> str:
    if currentEnv:
        currentEnv.disconnect()
    return "Disconnected"

def _getRawObservation() -> Optional[Observation]:
    if not currentEnv:
        return None
    try:
        return currentEnv.getObservation()
    except Exception:
        return None

def getObservation() -> list:
    obs = _getRawObservation()
    if obs is not None:
        return observationToMetta(obs)
    return []


def serverCommand(command: str):
    if not currentEnv or not getattr(currentEnv, "mc", None):
        return []
    cmd = str(command or "").strip()
    if not cmd:
        return []
    if cmd.startswith("/"):
        cmd = cmd[1:]

    low = cmd.lower()
    m = re.match(r"^time\s+add\s+(-?\d+)\s*$", low)
    if m:
        delta = int(m.group(1))
        prev = int(getattr(currentEnv, "timeAddOffset", 0))
        setattr(currentEnv, "timeAddOffset", prev + delta)
    
    try:
        currentEnv.mc.sendCommand(f"chat /{cmd}")
        return f"/{cmd}"
    except Exception as e:
        print(f"Failed server command '/{cmd}': {e}")
        return []


def sleepSeconds(seconds: float = 0.3):
    try:
        delay = max(0.0, float(seconds))
    except Exception:
        delay = 0.3
    time.sleep(delay)
    return "ok"

def executeAction(actionName: str, *args):
    print(f"Executing Action: {actionName} with args {args}")
    
    try:
        def normalizeActionResult(result):
            return [] if result is None else result

        if not currentEnv:
            print("No Minecraft environment connected.")
            return []
        
        normalized = re.sub(r'(?<!^)(?=[A-Z])', '_', actionName).lower()
        key = normalized.upper()
        actionMap = {
            # motion + orientation
            "move_forward": ActionType.MOVE_FORWARD,
            "turn_left": ActionType.TURN_LEFT,
            "turn_right": ActionType.TURN_RIGHT,
            "jump": ActionType.JUMP,
            "move_to": ActionType.MOVE_TO,

            # interaction
            "attack": ActionType.ATTACK,
            "eat": ActionType.EAT,
            "use": ActionType.USE,
            "place": ActionType.PLACE,
            "dig": ActionType.DIG,
            "crouch": ActionType.CROUCH,
            "drop": ActionType.DROP,
            
            # shelter
            "build_shelter": ActionType.BUILD_SHELTER,
            "seek_shelter": ActionType.SEEK_SHELTER,
            "enter_shelter": ActionType.ENTER_SHELTER,
            "find_ground": ActionType.FIND_GROUND,
            "sleep_at_night": ActionType.SLEEP_AT_NIGHT,
        }

        if normalized in actionMap and actionMap[normalized] == ActionType.MOVE_TO:
            if len(args) >= 3 and hasattr(currentEnv, 'moveTo'):
                return normalizeActionResult(
                    currentEnv.moveTo(float(args[0]), float(args[1]), float(args[2]))
                )
            print("Invalid arguments for move_to action. Expected 3 coordinates.")
            return []

        if normalized == "chat":
            msg = args[0] if args else "Hello"
            if currentEnv and hasattr(currentEnv, 'rob') and currentEnv.rob:
                currentEnv.rob.sendCommand(f"chat {msg}")
                return f"Chatted: {msg}"
            print("Current environment does not support chat command.")
            return []

        if normalized in actionMap:
            target_action = actionMap[normalized]
            return normalizeActionResult(currentEnv.executeAction(target_action))

        if hasattr(ActionType, key):
            act = getattr(ActionType, key)
            return normalizeActionResult(currentEnv.executeAction(act))
        
        print(f"Action '{actionName}' not recognized or not implemented.")
        return []


            
    except Exception as e:
        print(f"Error executing {actionName}: {e}")
        return []

def observationToMetta(obs: Observation):
    atoms = []
    x, y, z = obs.position
    atoms.append(f"(at {x} {y} {z})")
    atoms.append(f"(yaw {obs.yaw})")
    atoms.append(f"(health {obs.health})")
    atoms.append(f"(hunger {obs.hunger})")
    atoms.append(f"(time {obs.timeOfDay})")
    atoms.append(f"(isDay {str(obs.isDay)})")
    atoms.append(f"(air {obs.air if obs.air is not None else 300.0})")
    atoms.append(f"(onGround {str(obs.onGround) if obs.onGround is not None else 'True'})")
    if isinstance(obs.actionStatus, dict):
        for cmd, val in obs.actionStatus.items():
            try:
                atoms.append(f"(actionStatus {toSymbol(cmd)} {float(val)})")
            except Exception:
                continue
    
    if obs.nearbyEntities:
        for entity in obs.nearbyEntities:
            if isinstance(entity, dict):
                eType = toSymbol(entity.get('type', 'unknown'))
                dist = entity.get('distance', 0)
                pos = entity.get('position', [0,0,0])
                atoms.append(f"(nearEntity {eType} {dist} {pos[0]} {pos[1]} {pos[2]})")


    if obs.nearbyBlocks:
         for block in obs.nearbyBlocks:
             bType = block.get('type', 'stone')
             atoms.append(f"(nearBlock {bType})")
             
    if obs.inventory:
        for item in obs.inventory:
            if isinstance(item, dict):
                iType = toSymbol(item.get('item', 'unknown'))
                count = item.get('count', 1)
                atoms.append(f"(hasItem {iType} {count})")

    if obs.lineOfSightType is not None:
        atoms.append(f"(lineOfSightType {toSymbol(obs.lineOfSightType)})")
    if obs.lineOfSightDistance is not None:
        atoms.append(f"(lineOfSightDistance {obs.lineOfSightDistance})")
    if obs.lineOfSightHitType is not None:
        atoms.append(f"(lineOfSightHitType {toSymbol(obs.lineOfSightHitType)})")
    if isinstance(obs.lineOfSight, dict) and "inRange" in obs.lineOfSight:
        atoms.append(f"(lineOfSightInRange {str(obs.lineOfSight.get('inRange'))})")
                
    return atoms

def getHungerLevel() -> str:
    obs = _getRawObservation()
    return str(obs.hunger if obs is not None and obs.hunger is not None else 20.0)

def getHealth() -> str:
    obs = _getRawObservation()
    return str(obs.health if obs is not None and obs.health is not None else 20.0)

def isDay() -> str:
    obs = _getRawObservation()
    return "True" if obs is None or obs.isDay else "False"

def getAirLevel() -> str:
    obs = _getRawObservation()
    return str(obs.air if obs is not None and obs.air is not None else 300.0)

def hasShelterKnown() -> str:
    if not currentEnv:
        return "False"
    return "True" if bool(getattr(currentEnv, "shelterState", None)) else "False"

def sortEntities(*args) -> list:
    if not args:
        return []
    data = list(args[0]) if len(args) == 1 and isinstance(args[0], (list, tuple)) else list(args)
    
    try:
        return sorted(data, key=lambda e: float(e[-1]) if isinstance(e, (list, tuple)) and len(e) > 0 else 0)
    except Exception as e:
        print(f"Error sorting entities in Python: {e}")
        return data


