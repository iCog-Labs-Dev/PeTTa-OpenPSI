import time
import random
from typing import Any, Dict, List, Optional

from constants import EDIBLE_ITEMS


def getCurrentItemIndex(env) -> Optional[int]:
    if not env.mc:
        return None
    try:
        obs = env.mc.observe.get(env.mc.agentId, {}) or {}
        idx = obs.get("currentItemIndex", None)
        if idx is None:
            return None
        return int(idx)
    except Exception:
        return None


def findEdibleInventoryItem(inventory: List[Dict[str, Any]]):
    candidates = []
    for item in inventory:
        itype = str(item.get("type", "")).split(":")[-1].lower().strip()
        qty = int(item.get("quantity", 0) or 0)
        if itype in EDIBLE_ITEMS and qty > 0:
            candidates.append(item)

    if not candidates:
        return None

    for item in candidates:
        if int(item.get("index", 0)) == 0:
            return item

    return random.choice(candidates)


def eatFromInventory(env):
    if not env.connected or not env.rob or not env.mc:
        return

    env.rob.observeProcCached()
    inv = env.rob.waitNotNoneObserve("getInventory", updateReq=True, observeReq=True) or []
    if not inv:
        return

    target = findEdibleInventoryItem(inv)
    if target is None:
        return

    target_idx = int(target.get("index", 0))
    current_idx = getCurrentItemIndex(env)
    dst_idx = current_idx if (current_idx is not None and current_idx >= 0) else 0

    if target_idx != dst_idx:
        env.rob.sendCommand(f"swapInventoryItems {dst_idx} {target_idx}")
        time.sleep(1)

    food_before = env.mc.getFullStat("Food")

    env.rob.sendCommand("use 1")
    time.sleep(10.0)
    env.rob.sendCommand("use 0")
    time.sleep(0.4)

    food_after = env.mc.getFullStat("Food")
    print(f"Food before: {food_before}, Food after: {food_after}")

    if food_before is not None and food_after is not None and float(food_after) > float(food_before):
        return f"Ate ({target.get('type', 'food')})"

    return
