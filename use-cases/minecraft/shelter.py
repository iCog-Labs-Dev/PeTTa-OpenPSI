import math
import time

SHELTER_RADIUS = 4
SHELTER_HEIGHT = 3
SHELTER_MATERIAL = "oak_planks"


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

    doorway = (door_x, base_y, door_z)
    # Outside and inside pressure plates for reliable automatic door opening.
    outside_button = (door_x, base_y, door_z - 1)
    inside_pressure_plate = (door_x, base_y, door_z + 1)

    return floor, walls, roof, torches, doorway, outside_button, inside_pressure_plate


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


def setShelterState(env, base_x: int, base_y: int, base_z: int, doorway, outsideButton, insidePressurePlate):
    env.shelterState = {
        "center": (base_x, base_y, base_z),
        "doorway": doorway,
        "outsideButton": outsideButton,
        "insidePressurePlate": insidePressurePlate,
        # Move one block beyond the inside pressure plate for stable path targets.
        "insideTarget": (doorway[0], doorway[1], doorway[2] + 2),
        "outsideTarget": (doorway[0], doorway[1], doorway[2] - 2),
    }


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
        move_result = env.moveTo(float(target[0]), float(target[1]), float(target[2]))

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
    floor, walls, roof, torches, doorway, outsideButton, insidePressurePlate = shelterPlan(base_x, base_y, base_z)

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
    if not secureEntrance(env.mc, doorway, outsideButton, insidePressurePlate):
        return

    setShelterState(env, base_x, base_y, base_z, doorway, outsideButton, insidePressurePlate)
    return "Shelter Built"
