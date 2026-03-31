import math
import time

SHELTER_RADIUS = 4
SHELTER_HEIGHT = 3
SHELTER_MATERIAL = "oak_planks"
HOSTILE_TYPES = {"zombie", "skeleton"}
SLEEP_INTERACT_RANGE = 4.5


def shelterPlan(base_x: int, base_y: int, base_z: int, r: int = SHELTER_RADIUS):
    floor = []
    walls = []
    roof = []
    torches = []

    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            floor.append((base_x + dx, base_y - 1, base_z + dz))

    door_x, door_z = base_x, base_z - r
    for y in range(base_y, base_y + SHELTER_HEIGHT):
        for dx in range(-r, r + 1):
            for dz in [-r, r]:
                x, z = base_x + dx, base_z + dz
                if x == door_x and z == door_z and y in [base_y, base_y + 1]:
                    continue
                walls.append((x, y, z))
        for dz in range(-r + 1, r):
            for dx in [-r, r]:
                walls.append((base_x + dx, y, base_z + dz))

    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            roof.append((base_x + dx, base_y + SHELTER_HEIGHT, base_z + dz))

    torches = [
        (base_x - (r - 1), base_y, base_z - (r - 1)),
        (base_x + (r - 1), base_y, base_z - (r - 1)),
        (base_x - (r - 1), base_y, base_z + (r - 1)),
        (base_x + (r - 1), base_y, base_z + (r - 1)),
    ]

    bed = [
        (base_x - (r - 1), base_y, base_z, "lime_bed[part=foot,facing=south,occupied=false]"),
        (base_x - (r - 1), base_y, base_z + 1, "lime_bed[part=head,facing=south,occupied=false]"),
    ]

    doorway = (door_x, base_y, door_z)
    # Outside and inside pressure plates for reliable automatic door opening.
    outside_button = (door_x, base_y, door_z - 1)
    inside_pressure_plate = (door_x, base_y, door_z + 1)

    return floor, walls, roof, torches, doorway, outside_button, inside_pressure_plate, bed


def placeBlock(mc, x: int, y: int, z: int, block_type: str) -> bool:
    cmd = f"placeBlock {x} {y} {z} minecraft:{block_type} replace"
    try:
        mc.sendCommand(cmd)
    except AssertionError:
        print("  !! placement rejected (mission not running)")
        return False
    time.sleep(0.05)
    return True


def secureEntrance(mc, doorway, outsideButton, insidePressurePlate):
    x, y, z = doorway
    lower_ok = placeBlock(mc, x, y, z, "iron_door[half=lower,facing=south,hinge=left,open=false,powered=false]")
    upper_ok = placeBlock(mc, x, y + 1, z, "iron_door[half=upper,facing=south,hinge=left,open=false,powered=false]")
    if not (lower_ok and upper_ok):
        if not placeBlock(mc, x, y, z, "iron_door"):
            return False

    bx, by, bz = outsideButton
    if not placeBlock(mc, bx, by, bz, "stone_pressure_plate"):
        print("Warning: outside stone_pressure_plate placement failed")

    px, py, pz = insidePressurePlate
    if not placeBlock(mc, px, py, pz, "stone_pressure_plate"):
        print("Warning: inside stone_pressure_plate placement failed")

    return True


def setShelterState(env, base_x: int, base_y: int, base_z: int, doorway, outsideButton, insidePressurePlate, bedFoot):
    bedAccessPoint = None
    if bedFoot is not None:
        bedAccessPoint = (bedFoot[0] + 1, bedFoot[1], bedFoot[2])

    env.shelterState = {
        "center": (base_x, base_y, base_z),
        "doorway": doorway,
        "outsideButton": outsideButton,
        "insidePressurePlate": insidePressurePlate,
        "bedFoot": bedFoot,
        "bedUseTarget": bedAccessPoint,
        "insideTarget": (doorway[0], doorway[1], doorway[2] + 2),
        "outsideTarget": (doorway[0], doorway[1], doorway[2] - 2),
    }

def _getObservation(env):
    if hasattr(env, "getObservation"):
        try:
            return env.getObservation()
        except Exception:
            pass
    return None


def _isNightObservation(obs) -> bool:
    if obs is None:
        return False
    return not bool(getattr(obs, "isDay", True))


