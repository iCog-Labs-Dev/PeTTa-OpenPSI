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

def executeAction(actionName: str, *args) -> str:
    print(f"Executing Action: {actionName} with args {args}")
    
    try:
        if not currentEnv:
            return "Not Connected"
        
        key = re.sub(r'(?<!^)(?=[A-Z])', '_', actionName).upper()
        actionMap = {
            "use": ActionType.USE,
            "crouch": ActionType.CROUCH,
            "drop": ActionType.DROP,
            "jump": ActionType.JUMP,
            "place": ActionType.PLACE,
            "dig": ActionType.DIG,
            "move_to": ActionType.MOVE_TO
        }
        
        # print("Mapped action key:", key)
        if actionName in actionMap and actionMap[actionName] == ActionType.MOVE_TO:
            # print("len of args:", len(args))
            if len(args) >= 3 and hasattr(currentEnv, 'moveTo'):
                return currentEnv.moveTo(float(args[0]), float(args[1]), float(args[2]))
            return "MoveTo failed: insufficient args or mode"
            
        
        if hasattr(ActionType, key):
            act = getattr(ActionType, key)
            # print("Debugging line", act)
            return currentEnv.executeAction(act)
        else:
            if actionName == "chat":
                msg = args[0] if args else "Hello"
                if currentEnv and hasattr(currentEnv, 'rob') and currentEnv.rob:
                    currentEnv.rob.sendCommand(f"chat {msg}")
                    return f"Chatted: {msg}"
                return "Chat Failed: Not connected"
            
        if actionName in actionMap:
            target_action = actionMap[actionName]
            return currentEnv.executeAction(target_action)
        
        return f"Unknown Action {actionName}"


            
    except Exception as e:
        return f"Error executing {actionName}: {e}"

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

def sortEntities(*args) -> list:
    if not args:
        return []
    data = list(args[0]) if len(args) == 1 and isinstance(args[0], (list, tuple)) else list(args)
    
    try:
        return sorted(data, key=lambda e: float(e[-1]) if isinstance(e, (list, tuple)) and len(e) > 0 else 0)
    except Exception as e:
        print(f"Error sorting entities in Python: {e}")
        return data


