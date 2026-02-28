import time
import math
from typing import List, Dict, Any, Optional

from type import ActionType, Observation
from navigation import Navigation


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
        
        self.grid_bounds = [[-10, 10], [-2, 3], [-10, 10]]
        self.obs = mb.Observations(bAll=True)
        self.obs.gridNear = self.grid_bounds
        
        self.agentHandlers = mb.AgentHandlers(observations=self.obs)
        
        self.agentSection = mb.AgentSection(name='PythonPlayer', agenthandlers=self.agentHandlers)
        self.mission = mb.MissionXML(agentSections=[self.agentSection])
        self.mission.serverSection.initial_conditions.allowedmobs = "Pig Sheep Cow Zombie Skeleton"
        
        self.mission.setWorld(mb.defaultworld(seed='12345'))

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
            return True
        except Exception as e:
            print(f"Failed to connect to Vereya: {e}")
        return False
            
    def disconnect(self):
        self.connected = False
        print("Vereya environment disconnected.")

    def getObservation(self) -> Observation:
        if not self.connected or not self.rob:
            return Observation((0,0,0), 0, 0, 0, 0.0, False, 0, [], [], [], air=300.0, onGround=True, actionStatus="unknown")
        
        self.rob.observeProcCached() 
        
        # Position
        pos = self.rob.getCachedObserve('getAgentPos') # [x, y, z, pitch, yaw]
        if pos:
            p = (pos[0], pos[1], pos[2])
            y = pos[4]
            pitch = pos[3]
        else:
             p = (0.0, 64.0, 0.0)
             y = 0.0
             pitch = 0.0

        # Vital Stats
        life = self.rob.getCachedObserve('getLife') or 20.0

        food = self.mc.getFullStat('Food')
        food = float(food) if food is not None else 20.0

        air = self.rob.getCachedObserve('getAir')
        air = float(air) if air is not None else 300.0

        on_ground = self.rob.getCachedObserve('getOnGround')
        if on_ground is None:
            on_ground = True

        action_status = self.mc.getActionStatus()
        # print(f"Action Status: {action_status}")
        if action_status is None:
            action_status = "unknown"
        
        
        worldTime = self.mc.getFullStat('WorldTime')
        if worldTime is not None:
            worldTime = int(worldTime)
            # Day is roughly 0-12000, Night 12000-24000
            timeMod = worldTime % 24000
            is_day = timeMod < 12000
        else:
            worldTime = 6000
            is_day = True
            
        # Entities
        ents = self.rob.getCachedObserve('getNearEntities') or []
        parsedEnts = []
        for e in ents:
            ex, ey, ez = e.get('x', 0), e.get('y', 0), e.get('z', 0)
            dist = math.sqrt((ex-p[0])**2 + (ey-p[1])**2 + (ez-p[2])**2)
            parsedEnts.append({
                'type': e.get('name', 'unknown').lower(), 
                'distance': dist,
                'position': [ex, ey, ez]
            })

        rawInventory = self.rob.getCachedObserve('getInventory')
        inv = []
        if rawInventory:
            if isinstance(rawInventory, list):
                for item in rawInventory:
                    inv.append({
                        'item': item.get('type', 'unknown'),
                        'count': item.get('quantity', 1)
                    })
                    
        blocks = [] 
        
        line_of_sight = self.rob.getCachedObserve("getLineOfSights")
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
            timeOfDay=worldTime, 
            inventory=inv,
            nearbyEntities=parsedEnts,
            nearbyBlocks=blocks,
            lineOfSight=line_of_sight,
            air=air,
            onGround=on_ground,
            actionStatus=action_status,
            lineOfSightType=line_of_sight_type,
            lineOfSightDistance=line_of_sight_distance,
            lineOfSightHitType=line_of_sight_hit_type
        )

    def executeAction(self, actionType: ActionType) -> str:
        if not self.connected:
            return "Not Connected"

        if actionType == ActionType.MOVE_FORWARD:
            self.rob.sendCommand('move 1')
            time.sleep(5) 
            self.rob.sendCommand('move 0')
            return "Moved Forward"
            
        elif actionType == ActionType.TURN_LEFT:
            self.rob.sendCommand('turn -0.5')
            time.sleep(0.2) 
            self.rob.sendCommand('turn 0')
            return "Turned Left"
            
        elif actionType == ActionType.TURN_RIGHT:
            self.rob.sendCommand('turn 0.5')
            time.sleep(0.2)
            self.rob.sendCommand('turn 0')
            return "Turned Right"
            
        elif actionType == ActionType.EAT:
            self.rob.sendCommand('use 1')
            time.sleep(1)
            self.rob.sendCommand('use 0')
            return "Ate"
            
        elif actionType == ActionType.ATTACK:
            self.rob.sendCommand('attack 1')
            time.sleep(0.5)
            self.rob.sendCommand('attack 0')
            return "Attacked"
            
        elif actionType == ActionType.PLACE:
            self.rob.sendCommand('use 1')
            time.sleep(0.2)
            self.rob.sendCommand('use 0')
            return "Placed"

        elif actionType == ActionType.USE:
            self.rob.sendCommand('use 1')
            time.sleep(10)
            self.rob.sendCommand('use 0')
            return "Used"
            
        elif actionType == ActionType.DIG:
            self.rob.sendCommand('attack 1')
            time.sleep(0.1)
            self.rob.sendCommand('attack 0')
            return "Dug"

        elif actionType == ActionType.CHAT:
            self.rob.sendCommand('chat Hello')
            return "Chatted Hello"
            
        elif actionType == ActionType.CROUCH:
            self.rob.sendCommand('crouch 1')
            time.sleep(10)
            self.rob.sendCommand('crouch 0')
            return "Crouched"
        
        elif actionType == ActionType.JUMP:
            self.rob.sendCommand('jump 1')
            time.sleep(5)
            self.rob.sendCommand('jump 0')
            return "Jumped"
             
        elif actionType == ActionType.DROP:
            self.rob.sendCommand('discardCurrentItem')
            return "Dropped Item"
            
        return "Action Sent"

    def moveTo(self, target_x, target_y, target_z):
        if not self.connected or not self.rob:
            return "Not Connected"

        self.rob.observeProcCached()
        initialPos = self.rob.getCachedObserve('getAgentPos')
        print(f"current position: {initialPos}")


        
        rawGrid = self.rob.getCachedObserve('getNearGrid')
        
        if not initialPos or not rawGrid:
            return "Observations unavailable"

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
            return f"No path found to {goal_rel}"

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