def _hasNearbyHostileObservation(obs, max_distance: float = 10.0) -> bool:
    if obs is None:
        return False
    entities = getattr(obs, "nearbyEntities", []) or []
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_name = entity.get("type", entity.get("name", ""))
        if normalizeBlockName(entity_name) not in HOSTILE_TYPES:
            continue
        try:
            dist = float(entity.get("distance", 9999.0))
        except Exception:
            continue
        if dist <= max_distance:
            return True
    return False


def _getLineOfSightObservation(obs):
    if obs is None:
        return None
    los = getattr(obs, "lineOfSight", None)
    return los if isinstance(los, dict) else None


def isNightNow(env) -> bool:
    if not env.connected:
        return False
    obs = _getObservation(env)
    return _isNightObservation(obs)


def hasNearbyHostile(env, max_distance: float = 10.0) -> bool:
    if not env.connected:
        return False
    obs = _getObservation(env)
    return _hasNearbyHostileObservation(obs, max_distance)


def normalizeBlockName(name) -> str:
    return str(name or "").lower().replace("minecraft:", "").split("_")[-1]


def readLineOfSight(env):
    obs = _getObservation(env)
    return _getLineOfSightObservation(obs)


def isLookingAtBed(env) -> bool:
    obs = _getObservation(env)
    los = _getLineOfSightObservation(obs)
    if not los:
        return False
    
    hit_type = normalizeBlockName(los.get("type"))
    in_range = los.get("inRange", True)
    dist = los.get("distance")

    if not in_range:
        return False
    if dist is not None:
        try:
            if float(dist) > SLEEP_INTERACT_RANGE:
                return False
        except Exception:
            pass
    return ("bed" in hit_type)


def aimAtPoint(env, target_x: float, target_y: float, target_z: float, max_steps: int = 18):
    if not env.rob:
        return

    for _ in range(max_steps):
        env.rob.observeProcCached()
        pos = env.rob.getCachedObserve("getAgentPos")
        if not pos:
            break

        eye_x = float(pos[0])
        eye_y = float(pos[1]) + 1.62
        eye_z = float(pos[2])
        curr_pitch = float(pos[3])
        curr_yaw = float(pos[4])

        dx = target_x - eye_x
        dy = target_y - eye_y
        dz = target_z - eye_z
        horiz = max(0.001, math.hypot(dx, dz))

        target_yaw = math.degrees(math.atan2(-dx, dz))
        target_pitch = -math.degrees(math.atan2(dy, horiz))
        target_pitch = max(-89.0, min(89.0, target_pitch))

        yaw_diff = (target_yaw - curr_yaw + 180.0) % 360.0 - 180.0
        pitch_diff = target_pitch - curr_pitch

        if abs(yaw_diff) < 2.0 and abs(pitch_diff) < 2.0:
            break

        turn_speed = max(-1.0, min(1.0, yaw_diff / 40.0))
        pitch_speed = max(-1.0, min(1.0, pitch_diff / 35.0))
        env.rob.sendCommand(f"turn {turn_speed}")
        env.rob.sendCommand(f"pitch {pitch_speed}")
        time.sleep(0.08)

    env.rob.sendCommand("turn 0")
    env.rob.sendCommand("pitch 0")


def aimAtTarget(env, target_x: float, target_z: float):
    if not env.rob:
        return
    pos = env.rob.getCachedObserve("getAgentPos")
    if not pos:
        return
    dx = target_x - float(pos[0])
    dz = target_z - float(pos[2])
    target_yaw = math.degrees(math.atan2(-dx, dz))
    curr_yaw = float(pos[4])
    yaw_diff = (target_yaw - curr_yaw + 180.0) % 360.0 - 180.0
    turn_speed = max(-1.0, min(1.0, yaw_diff / 45.0))
    env.rob.sendCommand(f"turn {turn_speed}")
    time.sleep(0.2)
    env.rob.sendCommand("turn 0")


def hasShelter(env) -> bool:
    return bool(getattr(env, "shelterState", None))


def setDoorOpen(mc, doorway, is_open: bool):
    x, y, z = doorway
    flag = "true" if is_open else "false"
    lower = f"iron_door[half=lower,facing=south,hinge=left,open={flag},powered={flag}]"
    upper = f"iron_door[half=upper,facing=south,hinge=left,open={flag},powered={flag}]"
    placeBlock(mc, x, y, z, lower)
    placeBlock(mc, x, y + 1, z, upper)


