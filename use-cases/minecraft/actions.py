import time
from typing import Optional


def sendHoldCommand(env, onCommand: str, holdSeconds: float, offCommand: Optional[str] = None, delay: float = 0.5):
    env.rob.sendCommand(onCommand)
    time.sleep(holdSeconds)
    if offCommand:
        env.rob.sendCommand(offCommand)
    if delay > 0:
        time.sleep(delay)


def doMoveForward(env):
    sendHoldCommand(env, "move 1", 2, "move 0")
    return "Moved Forward"


def doTurnLeft(env):
    sendHoldCommand(env, "turn -0.5", 2, "turn 0")
    return "Turned Left"


def doTurnRight(env):
    sendHoldCommand(env, "turn 0.5", 2, "turn 0")
    return "Turned Right"


def doAttack(env):
    sendHoldCommand(env, "attack 1", 2, "attack 0")
    return "Attacked"


def doPlace(env):
    sendHoldCommand(env, "use 1", 2, "use 0")
    return "Placed"


def doUse(env):
    sendHoldCommand(env, "use 1", 10, "use 0")
    return "Used"


def doDig(env):
    sendHoldCommand(env, "attack 1", 2, "attack 0")
    return "Dug"


def doChat(env):
    env.rob.sendCommand("chat Hello")
    return "Chatted Hello"


def doCrouch(env):
    sendHoldCommand(env, "crouch 1", 2, "crouch 0")
    return "Crouched"


def doJump(env):
    sendHoldCommand(env, "jump 1", 2, "jump 0")
    return "Jumped"


def doDrop(env):
    env.rob.sendCommand("discardCurrentItem")
    return "Dropped Item"
