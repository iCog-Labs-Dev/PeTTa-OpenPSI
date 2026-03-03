
(= (addMinecraftRules $space) (
  let $rules (superpose (

    ;; Rule 1: Eat immediately if edible food is already available
    (: Rule 1
        (TTV 0)
        (STV 0.95 0.9)
        (Complexity 4)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isHungry (STV 1.0 0.95))
                    (hasEdibleFoodInInventory (STV 1.0 0.9))
                )))
                (Action (SEQ_AND (
                    (eatFood)
                )))
            )
            (Goal (STV 1.0 0.95) (AND (
                (hasFood (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 2: Hunt nearby food animal when hungry and no edible inventory
    (: Rule 2
        (TTV 0)
        (STV 0.9 0.85)
        (Complexity 6)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isHungry (STV 1.0 0.95))
                    (foodAnimalNearby (STV 1.0 0.9))
                    (noEdibleFoodInInventory (STV 1.0 0.85))
                )))
                (Action (SEQ_AND (
                    (moveToFood)
                    (dig)
                    (collectFood)
                )))
            )
            (Goal (STV 1.0 0.9) (AND (
                (hasFood (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 3: Explore for food sources when hungry and none is available nearby
    (: Rule 3
        (TTV 0)
        (STV 0.85 0.8)
        (Complexity 5)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isHungry (STV 1.0 0.95))
                    (noEdibleFoodInInventory (STV 1.0 0.85))
                    (noFoodAnimalNearby (STV 1.0 0.8))
                )))
                (Action (SEQ_AND (
                    (searchForFood)
                    (wander)
                )))
            )
            (Goal (STV 1.0 0.85) (AND (
                (hasFood (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 4: Emergency escape at night when hostile entities are close
    (: Rule 4
        (TTV 0)
        (STV 0.95 0.9)
        (Complexity 6)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isNightTime (STV 1.0 1.0))
                    (hostileNearby (STV 1.0 0.95))
                    (lowHealth (STV 1.0 0.9))
                )))
                (Action (SEQ_AND (
                    (turnAwayFromThreat)
                    (sprintForward)
                    (findCover)
                )))
            )
            (Goal (STV 1.0 0.95) (AND (
                (shelterVisible (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 5: Create distance from hostiles when health is not critical
    (: Rule 5
        (TTV 0)
        (STV 0.9 0.85)
        (Complexity 4)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isNightTime (STV 1.0 1.0))
                    (hostileNearby (STV 1.0 0.9))
                    (safeHealth (STV 1.0 0.8))
                )))
                (Action (SEQ_AND (
                    (flee)
                    (wander)
                )))
            )
            (Goal (STV 1.0 0.9) (AND (
                (shelterVisible (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 6: Navigate and scan for a safer position when it is night but no direct threat
    (: Rule 6
        (TTV 0)
        (STV 0.82 0.78)
        (Complexity 6)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isNightTime (STV 1.0 1.0))
                    (noHostilesNearby (STV 1.0 0.85))
                )))
                (Action (SEQ_AND (
                    (chooseDirection)
                    (walkForward)
                    (scanEnvironment)
                )))
            )
            (Goal (STV 1.0 0.88) (AND (
                (shelterVisible (STV 1.0 1.0))
            )))
        )
    )


    ;; Rule 7: Recover energy by eating when health is low and food is available
    (: Rule 7
        (TTV 0)
        (STV 0.95 0.9)
        (Complexity 4)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (lowHealth (STV 1.0 0.95))
                    (hasEdibleFoodInInventory (STV 1.0 0.9))
                )))
                (Action (SEQ_AND (
                    (eatFood)
                )))
            )
            (Goal (STV 1.0 0.9) (AND (
                (healthIncreasing (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 8: Acquire food first when low health and no edible inventory exists
    (: Rule 8
        (TTV 0)
        (STV 0.85 0.8)
        (Complexity 6)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (lowHealth (STV 1.0 0.95))
                    (noEdibleFoodInInventory (STV 1.0 0.9))
                    (foodAnimalNearby (STV 1.0 0.85))
                )))
                (Action (SEQ_AND (
                    (moveToFood)
                    (dig)
                    (collectFood)
                )))
            )
            (Goal (STV 1.0 0.85) (AND (
                (healthIncreasing (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 9: Explore during daytime when basic survival conditions are stable
    (: Rule 9
        (TTV 0)
        (STV 0.8 0.72)
        (Complexity 5)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isDayTime (STV 1.0 1.0))
                    (notHungry (STV 1.0 0.9))
                    (noHostilesNearby (STV 1.0 0.9))
                    (safeHealth (STV 1.0 0.85))
                )))
                (Action (SEQ_AND (
                    (walkForward)
                    (scanEnvironment)
                    (wander)
                )))
            )
            (Goal (STV 1.0 0.85) (AND (
                (Explore (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 10: Low-risk curiosity-driven roaming
    (: Rule 10
        (TTV 0)
        (STV 0.7 0.65)
        (Complexity 3)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isDayTime (STV 1.0 1.0))
                    (curiosityHigh (STV 1.0 0.7))
                )))
                (Action (SEQ_AND (
                    (wander)
                    (scanEnvironment)
                )))
            )
            (Goal (STV 1.0 0.75) (AND (
                (Explore (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 11: Prioritize surfacing when oxygen is low
    (: Rule 11
        (TTV 0)
        (STV 0.98 0.9)
        (Complexity 4)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (lowAir (STV 1.0 0.98))
                )))
                (Action (SEQ_AND (
                    (surfaceForAir)
                    (checkBreathing)
                )))
            )
            (Goal (STV 1.0 0.98) (AND (
                (breathableAir (STV 1.0 1.0))
            )))
        )
    )

  ))
  (add-atom $space $rules)
))

!(addMinecraftRules &ruleSpace)
