
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
                    (foodNearby (STV 1.0 0.9))
                    (noEdibleFoodInInventory (STV 1.0 0.85))
                )))
                (Action (SEQ_AND (
                    (moveToFood)
                    (eatFood)
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
                    (noFoodNearby (STV 1.0 0.8))
                )))
                (Action (SEQ_AND (
                    (searchForFood)
                )))
            )
            (Goal (STV 1.0 0.85) (AND (
                (hasFood (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 4: Under direct threat, use known shelter immediately
    (: Rule 4
        (TTV 0)
        (STV 0.95 0.9)
        (Complexity 5)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (hostileNearby (STV 1.0 0.95))
                    (hasShelterKnown (STV 1.0 0.9))
                )))
                (Action (SEQ_AND (
                    (seekShelter)
                )))
            )
            (Goal (STV 1.0 0.95) (AND (
                (shelterUnderThreat (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 5: Under direct threat with no known shelter, build then enter
    (: Rule 5
        (TTV 0)
        (STV 0.9 0.85)
        (Complexity 7)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (hostileNearby (STV 1.0 0.95))
                    (noShelterKnown (STV 1.0 0.9))
                )))
                (Action (SEQ_AND (
                    (buildShelter)
                    (enterShelter)
                )))
            )
            (Goal (STV 1.0 0.95) (AND (
                (shelterUnderThreat (STV 1.0 1.0))
            )))
        )
    )


    ;; Rule 6: Recover energy by eating when health is low and food is available
    (: Rule 6
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

    ;; Rule 7: Acquire food first when low health and no edible inventory exists
    (: Rule 7
        (TTV 0)
        (STV 0.85 0.8)
        (Complexity 6)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (lowHealth (STV 1.0 0.95))
                    (noEdibleFoodInInventory (STV 1.0 0.9))
                    (foodNearby (STV 1.0 0.85))
                )))
                (Action (SEQ_AND (
                    (moveToFood)
                    (eatFood)
                )))
            )
            (Goal (STV 1.0 0.85) (AND (
                (healthIncreasing (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 8: Explore during daytime when basic survival conditions are stable
    (: Rule 8
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
                    (scanEnvironment)
                    (wander)
                )))
            )
            (Goal (STV 1.0 0.85) (AND (
                (Explore (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 10: Prioritize surfacing when oxygen is low
    (: Rule 10
        (TTV 0)
        (STV 0.98 0.9)
        (Complexity 4)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (lowAir (STV 1.0 0.98))
                )))
                (Action (SEQ_AND (
                    (findGround)
                    (checkBreathing)
                )))
            )
            (Goal (STV 1.0 0.98) (AND (
                (breathableAir (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 11: Night-time safety with known shelter (no immediate hostile)
    (: Rule 11
        (TTV 0)
        (STV 0.9 0.85)
        (Complexity 5)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isNightTime (STV 1.0 1.0))
                    (noHostilesNearby (STV 1.0 0.85))
                    (hasShelterKnown (STV 1.0 0.9))
                )))
                (Action (SEQ_AND (
                    (seekShelter)
                    (sleepAtNight)
                )))
            )
            (Goal (STV 1.0 0.9) (AND (
                (shelterUnderThreat (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 12: Night-time safety with no known shelter (build then enter)
    (: Rule 12
        (TTV 0)
        (STV 0.88 0.82)
        (Complexity 6)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isNightTime (STV 1.0 1.0))
                    (noHostilesNearby (STV 1.0 0.85))
                    (noShelterKnown (STV 1.0 0.9))
                )))
                (Action (SEQ_AND (
                    (buildShelter)
                    (enterShelter)
                    (sleepAtNight)
                )))
            )
            (Goal (STV 1.0 0.88) (AND (
                (shelterUnderThreat (STV 1.0 1.0))
            )))
        )
    )

    ;; Rule 13: Daytime proactive shelter preparation
    (: Rule 13
        (TTV 0)
        (STV 0.8 0.75)
        (Complexity 5)
        (IMPLICATION
            (AND
                (Context (STV 1.0 1.0) (AND (
                    (isDayTime (STV 1.0 1.0))
                    (noHostilesNearby (STV 1.0 0.9))
                    (noShelterKnown (STV 1.0 0.85))
                )))
                (Action (SEQ_AND (
                    (buildShelter)
                )))
            )
            (Goal (STV 1.0 0.85) (AND (
                (shelterPrepared (STV 1.0 1.0))
            )))
        )
    )

  ))
  (add-atom $space $rules)
))

!(addMinecraftRules &ruleSpace)

