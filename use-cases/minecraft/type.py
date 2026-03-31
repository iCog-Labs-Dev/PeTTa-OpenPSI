from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any, Tuple, Optional

class ActionType(Enum):
    MOVE_FORWARD = auto()
    MOVE_BACKWARD = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    JUMP = auto()
    ATTACK = auto()
    EAT = auto()
    PLACE = auto()
    DIG = auto()
    CHAT = auto()
    USE = auto()
    CROUCH = auto()
    DROP = auto()
    MOVE_TO = auto()
    BUILD_SHELTER = auto()
    SEEK_SHELTER = auto()
    ENTER_SHELTER = auto()
    FIND_GROUND = auto()
    SLEEP_AT_NIGHT = auto()


@dataclass
class Observation:
    position: Tuple[float, float, float]
    yaw: float
    pitch: float
    health: float
    hunger: float
    isDay: bool
    timeOfDay: int
    inventory: List[Dict[str, Any]]
    nearbyEntities: List[Dict[str, Any]]
    nearbyBlocks: List[Dict[str, Any]]
    
    lineOfSight: Optional[Dict[str, Any]] = None
    air: Optional[float] = None
    onGround: Optional[bool] = None
    actionStatus: Optional[str] = None
    lineOfSightType: Optional[str] = None
    lineOfSightDistance: Optional[float] = None
    lineOfSightHitType: Optional[str] = None
