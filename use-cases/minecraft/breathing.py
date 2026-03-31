import math
import time


WATER_BLOCKS = {"water", "flowing_water", "bubble_column"}
AIR_BLOCKS = {"air", "cave_air", "void_air"}
COMMON_PASSABLE = {
    "short_grass", "tall_grass", "seagrass", "tall_seagrass",
    "kelp", "kelp_plant", "sugar_cane", "fern", "large_fern",
    "snow", "vine", "lily_pad", "dead_bush", "dandelion", "poppy",
    "brown_mushroom", "red_mushroom", "sugar_cane",
}

UNSAFE_SUPPORT_BLOCKS = {
    "cactus",
    "magma_block",
    "lava",
    "flowing_lava",
    "fire",
    "soul_fire",
    "sweet_berry_bush",
}


def normalizeBlock(name):
    text = str(name or "").lower().replace("minecraft:", "")
    return text.split("[", 1)[0]


def isWater(name):
    return normalizeBlock(name) in WATER_BLOCKS


def stopMotion(env):
    env.rob.sendCommand("move 0")
    env.rob.sendCommand("turn 0")
    env.rob.sendCommand("jump 0")
    env.rob.sendCommand("pitch 0")


def getGrid3D(env):
    rawGrid = env.rob.getCachedObserve("getNearGrid")
    if not rawGrid:
        return None

    bounds = env.grid_bounds
    dimX = bounds[0][1] - bounds[0][0] + 1
    dimY = bounds[1][1] - bounds[1][0] + 1
    dimZ = bounds[2][1] - bounds[2][0] + 1
    if len(rawGrid) != dimX * dimY * dimZ:
        return None

    grid3D = []
    idx = 0
    for _ in range(dimY):
        layer = []
        for _ in range(dimZ):
            row = []
            for _ in range(dimX):
                row.append(rawGrid[idx])
                idx += 1
            layer.append(row)
        grid3D.append(layer)
    return grid3D


def getState(env):
    env.rob.observeProcCached()
    pos = env.rob.getCachedObserve("getAgentPos")
    onGround = bool(env.rob.getCachedObserve("getOnGround"))
    air = env.rob.getCachedObserve("getAir")
    air = float(air) if air is not None else None

    grid = getGrid3D(env)
    if not grid:
        return {
            "pos": pos,
            "onGround": onGround,
            "air": air,
            "feetWater": True,
            "headWater": True,
            "dryStable": False,
            "dryVisible": False,
            "grid": None,
        }

    dimY = len(grid)
    dimZ = len(grid[0])
    dimX = len(grid[0][0])
    cx, cy, cz = dimX // 2, dimY // 2, dimZ // 2
    feet = normalizeBlock(grid[cy][cz][cx])
    head = normalizeBlock(grid[min(cy + 1, dimY - 1)][cz][cx])
    below = normalizeBlock(grid[max(cy - 1, 0)][cz][cx])

    feetWater = isWater(feet)
    headWater = isWater(head)
    dryVisible = (not feetWater) and (not headWater)
    dryStable = dryVisible and (below not in AIR_BLOCKS) and (not isWater(below))
    return {
        "pos": pos,
        "onGround": onGround,
        "air": air,
        "feetWater": feetWater,
        "headWater": headWater,
        "dryStable": dryStable,
        "dryVisible": dryVisible,
        "grid": grid,
    }


def isPassableBlock(name, passableSet):
    return name in passableSet or isWater(name)


def classifyExitCell(feet, head, below, passableSet):
    feetWater = isWater(feet)
    if below in AIR_BLOCKS or below in passableSet or isWater(below) or below in UNSAFE_SUPPORT_BLOCKS:
        return None
    
    if feet in AIR_BLOCKS and head in AIR_BLOCKS:
        return "dry_land"
    
    if feetWater and head in AIR_BLOCKS:
        return "shallow_edge"
    return None


