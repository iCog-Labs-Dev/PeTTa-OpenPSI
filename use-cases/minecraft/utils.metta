
(= (getRules) (collapse (get-atoms &ruleSpace)))


(= (minecraftGoalSelector $x) (
  case $x (
    (hunger (Goal hasFood 1.0 0.9))
    (safety (Goal shelterVisible 1.0 0.9))
    (curiosity (Goal Explore 1.0 0.5))
    (energy (Goal healthIncreasing 1.0 0.9))
    (breath (Goal breathableAir 1.0 0.95))
  ))
)


(= (hungerThreshold) 10)

(= (lowHealthThreshold) 10)

(= (safeHealthThreshold) 14)

(= (curiosityThreshold) 0.5)

(= (lowAirThreshold) 200)

(= (isHungryNow)
   (let $h (eval (getHunger &perceptionSpace))
      (if (== $h ())
         False
         (< $h (hungerThreshold)))))

(= (isLowHealthNow)
   (let $health (eval (getHealth &perceptionSpace))
      (if (== $health ())
         False
         (< $health (lowHealthThreshold)))))

(= (isSafeHealthNow)
   (let $health (eval (getHealth &perceptionSpace))
      (if (== $health ())
         False
         (>= $health (safeHealthThreshold)))))

(= (isDayNow)
   (let $d (eval (isDaytime &perceptionSpace))
      (if (== $d ())
         False
         $d)))

(= (isNightNow)
   (not (isDayNow)))

(= (hasHostileNearbyNow)
   (eval (hostileNearBy &perceptionSpace)))

(= (hasEdibleFoodNow)
   (eval (hasEdibleFood &perceptionSpace)))

(= (hasFoodAnimalNearbyNow)
   (eval (hasFoodAnimalNearby &perceptionSpace)))

(= (isCuriosityHighNow)
   (let* (
         ($vals (match &demandSpace (demand curiosity $min $max $val) $val))
         ; ($_ (println! ("Curiosity val: " $vals)))
      )
      (if (== $vals ())
         False
         (>= $vals (curiosityThreshold)))))

(= (airNow)
   (let $vals (collapse (match &perceptionSpace (air $airVal) $airVal))
      (if (== $vals ())
         (airMaxTicks)
         (car-atom $vals))))

(= (isLowAirNow)
   (< (airNow) (lowAirThreshold)))


(= (contextAtomName $ctxAtom)
   (case $ctxAtom (
      (($name (STV $s $c)) $name)
      (($name $x) $name)
      ($name $name)
   )))

(= (evalContextPredicate $name)
   (case $name (
      (isHungry (isHungryNow))
      (notHungry (not (isHungryNow)))
      (lowHealth (isLowHealthNow))
      (safeHealth (isSafeHealthNow))
      (isNightTime (isNightNow))
      (isDayTime (isDayNow))
      (hostileNearby (hasHostileNearbyNow))
      (noHostilesNearby (not (hasHostileNearbyNow)))
      (hasEdibleFoodInInventory (hasEdibleFoodNow))
      (noEdibleFoodInInventory (not (hasEdibleFoodNow)))
      (foodAnimalNearby (hasFoodAnimalNearbyNow))
      (noFoodAnimalNearby (not (hasFoodAnimalNearbyNow)))
      (curiosityHigh (isCuriosityHighNow))
      (lowAir (isLowAirNow))
      (safeAir (not (isLowAirNow)))
      ($_ False)
   )))

(= (isContextAtomApplicable $ctxAtom)
   (let $ctxName (contextAtomName $ctxAtom)
      (evalContextPredicate $ctxName)))

(= (isContextApplicable $ctxAtoms)
   (if (== $ctxAtoms ())
      True
      (let* (
         (($head $tail) (decons-atom $ctxAtoms))
         ($isHeadApplicable (isContextAtomApplicable $head))
      )
      (if $isHeadApplicable
         (isContextApplicable $tail)
         False))))

(= (filterRulesByContext $ruleIds $space)
   (if (== $ruleIds ())
      ()
      (let* (
         (($head $tail) (decons-atom $ruleIds))
         ($ctxAtoms (eval (getContextAtoms $head $space)))
         ; ($_ (println! ("Filtering Rule ID: " $head " with Context Atoms: " $ctxAtoms)))
         ($isMatch (isContextApplicable $ctxAtoms))
         ; ($_ (println! ("Rule ID: " $head " Context Match: " $isMatch)))
         ($filteredTail (filterRulesByContext $tail $space))
      )
      (if $isMatch
         (cons-atom $head $filteredTail)
         $filteredTail))))


(= (moveToRandomOffset $minStep $maxStep)
   (let* (
      ((at $x $y $z) (getPosition &perceptionSpace))
      ($dxMag (random-int &rng $minStep $maxStep))
      ($dzMag (random-int &rng $minStep $maxStep))
      ($dxSign (if (== (random-int &rng 0 1) 0) -1 1))
      ($dzSign (if (== (random-int &rng 0 1) 0) -1 1))
      ($tx (+ $x (* $dxSign $dxMag)))
      ($tz (+ $z (* $dzSign $dzMag)))
   )
   (py-call (utils.executeAction move_to $tx $y $tz))))


(= (moveVerticalOffset $deltaY) 
   (let* (
      ((at $x $y $z) (getPosition &perceptionSpace))
      ($ty (+ $y $deltaY))
   )
   (py-call (utils.executeAction move_to $x $ty $z)))
)


