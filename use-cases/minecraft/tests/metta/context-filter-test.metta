; Standalone tests for context filtering across utils.metta and ts-algorithm.metta.
; This checks the bridge from current perception state to applicable rule IDs.
!(import! &self ../../perception)
!(import! &self ../../utils)
!(import! &self ../../ts-algorithm)

; Start with no air/onGround atoms to verify default safety assumptions.
!(test (airNow) 300.0)
!(test (onGroundNow) True)
!(test (isLowAirNow) False)

; A stable daytime state should choose proactive shelter preparation for safety.
!(add-atom &perceptionSpace (isDay True))
!(add-atom &perceptionSpace (air 250.0))
!(add-atom &perceptionSpace (hunger 14.0))
!(add-atom &perceptionSpace (health 16.0))
!(test (minecraftGoalSelector safety) (Goal shelterPrepared 1.0 0.85))

; Custom rule atoms let us test context filtering without importing live rule actions.
!(add-atom &contextRuleSpace (: Rule 101
   (TTV 0)
   (STV 0.9 0.8)
   (Complexity 1)
   (IMPLICATION
      (AND
         (Context (STV 1.0 1.0) (AND (
            (isDayTime (STV 1.0 1.0))
            (safeAir (STV 1.0 0.9))
            (safeHealth (STV 1.0 0.85))
         )))
         (Action (SEQ_AND ((scanEnvironment))))
      )
      (Goal (STV 1.0 0.9) (AND ((Explore (STV 1.0 1.0)))))
   )
))

!(add-atom &contextRuleSpace (: Rule 102
   (TTV 0)
   (STV 0.9 0.8)
   (Complexity 1)
   (IMPLICATION
      (AND
         (Context (STV 1.0 1.0) (AND (
            (lowAir (STV 1.0 0.98))
         )))
         (Action (SEQ_AND ((findGround))))
      )
      (Goal (STV 1.0 0.9) (AND ((breathableAir (STV 1.0 1.0)))))
   )
))

!(test (filterRulesByContext (101 102) &contextRuleSpace) (101))
