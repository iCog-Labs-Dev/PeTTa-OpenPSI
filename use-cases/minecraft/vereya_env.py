import time
import math
from typing import List, Dict, Any, Optional, Callable

from type import ActionType, Observation
from navigation import Navigation
import actions as actionOps
import inventory as inventoryOps
import observation as observationOps
import shelter as shelterOps

try:
    import tagilmo.utils.mission_builder as mb
    from tagilmo.utils.vereya_wrapper import MCConnector, RobustObserver
    VEREYA_AVAILABLE = True
except ImportError:
    VEREYA_AVAILABLE = False


class VereyaEnvironment:
    def __init__(self):
        if not VEREYA_AVAILABLE:
            raise ImportError("Vereya modules not found")
            
        self.connected = False
        self.mc: Optional[MCConnector] = None
        self.rob: Optional[RobustObserver] = None
        
        self.grid_bounds = [[-20, 20], [-2, 2], [-20, 20]]
        self.obs = mb.Observations(bAll=True)
        self.obs.gridNear = self.grid_bounds
        
        self.agentHandlers = mb.AgentHandlers(observations=self.obs)
        
        self.agentSection = mb.AgentSection(name='OpenPsiAgent', agenthandlers=self.agentHandlers)
        self.mission = mb.MissionXML(agentSections=[self.agentSection])
        self.mission.serverSection.initial_conditions.allowedmobs = "Pig Sheep Cow Chicken Ozelot Rabbit Villager Zombie Skeleton"
        
        self.mission.setWorld(mb.defaultworld(seed='12347', forceReset=False))
        self.actionHandlers = {
            ActionType.MOVE_FORWARD: self.doMoveForward,
            ActionType.TURN_LEFT: self.doTurnLeft,
            ActionType.TURN_RIGHT: self.doTurnRight,
            ActionType.EAT: self.eatFromInventory,
            ActionType.ATTACK: self.doAttack,
            ActionType.PLACE: self.doPlace,
            ActionType.USE: self.doUse,
            ActionType.DIG: self.doDig,
            ActionType.CHAT: self.doChat,
            ActionType.CROUCH: self.doCrouch,
            ActionType.JUMP: self.doJump,
            ActionType.DROP: self.doDrop,
            ActionType.BUILD_SHELTER: self.doBuildShelter,
            ActionType.SEEK_SHELTER: self.doSeekShelter,
            ActionType.ENTER_SHELTER: self.doEnterShelter,
        }

    def sendHoldCommand(self, onCommand: str, holdSeconds: float, offCommand: Optional[str] = None, settleSeconds: float = 0.0):
        actionOps.sendHoldCommand(self, onCommand, holdSeconds, offCommand, settleSeconds)

    def connect(self):
        print("Connecting to REAL Minecraft via Vereya ...")
        try:
            # clientIp should be of the host machine running Minecraft, adjust based on that
            self.mc = MCConnector(self.mission, clientIp='172.19.176.1') 
            self.rob = RobustObserver(self.mc)
            self.mc.safeStart()
                
            print("Mission accepted. Waiting for spawn...")
            time.sleep(2)
            self.connected = True

            # The following commands are for testing purposes only
            # to ensure the agent has food and can eat.
            # Remove manual inteventions for a more naturalistic environment.
            self.mc.sendCommand("chat /give @p apple 2")
            time.sleep(1)
            
            self.mc.sendCommand("chat /give @p bread 2")
            time.sleep(1)
            
            self.mc.sendCommand("chat /give @p glow_berries 2")
            time.sleep(1)
            
            self.mc.sendCommand("chat /effect give @p minecraft:hunger 10 50 true")
            time.sleep(1)

            return True
        except Exception as e:
            print(f"Failed to connect to Vereya: {e}")
        return False
            
    def disconnect(self):
        self.connected = False
        print("Vereya environment disconnected.")

    def getCurrentItemIndex(self):
        return inventoryOps.getCurrentItemIndex(self)

    def findEdibleInventoryItem(self, inventory):
        return inventoryOps.findEdibleInventoryItem(inventory)

    def eatFromInventory(self):
        return inventoryOps.eatFromInventory(self)

    def getObservation(self) -> Observation:
        return observationOps.buildObservation(self)

    def executeAction(self, actionType: ActionType):
        if not self.connected:
            print("Not connected to Vereya environment.")
            return []

        handler = self.actionHandlers.get(actionType)
        if handler is not None:
            return handler()
        
        print(f"Unknown action type: {actionType}")
        return []

    def doMoveForward(self):
        return actionOps.doMoveForward(self)

    def doTurnLeft(self):
        return actionOps.doTurnLeft(self)

    def doTurnRight(self):
        return actionOps.doTurnRight(self)

    def doAttack(self):
        return actionOps.doAttack(self)

    def doPlace(self):
        return actionOps.doPlace(self)

    def doUse(self):
        return actionOps.doUse(self)

    def doDig(self):
        return actionOps.doDig(self)

    def doChat(self):
        return actionOps.doChat(self)

    def doCrouch(self):
        return actionOps.doCrouch(self)

    def doJump(self):
        return actionOps.doJump(self)

    def doDrop(self):
        return actionOps.doDrop(self)

    def doBuildShelter(self):
        return shelterOps.buildShelter(self)

    def doSeekShelter(self):
        return shelterOps.seekShelter(self)

    def doEnterShelter(self):
        return shelterOps.enterShelter(self)

    def moveTo(self, target_x, target_y, target_z):
        if not self.connected or not self.rob:
            print("Not connected to Vereya environment.")
            return []

        self.rob.observeProcCached()
        initialPos = self.rob.getCachedObserve('getAgentPos')
        print(f"current position: {initialPos}")


        
        rawGrid = self.rob.getCachedObserve('getNearGrid')
        
        if not initialPos or not rawGrid:
            print("Failed to get initial position or grid data")
            return []

        gridMap = Navigation.parseGrid(rawGrid, self.grid_bounds)
        goal_rel = (
            int(math.floor(target_x) - math.floor(initialPos[0])),
            int(math.floor(target_y) - math.floor(initialPos[1])),
            int(math.floor(target_z) - math.floor(initialPos[2]))
        )
        
        goal_rel = (
            max(self.grid_bounds[0][0], min(self.grid_bounds[0][1], goal_rel[0])),
            max(self.grid_bounds[1][0], min(self.grid_bounds[1][1], goal_rel[1])),
            max(self.grid_bounds[2][0], min(self.grid_bounds[2][1], goal_rel[2]))
        )

        path = Navigation.aStar((0, 0, 0), goal_rel, gridMap)
        if not path:
            print("No path found to target!")
            return []

        print(f"Executing path: {path}")
        
        for rel_step in path:
            abs_target = (
                math.floor(initialPos[0]) + rel_step[0] + 0.5,
                math.floor(initialPos[1]) + rel_step[1],
                math.floor(initialPos[2]) + rel_step[2] + 0.5
            )
            
            last_dist = 999
            stuck_ticks = 0
            
            while True:
                self.rob.observeProcCached()
                curr = self.rob.getCachedObserve('getAgentPos')
                if not curr: break
                
                dx = abs_target[0] - curr[0]
                dy = abs_target[1] - curr[1]
                dz = abs_target[2] - curr[2]
                dist_h = math.sqrt(dx*dx + dz*dz)
                
                if dist_h < 0.35 and abs(dy) < 1.0:
                    break
                
                if abs(dist_h - last_dist) < 0.01:
                    stuck_ticks += 1
                else:
                    stuck_ticks = 0
                last_dist = dist_h
                
                if stuck_ticks > 150:
                    print("Stuck! Attempting to ")
                    self.rob.sendCommand("jump 1")
                    self.rob.sendCommand("move -1")
                    time.sleep(0.2)
                    self.rob.sendCommand("move 1")
                    stuck_ticks = 0

                if dy > 0.5:
                    self.rob.sendCommand("jump 1")
                else:
                    self.rob.sendCommand("jump 0")

                target_yaw = math.atan2(-dx, dz) * 180 / math.pi
                curr_yaw = curr[4]
                yaw_diff = (target_yaw - curr_yaw + 180) % 360 - 180
                
                turn_speed = 0
                if abs(yaw_diff) > 10:
                    turn_speed = max(0.3, min(abs(yaw_diff) / 45.0, 1.0))
                    if yaw_diff < 0: 
                        turn_speed *= -1
                
                self.rob.sendCommand(f"turn {turn_speed}")

                if abs(yaw_diff) > 45:
                    self.rob.sendCommand("move 0.2")
                else:
                    self.rob.sendCommand("move 1")
                
                time.sleep(0.05)
        
        self.rob.sendCommand("move 0")
        self.rob.sendCommand("turn 0")
        self.rob.sendCommand("jump 0")
        return "Reached Destination"

