import math

from type import Observation


def getDefaultObservation() -> Observation:
    return Observation(
        (0, 0, 0),0,0,0,0.0,False,0,[],[],[],air=300.0,
        onGround=True,actionStatus="unknown",
    )


def buildObservation(env) -> Observation:
    if not env.connected or not env.rob:
        return getDefaultObservation()

    env.rob.observeProcCached()

    pos = env.rob.getCachedObserve("getAgentPos")  # [x, y, z, pitch, yaw]
    if pos:
        p = (pos[0], pos[1], pos[2])
        y = pos[4]
        pitch = pos[3]
    else:
        p = (0.0, 64.0, 0.0)
        y = 0.0
        pitch = 0.0

    life = env.rob.getCachedObserve("getLife") or 20.0

    food = env.mc.getFullStat("Food")
    food = float(food) if food is not None else 20.0

    air = env.rob.getCachedObserve("getAir")
    air = float(air) if air is not None else 300.0

    on_ground = env.rob.getCachedObserve("getOnGround")
    if on_ground is None:
        on_ground = True

    action_status = env.mc.getActionStatus()
    if action_status is None:
        action_status = "unknown"

    worldTime = env.mc.getFullStat("WorldTime")
    worldStart = int(env.mission.serverSection.initial_conditions.time_start or 0)
    if worldTime is not None:
        worldTime = int(worldTime)
        timeOffset = int(getattr(env, "timeAddOffset", 0))
        dayTime = worldTime + worldStart + timeOffset
        timeMod = dayTime % 24000
        isNight = 13000 <= timeMod < 23000
        is_day = not isNight
        timeValue = dayTime
    else:
        timeValue = 6000
        is_day = True

    ents = env.rob.getCachedObserve("getNearEntities") or []
    parsedEnts = []
    for e in ents:
        ex, ey, ez = e.get("x", 0), e.get("y", 0), e.get("z", 0)
        dist = math.sqrt((ex - p[0]) ** 2 + (ey - p[1]) ** 2 + (ez - p[2]) ** 2)
        parsedEnts.append(
            {
                "type": e.get("name", "unknown").lower(),
                "distance": dist,
                "position": [ex, ey, ez],
            }
        )

    rawInventory = env.rob.getCachedObserve("getInventory")
    inv = []
    if rawInventory and isinstance(rawInventory, list):
        for item in rawInventory:
            inv.append(
                {
                    "item": item.get("type", "unknown"),
                    "count": item.get("quantity", 1),
                }
            )

    blocks = []

    line_of_sight = env.rob.getCachedObserve("getLineOfSights")
    line_of_sight_type = None
    line_of_sight_distance = None
    line_of_sight_hit_type = None
    if isinstance(line_of_sight, dict):
        line_of_sight_type = line_of_sight.get("type")
        line_of_sight_distance = line_of_sight.get("distance")
        line_of_sight_hit_type = line_of_sight.get("hitType")

    return Observation(
        position=p,
        yaw=y,
        pitch=pitch,
        health=life,
        hunger=food,
        isDay=is_day,
        timeOfDay=timeValue,
        inventory=inv,
        nearbyEntities=parsedEnts,
        nearbyBlocks=blocks,
        lineOfSight=line_of_sight,
        air=air,
        onGround=on_ground,
        actionStatus=action_status,
        lineOfSightType=line_of_sight_type,
        lineOfSightDistance=line_of_sight_distance,
        lineOfSightHitType=line_of_sight_hit_type,
    )
