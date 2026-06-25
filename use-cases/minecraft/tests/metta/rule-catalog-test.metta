; Standalone tests for the Minecraft rule catalog and rule access helpers.
; This checks the symbolic policy shape without running the planner or actions.
!(import! &self ../../ts-algorithm)
!(import! &self ../../rules)

; rules.metta should load the expected catalog into &ruleSpace.
!(test (size-atom (collapse (get-atoms &ruleSpace))) 12)

; Planner helpers should expose stable fields from representative rules.
!(test (getSTV 1 &ruleSpace) (0.95 0.9))
!(test (getAction 1 &ruleSpace) (SEQ_AND ((eatFood))))
!(test (getAction 10 &ruleSpace) (SEQ_AND ((findGround) (checkBreathing))))

; Rule 1 protects the hunger path: hungry + edible inventory means eat.
!(test (getContextAtoms 1 &ruleSpace) ((isHungry (STV 1.0 0.95)) (hasEdibleFoodInInventory (STV 1.0 0.9))))

; Goal matching is the bridge from selected demand goal to candidate rule IDs.
!(test (size-atom (matchGoal hasFood &ruleSpace)) 3)
!(test (matchGoal breathableAir &ruleSpace) (10))
