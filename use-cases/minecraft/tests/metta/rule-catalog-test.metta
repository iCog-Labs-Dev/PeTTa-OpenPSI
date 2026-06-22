!(import! &self ../../ts-algorithm)
!(import! &self ../../rules)

!(test (size-atom (collapse (get-atoms &ruleSpace))) 12)

!(test (getSTV 1 &ruleSpace) (0.95 0.9))
!(test (getAction 1 &ruleSpace) (SEQ_AND ((eatFood))))
!(test (getAction 10 &ruleSpace) (SEQ_AND ((findGround) (checkBreathing))))

!(test (getContextAtoms 1 &ruleSpace) ((isHungry (STV 1.0 0.95)) (hasEdibleFoodInInventory (STV 1.0 0.9))))

!(test (size-atom (matchGoal hasFood &ruleSpace)) 3)
!(test (matchGoal breathableAir &ruleSpace) (10))
