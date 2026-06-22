; Standalone tests for utils.metta goal selection and context predicates.
; The fake &perceptionSpace below represents one risky survival state.
!(import! &self ../../perception)
!(import! &self ../../utils)

; Risky snapshot: hungry, low health, night, low air, airborne, food present,
; hostile nearby, and edible food nearby.
!(add-atom &perceptionSpace (hunger 7.0))
!(add-atom &perceptionSpace (health 9.0))
!(add-atom &perceptionSpace (isDay False))
!(add-atom &perceptionSpace (air 150.0))
!(add-atom &perceptionSpace (onGround False))
!(add-atom &perceptionSpace (hasItem bread 1))
!(add-atom &perceptionSpace (nearEntity zombie 4.0 2 64 2))
!(add-atom &perceptionSpace (nearEntity apple 3.0 3 64 2))

; Demand names should map to the goals used by the Minecraft planner.
!(test (minecraftGoalSelector hunger) (Goal hasFood 1.0 0.9))
!(test (minecraftGoalSelector energy) (Goal healthIncreasing 1.0 0.9))
!(test (minecraftGoalSelector breath) (Goal breathableAir 1.0 0.95))
!(test (minecraftGoalSelector curiosity) (Goal Explore 1.0 0.5))

; Context atoms may appear bare or paired with STV metadata.
!(test (contextAtomName (isHungry (STV 1.0 0.95))) isHungry)
!(test (contextAtomName lowAir) lowAir)

; Current-state predicates read from &perceptionSpace only.
!(test (isHungryNow) True)
!(test (isLowHealthNow) True)
!(test (isSafeHealthNow) False)
!(test (isDayNow) False)
!(test (isNightNow) True)
!(test (hasHostileNearbyNow) True)
!(test (hasEdibleFoodNow) True)
!(test (hasFoodNearbyNow) True)
!(test (isCuriosityHighNow) True)
!(test (airNow) 150.0)
!(test (isLowAirNow) True)
!(test (onGroundNow) False)

; evalContextPredicate maps rule DSL names to the current-state predicates.
!(test (evalContextPredicate isHungry) True)
!(test (evalContextPredicate noHostilesNearby) False)
!(test (evalContextPredicate safeAir) False)
!(test (evalContextPredicate unknownContext) False)

; A rule context is applicable only when every required context atom is true.
!(test (isContextApplicable ((isHungry (STV 1.0 0.95)) (lowAir (STV 1.0 0.98)))) True)
!(test (isContextApplicable ((safeHealth (STV 1.0 0.85)))) False)