def pickExitTarget(env, grid, preferDry=True):
    if not grid:
        return None

    dimY = len(grid)
    dimZ = len(grid[0])
    dimX = len(grid[0][0])
    cx, cy, cz = dimX // 2, dimY // 2, dimZ // 2
    maxRadius = max(1, min((dimX // 2) - 1, (dimZ // 2) - 1, 20))
    yOffsets = [1, 0, -1]

    passableSet = {normalizeBlock(b) for b in getattr(env.rob, "passableBlocks", [])}
    if not passableSet:
        passableSet = set(AIR_BLOCKS) | {"water", "flowing_water"} | COMMON_PASSABLE

    best = None
    for radius in range(1, maxRadius + 1):
        for dz in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if max(abs(dx), abs(dz)) != radius:
                    continue
                gx = cx + dx
                gz = cz + dz
                if gx < 0 or gx >= dimX or gz < 0 or gz >= dimZ:
                    continue

                for yOff in yOffsets:
                    gy = cy + yOff
                    if gy - 1 < 0 or gy + 1 >= dimY:
                        continue
                    feet = normalizeBlock(grid[gy][gz][gx])
                    head = normalizeBlock(grid[gy + 1][gz][gx])
                    below = normalizeBlock(grid[gy - 1][gz][gx])
                    kind = classifyExitCell(feet, head, below, passableSet)
                    if kind is None:
                        continue
                    if preferDry and kind != "dry_land":
                        continue
                    rank = 0 if kind == "dry_land" else 1
                    yPenalty = 0 if yOff >= 0 else 1
                    score = (rank, abs(dx) + abs(dz), yPenalty, abs(yOff))
                    if best is None or score < best[0]:
                        best = (score, dx, dz, kind, yOff)
        if best is not None and best[0][0] == 0:
            break

    if best is None:
        return None
    return best[1], best[2], best[3], best[4]


def buildWorldTarget(pos, dx, yOff, dz):
    return (
        math.floor(pos[0]) + dx + 0.5,
        math.floor(pos[1]) + yOff,
        math.floor(pos[2]) + dz + 0.5,
    )


def aimToWorldTarget(env, target):
    pos = env.rob.getCachedObserve("getAgentPos")
    if not pos:
        return None
    dx = float(target[0]) - float(pos[0])
    dz = float(target[2]) - float(pos[2])
    dist = math.hypot(dx, dz)
    currYaw = float(pos[4])
    targetYaw = math.degrees(math.atan2(-dx, dz))
    yawDiff = (targetYaw - currYaw + 180.0) % 360.0 - 180.0
    if abs(yawDiff) < 8.0:
        turnSpeed = 0.0
    else:
        turnSpeed = max(0.22, min(abs(yawDiff) / 45.0, 1.0))
        if yawDiff < 0:
            turnSpeed *= -1
    env.rob.sendCommand(f"turn {turnSpeed}")
    return dist, abs(yawDiff), float(target[1]) - float(pos[1])


def isLanded(state):
    return (
        (not state["feetWater"]) and
        (not state["headWater"]) and
        state["onGround"] and
        state["dryStable"]
    )


def confirmGroundReached(env, samples=6, required=4, requireDry=True):
    stopMotion(env)
    ok = 0
    for _ in range(samples):
        state = getState(env)
        stableNow = state["onGround"] or state["dryStable"]
        if (isLanded(state) if requireDry else stableNow):
            ok += 1
        time.sleep(0.08)
    return ok >= required


def findGroundWhileSwimming(env, timeoutSec=60.0):
    endTime = time.time() + timeoutSec
    landedStreak = 0
    targetLock = None
    targetLockTicks = 0
    prevPos = None
    noProgressTicks = 0
    lastTargetDist = None
    closeDryTicks = 0

    stopMotion(env)

    while time.time() < endTime:
        state = getState(env)
        pos = state["pos"]
        if pos is not None:
            if prevPos is not None:
                moved = math.hypot(float(pos[0]) - float(prevPos[0]), float(pos[2]) - float(prevPos[2]))
                noProgressTicks = 0 if moved > 0.03 else noProgressTicks + 1
            prevPos = pos

        if isLanded(state):
            landedStreak += 1
        else:
            landedStreak = 0

        if landedStreak >= 4:
            if confirmGroundReached(env, requireDry=True):
                stopMotion(env)
                return "Ground Reached"
            landedStreak = 0
            targetLock = None
            targetLockTicks = 0
            lastTargetDist = None
            closeDryTicks = 0

        preferDry = not state["headWater"]

        if noProgressTicks > 20:
            targetLock = None
            targetLockTicks = 0
            lastTargetDist = None
            closeDryTicks = 0
            env.rob.sendCommand("turn 0.55")
            env.rob.sendCommand("move 1")
            env.rob.sendCommand("jump 1")
            time.sleep(0.15)
            continue

        if targetLock is None or targetLockTicks <= 0:
            relTarget = pickExitTarget(env, state["grid"], preferDry=preferDry)
            if relTarget is None and preferDry:
                relTarget = pickExitTarget(env, state["grid"], preferDry=False)
            if relTarget is not None and pos is not None:
                dx, dz, kind, yOff = relTarget
                targetLock = buildWorldTarget(pos, dx, yOff, dz) + (kind,)
                targetLockTicks = 40 if kind == "dry_land" else 12
                noProgressTicks = 0
                lastTargetDist = None
                closeDryTicks = 0
            else:
                targetLock = None
                targetLockTicks = 0
                lastTargetDist = None
                closeDryTicks = 0
        else:
            targetLockTicks -= 1

        if targetLock is not None:
            tx, ty, tz, kind = targetLock
            aim = aimToWorldTarget(env, (tx, ty, tz))
            if aim is None:
                time.sleep(0.1)
                continue
            dist, yawAbs, dy = aim
            dryNow = (not state["feetWater"]) and (not state["headWater"])
            if lastTargetDist is not None and dist >= lastTargetDist - 0.02:
                targetLockTicks -= 2
            lastTargetDist = dist

            if kind == "dry_land" and dist < 1.2 and not isLanded(state):
                closeDryTicks += 1
            else:
                closeDryTicks = 0

            if kind == "dry_land" and dryNow and dist < 0.9:
                env.rob.sendCommand("move 0.2" if yawAbs <= 25 else "0")
                env.rob.sendCommand("jump 0")
                env.rob.sendCommand("turn 0")
                time.sleep(0.15)
                if confirmGroundReached(env, samples=4, required=2, requireDry=True):
                    stopMotion(env)
                    return "Ground Reached"

            moveSpeed = "0.3" if yawAbs > 50 else "1"
            env.rob.sendCommand(f"move {moveSpeed}")
            if state["headWater"] or state["feetWater"]:
                env.rob.sendCommand("jump 1")
            elif dy > 0.6 and dist > 0.8:
                env.rob.sendCommand("jump 1")
            elif kind != "dry_land" and not isLanded(state):
                env.rob.sendCommand("jump 1")
            else:
                env.rob.sendCommand("jump 0")

            if kind == "dry_land" and isLanded(state):
                targetLockTicks = 0
            elif kind != "dry_land" and dist < 0.35:
                targetLockTicks = 0
            elif kind == "dry_land" and closeDryTicks >= 20:
                targetLock = None
                targetLockTicks = 0
                lastTargetDist = None
                closeDryTicks = 0
                noProgressTicks = 0
        else:
            lastTargetDist = None
            closeDryTicks = 0
            env.rob.sendCommand("turn 0.35")
            if state["headWater"]:
                env.rob.sendCommand("move 0")
                env.rob.sendCommand("jump 1")
            else:
                env.rob.sendCommand("move 0.6")
                env.rob.sendCommand("jump 1")
        time.sleep(0.1)

    stopMotion(env)
    return []