(= (surfaceForAirLoop $stepsLeft)
   (if (== $stepsLeft 0)
      ()
      (let* (
         ; ($_ (updatePerception &perceptionSpace))
         ($currAirlvl (sread (py-call (utils.getAirLevel))))
         ($stillLowAir (< $currAirlvl (lowAirThreshold)))
         ($_ (println! ("Current Air Level: " $currAirlvl "still low: " $stillLowAir)))

      )
      (if $stillLowAir
         (let* (
            ($_ (py-call (utils.executeAction jump)))
         )
         (surfaceForAirLoop (- $stepsLeft 1)))
         (Air Recovered)))))

(= (getNearestEntityPosByType $space $targetType)
   (let $targets (collapse
      (match $space (nearEntity $type $dist $x $y $z)
         (if (== $type $targetType)
            ($x $y $z $dist)
            (empty))))
      (if (== $targets ())
         ()
         (let* (
            ($sorted (py-call (utils.sortEntities $targets)))
            (($x $y $z $dist) (car-atom $sorted))
         )
         ($x $y $z)
         )
      )
))


(= (performAction $actions) (
   if (== $actions ())
      1
      (let* (
         (($head $tail) (decons-atom $actions))
         ($result (performSingleAction $head))
         ($_ (println! ("Performed action: " $head " Result: " $result)))
         ($_ (updatePerception &perceptionSpace))
      )
      
      (if (== $result ())
         0
         (performAction $tail))
      )
))

(= (performSingleAction $action) (
  case $action (
   
    ((moveToFood) (
      let* (
        ($pos (eval (getNearestFoodAnimalPos &perceptionSpace)))
        ($_ (println! ("Moving to food at position:" $pos)))
        )
      (if (== $pos ())
         ()
         (let ($x $y $z) $pos
            (py-call (utils.executeAction move_to $x $y $z)))
         )))

    ((eatFood) (py-call (utils.executeAction eat)))
    ((turnAwayFromThreat) (py-call (utils.executeAction turnLeft)))
    ((sprintForward) (py-call (utils.executeAction moveForward)))
    ((mineResource) (py-call (utils.executeAction dig)))
    ((walkForward) (py-call (utils.executeAction moveForward)))
    ((surfaceForAir) (surfaceForAirLoop 3))
    ((recoverMobility) (let* (
        ($_ (py-call (utils.executeAction turnLeft)))
        ($res (moveToRandomOffset 1 5))
    ) $res))
    ((eat) (py-call (utils.executeAction eat)))
    ((dig) (py-call (utils.executeAction dig)))
    ((checkBreathing) (if (isLowAirNow) (Low Air) (Air Stable)))
    ((searchForFood) (moveToRandomOffset -10 12))

    ((wander) (moveToRandomOffset 6 18))
    
    ((flee) (let* (
       ($_ (py-call (utils.executeAction turnLeft)))
       ($res (py-call (utils.executeAction moveForward)))
       )
      $res))
      
    ((approachTarget) (let* (
        ($pos (eval (getNearestFoodAnimalPos &perceptionSpace)))
      )
      (if (== $pos ())
         (moveToRandomOffset 2 6)
         (let* (
            (($x $y $z) $pos)
         )
         (py-call (utils.executeAction move_to $x $y $z))))))

    ((collectItem) (
      let* (
        ($pos (eval (getNearestEntityPosByType &perceptionSpace item)))
        )
         (if (== $pos ())
            ()
            (let ($x $y $z) $pos
            (py-call (utils.executeAction move_to $x $y $z))))
      ))

   ;  (collectFood (performSingleAction (approachTarget)))

   ;  (selectFood (if (hasEdibleFood &perceptionSpace) (Food Selected) (No Food To Select)))
    
   ;  (searchForShelter (performSingleAction (findShelter)))
   ;  (moveToShelter (performSingleAction (findShelter)))
   ;  (findCover (performSingleAction (findShelter)))
    
   ;  (closeEntrance (py-call (utils.executeAction place)))
   ;  (selectBlocks (py-call (utils.executeAction place)))
    
   ;  (reinforceBarrier (performSingleAction (placeBlocks)))
    
   ;  (moveToResource (moveToRandomOffset 2 6))
   ;  (collectDrops (performSingleAction (collectItem)))
    
   ;  (chooseDirection (performSingleAction (lookAround)))
    ((scanEnvironment) (performSingleAction (lookAround)))



   ;  (findShelter (let* (
   ;      ($_ (performSingleAction (lookAround)))
   ;      ($res (moveToRandomOffset 3 7))
   ;  ) $res))

    ((lookAround) (let* (
        ($_ (py-call (utils.executeAction turnLeft)))
        ($res (py-call (utils.executeAction turnRight)))
    ) $res))
   ;  (enterShelter (py-call (utils.executeAction crouch)))
   ;  (placeBlocks (py-call (utils.executeAction place)))


    ($else (let* (
        ($_ (println! (Unknown Action $else)))
    ) ()))
  ))
)


(= (actionPlanner $space $goalName)
    (let* (
          ($goalMatchedRules (eval (matchGoal $goalName $space)))
          ($rules (filterRulesByContext $goalMatchedRules $space))
          ($_ (println! ("Goal-Matched: " $goalMatchedRules )))
          ($_ (println! ("Context-Matched: " $rules )))
          ($result (if (== $rules ())
             ()
             (let* (
                (($chosenId $score) (eval (sampler $rules $space)))
                ($_ (println! ("Chosen Rule ID: " $chosenId " Score: " $score)))
                ($actionAtom (eval (getAction $chosenId $space)))
                ((SEQ_AND $actions) $actionAtom)
             )
             ($actions $chosenId)
             )
          ))
    )
    $result
    )
)

(= (modulatorUpdaterAgent $space $comp $aff $ener)
   (let* (
      ;; just temporary placeholders for modulator update logic
      ($_ (println! "Modulators Updated"))
   )
   (Modulators Updated)
   )
)