def enterShelter(env):
    if not env.connected or not env.rob or not env.mc:
        return None
    if not hasShelter(env):
        return None

    state = env.shelterState
    doorway = state["doorway"]
    target = state["insideTarget"]

    # Open doorway, move inside, then close for safety.
    setDoorOpen(env.mc, doorway, True)
    move_result = None
    if hasattr(env, "moveTo"):
        move_result = env.moveTo(float(target[0]), float(target[1]), float(target[2]) + 2)

    time.sleep(0.2)

    entered = move_result == "Reached Destination"
    if entered:
        setDoorOpen(env.mc, doorway, False)
        return "Entered Shelter"

    return None


def seekShelter(env):
    if hasShelter(env):
        return enterShelter(env)
    return buildShelter(env)


def buildShelter(env):
    if not env.connected or not env.rob or not env.mc:
        return

    env.rob.observeProcCached()
    pos = env.rob.getCachedObserve("getAgentPos")
    if not pos:
        print("Cannot read agent position.")
        return
    
    yaw_deg = float(pos[4]) if len(pos) > 4 else 0.0
    yaw_rad = math.radians(yaw_deg)
    offset = SHELTER_RADIUS + 2
    fwd_x = -math.sin(yaw_rad)
    fwd_z = math.cos(yaw_rad)

    base_x = int(math.floor(pos[0] + fwd_x * offset))
    base_y = int(math.floor(pos[1]))
    base_z = int(math.floor(pos[2] + fwd_z * offset))
    floor, walls, roof, torches, doorway, outsideButton, insidePressurePlate, bed = shelterPlan(base_x, base_y, base_z)

    for x, y, z in floor:
        if not placeBlock(env.mc, x, y, z, SHELTER_MATERIAL):
            return
    for x, y, z in walls:
        if not placeBlock(env.mc, x, y, z, SHELTER_MATERIAL):
            return
    for x, y, z in roof:
        if not placeBlock(env.mc, x, y, z, SHELTER_MATERIAL):
            return
    for x, y, z in torches:
        if not placeBlock(env.mc, x, y, z, "torch"):
            return
    for x, y, z, block_type in bed:
        if not placeBlock(env.mc, x, y, z, block_type):
            return
    bed_foot = (bed[0][0], bed[0][1], bed[0][2])

    if not secureEntrance(env.mc, doorway, outsideButton, insidePressurePlate):
        return

    setShelterState(env, base_x, base_y, base_z, doorway, outsideButton, insidePressurePlate, bed_foot)
    return "Shelter Built"

def sleepAtNight(env):
    if not env.connected or not env.rob or not env.mc:
        return None
    if not hasShelter(env):
        return None

    obs = _getObservation(env)
    if not _isNightObservation(obs):
        return None
    if _hasNearbyHostileObservation(obs):
        return None

    state = env.shelterState
    bed_foot = state.get("bedFoot")
    if bed_foot is None:
        return None

    enterShelter(env)

    if not hasattr(env, "moveTo"):
        return None

    bed_location = state.get("bedUseTarget")
    if bed_location is None:
        bed_location = (bed_foot[0] + 1, bed_foot[1], bed_foot[2])

    if _hasNearbyHostileObservation(_getObservation(env)):
        return None

    move_result = env.moveTo(float(bed_location[0]), float(bed_location[1]), float(bed_location[2]))
    if move_result != "Reached Destination":
        return None

    env.rob.sendCommand("move 0")
    env.rob.sendCommand("jump 0")
    env.rob.sendCommand("turn 0")
    env.rob.sendCommand("pitch 0")
    time.sleep(0.1)

    bed_target = (
        float(bed_foot[0]) + 0.5,
        float(bed_foot[1]) + 0.6,
        float(bed_foot[2]) + 0.5,
    )
    aimAtPoint(env, bed_target[0], bed_target[1], bed_target[2])
    if not isLookingAtBed(env):
        return None

    env.rob.sendCommand("use 1")
    time.sleep(0.45)
    env.rob.sendCommand("use 0")

    time.sleep(5)

    if isLookingAtBed(env):
        env.rob.sendCommand("turn 0")
        env.rob.sendCommand("pitch 0")
        time.sleep(0.25)

    return "Slept in Shelter"
