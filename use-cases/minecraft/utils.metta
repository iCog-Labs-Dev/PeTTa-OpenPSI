(= (operator) (eval (import operator)))

(= (mod $val $mod)
   (py-call (".mod" (operator) $val $mod)))

(= (isModuloZero $step $n)
   (== (mod $step $n) 0))

(= (applyIterationEnvironment $step)
   (let* (
      ($timePulse (isModuloZero $step 2))
      ($_ (if $timePulse
               (py-call (utils.serverCommand "time add 1000"))
               ()))
               
      ($hungerPulse (isModuloZero $step 10))
      ($_ (if $hungerPulse
               (py-call (utils.serverCommand "effect give @p minecraft:hunger 10 40 true"))
               ()))
               
      ($nightThreatPulse (isModuloZero $step 7))
      ($_ (if (and $nightThreatPulse (isNightNow))
               (py-call (utils.serverCommand "summon zombie ~15 ~ ~15"))
               ()))
   )
   ()
))

(= (getRules) (collapse (get-atoms &ruleSpace)))


(= (minecraftGoalSelector $x) (
  case $x (
    (hunger (Goal hasFood 1.0 0.9))
    (safety (if (or (isNightNow) (hasHostileNearbyNow))
                (Goal shelterUnderThreat 1.0 0.95)
                (Goal shelterPrepared 1.0 0.85)))
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

(= (hasFoodNearbyNow)
   (eval (hasFoodNearby &perceptionSpace)))

(= (isCuriosityHighNow)
   (let* (
         ($vals (match &demandSpace (demand curiosity $min $max $val) $val))
         ; ($_ (println! ("Curiosity val: " $vals)))
      )
      (if (== $vals ())
         False
         (>= $vals (curiosityThreshold)))))

(= (hasShelterKnownNow)
   (let $v (sread (py-call (utils.hasShelterKnown)))
      (if (== $v ())
         False
         $v)))

(= (noShelterKnownNow)
   (not (hasShelterKnownNow)))

(= (airNow)
   (let $vals (collapse (match &perceptionSpace (air $airVal) $airVal))
      (if (== $vals ())
         (airMaxTicks)
         (car-atom $vals))))

(= (isLowAirNow)
   (< (airNow) (lowAirThreshold)))

(= (onGroundNow)
   (let $vals (collapse (match &perceptionSpace (onGround $g) $g))
      (if (== $vals ())
         True
         (car-atom $vals))))

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
      (foodNearby (hasFoodNearbyNow))
      (noFoodNearby (not (hasFoodNearbyNow)))
      (curiosityHigh (isCuriosityHighNow))
      (hasShelterKnown (hasShelterKnownNow))
      (noShelterKnown (noShelterKnownNow))
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
         ($_ (println! ("Evaluating Context Atom: " $head " Applicable: " $isHeadApplicable)))
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
      ((at $x $y $z) (eval (getPosition &perceptionSpace)))
      ($dxMag (random-int &rng $minStep $maxStep))
      ($dzMag (random-int &rng $minStep $maxStep))
      ($dxSign (if (== (random-int &rng 0 1) 0) -1 1))
      ($dzSign (if (== (random-int &rng 0 1) 0) -1 1))
      ($tx (+ $x (* $dxSign $dxMag)))
      ($tz (+ $z (* $dzSign $dzMag)))
      ; ($_ (println! ("Moving to random offset position: " $tx $y $tz)))
   )
   (py-call (utils.executeAction move_to $tx $y $tz))))


(= (moveVerticalOffset $deltaY) 
   (let* (
      ((at $x $y $z) (eval (getPosition &perceptionSpace)))
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
         ($_ (eval (pushEvent Action ($head))))
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
        ($pos (eval (getNearestFoodPos &perceptionSpace)))
        ($_ (println! ("Moving to food at position:" $pos)))
        )
      (if (== $pos ())
         ()
         (let ($x $y $z) $pos
            (py-call (utils.executeAction move_to $x $y $z)))
         )))

    ((eatFood) (py-call (utils.executeAction eat)))
    ((turnAwayFromThreat) (py-call (utils.executeAction turn_left)))
    ((sprintForward) (py-call (utils.executeAction move_forward)))
    ((mineResource) (py-call (utils.executeAction dig)))
    ((walkForward) (py-call (utils.executeAction move_forward)))
    ((surfaceForAir) (surfaceForAirLoop 3))
    ((findGround) (py-call (utils.executeAction find_ground)))
    ((recoverMobility) (let* (
        ($_ (py-call (utils.executeAction turn_left)))
        ($res (moveToRandomOffset 1 5))
    ) $res))
    ((seekShelter) (py-call (utils.executeAction seek_shelter)))
    ((enterShelter) (py-call (utils.executeAction enter_shelter)))
    ((sleepAtNight) (py-call (utils.executeAction sleep_at_night)))
    ((eat) (py-call (utils.executeAction eat)))
    ((dig) (py-call (utils.executeAction dig)))
    ((buildShelter) (py-call (utils.executeAction build_shelter)))
    ((checkBreathing) (if (and (not (isLowAirNow)) (onGroundNow)) (Air Stable) (Breathing Recovery)))
    ((searchForFood) (moveToRandomOffset -10 12))

    ((wander) (moveToRandomOffset -20 20))
    
    ((flee) (let* (
       ($_ (py-call (utils.executeAction turn_left)))
       ($res (py-call (utils.executeAction move_forward)))
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

    ((collectFood) (performSingleAction (collectItem)))

    ((scanEnvironment) (performSingleAction (lookAround)))

    ((lookAround) (let* (
      ;   ($leftRes (py-call (utils.executeAction turn_left)))
        ($rightRes (py-call (utils.executeAction turn_right)))
        ($_ (println! "Looked around"))
    ) (LookedAround)))

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
             (() ())
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


