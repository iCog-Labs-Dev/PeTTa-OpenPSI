;; Minecraft Agent Perception Module

!(add-atom &demandSpace (demand hunger 0.0 1.0 1.0))
!(add-atom &demandSpace (demand safety 0.0 1.0 0.7))
!(add-atom &demandSpace (demand curiosity 0.0 1.0 0.75))
!(add-atom &demandSpace (demand energy 0.0 1.0 1.0))
!(add-atom &demandSpace (demand breath 0.0 1.0 1.0))

(= (totalPoints) 20)

(= (removeOccurrences $space)
   (let $atoms (get-atoms $space)
        (remove-atom $space $atoms)
    )
)

(= (updatePerception $space)
   (let* (
      ($_ (collapse(removeOccurrences $space)))
      ($obs (py-call (utils.getObservation)))
      ($_ (collapse (addIndividualObservation $obs $space)))
   )
   ()
))

(= (addIndividualObservation $atoms $space)
   (if (== $atoms ())
      (empty)
      (let* (
         (($head $tail) (decons $atoms))
         ; ($_ (println! ("Adding observation: " $head)))
         ($expr (sread $head))
         ($_ (collapse (add-atom $space $expr)))
         ($_ (collapse (addIndividualObservation $tail $space)))
      )
      ()
      )
))


(= (getPosition $space)
   (match $space (at $x $y $z) (at $x $y $z)))
   
(= (getHealth $space)
   (match $space (health $h) $h))
   
(= (getHunger $space)
   (match $space (hunger $h) $h))

(= (getAir $space)
   (match $space (air $a) $a))

(= (getOnGround $space)
   (match $space (onGround $g) $g))

(= (getActionStatus $space)
   (collapse (match $space (actionStatus $cmd $val) (actionStatus $cmd $val))))
   
(= (isDaytime $space)
   (match $space (isDay $d) $d))
   
(= (getNearbyEntities $space $type)
   (collapse (match $space (nearEntity $type $dist $x $y $z) (nearEntity $type $dist $x $y $z))))

   
(= (hostileNearBy $space)
   (let $hostiles (collapse (match $space (nearEntity $type $dist $x $y $z)
       (if (or (== $type zombie) 
               (or (== $type skeleton) 
                   (or (== $type spider) (== $type creeper))))
           True
           (empty))))
      (if (== $hostiles ())
         False 
         True  
      )
))


(= (hasItem $space $item)
   (let $found (collapse (match $space (hasItem $item $count) True))
      (if (== $found ()) False True)))

(= (getItemCount $space $item)
   (let $counts (collapse (match $space (hasItem $item $count) $count))
      (if (== $counts ()) 
         0 
         (car-atom $counts))
))


(= (hungerUrgency $space)
   (let $hunger (getHunger $space)
      (/ (- (totalPoints) $hunger) (totalPoints))))


(= (healthUrgency $space)
   (let $health (getHealth $space)
      (/ (- (totalPoints) $health) (totalPoints))))

(= (safetyLevel $space)
   (let* (
      ($isDay (isDaytime $space))
      ($isNight (not $isDay))
      ($hostileNear (hostileNearBy $space))
      ($hasShelter (eval (hasShelterKnownNow)))
      ($_ (println! ("Calculating safety level. IsDay: " $isDay " HostileNearby: " $hostileNear " HasShelter: " $hasShelter)))

      ($baseSafety (if $isDay 0.9 0.55))
      ($shelterBonus (if (and $isNight $hasShelter) 0.2 0.0))
      ($noShelterPenalty
         (if $hasShelter
            0.0
            (if $isDay 0.25 0.35)))
            
      ($hostilePenalty
         (if $hostileNear
            (if $hasShelter 0.5 0.8)
            0.0))

      ($safety  (- (- (+ $baseSafety $shelterBonus) $hostilePenalty) $noShelterPenalty))
   )
   (if (< $safety  0.0)
      0.0
      (if (> $safety  1.0) 1.0 $safety ))))

(= (airMaxTicks) 300.0)

(= (airUrgency $space)
   (let $air (getAir $space)
      (/ (- (airMaxTicks) $air) (airMaxTicks))))



(= (perceptionToDemands $perceptionSpace $demandSpace)
   (let* (
      ($hungerVal (- 1 (hungerUrgency $perceptionSpace)))
      ($healthVal (- 1 (healthUrgency $perceptionSpace)))
      ($safetyVal (safetyLevel $perceptionSpace))
      ($airVal (- 1 (airUrgency $perceptionSpace)))
      ($_ (println! ("Demands: " $safetyVal $hungerVal $healthVal $airVal)))
      
      
      ((demand hunger $hMin $hMax $hOld) (getDemandByName $demandSpace hunger))
      ($_ (updateDemandValue $demandSpace hunger $hungerVal))
      
      ((demand safety $sMin $sMax $sOld) (getDemandByName $demandSpace safety))
      ($_ (updateDemandValue $demandSpace safety $safetyVal))

      ((demand energy $eMin $eMax $eOld) (getDemandByName $demandSpace energy))
      ($_ (updateDemandValue $demandSpace energy $healthVal))

      ((demand breath $bMin $bMax $bOld) (getDemandByName $demandSpace breath))
      ($_ (updateDemandValue $demandSpace breath $airVal))

   )
   ()
   )
)


(= (isEdible $item)
   (case $item (
      (porkchop True)
      (cooked_porkchop True)
      (beef True)
      (cooked_beef True)
      (chicken True)
      (cooked_chicken True)
      (mutton True)
      (cooked_mutton True)
      (rabbit True)
      (cooked_rabbit True)
      (bread True)
      (apple True)
      (carrot True)
      (potato True)
      (baked_potato True)
      (golden_apple True)
      (melon_slice True)
      (sweet_berries True)
      (glow_berries True)
      ($_ False)
   )))


(= (hasEdibleFood $space)
   (let* (
      ($foodItems (collapse (match $space (hasItem $item $count)
         (if (isEdible $item) 
            ($item $count)
            (empty) ))))
         ; ($_ (println! ("Edible food items in inventory: " $foodItems)))
      )
      (if (== $foodItems ()) 
         False 
         True)))


(= (getInventoryFood $space)
   (collapse 
      (match $space (hasItem $item $count)
         (if (isEdible $item) 
            (FoodItem $item $count) 
            (empty)))))


(= (isFoodAnimal $type)
   (case $type (
      (pig True)
      (cow True)
      (sheep True)
      (chicken True)
      (rabbit True)
      ($_ False)
   )))


(= (hasFoodNearby $space)
   (let $foodEntity (collapse 
      (match $space (nearEntity $type $dist $x $y $z)
         ;; currently we will only look for only edible foods only
         ;; going after food animals needs complex logic to hunt and collect, which we will implement later
         (if (isEdible $type)
            ($type $dist)
            (empty))))
      (if (== $foodEntity ())
         False
         True)))

(= (getNearestFoodAnimal $space)
   (let $animals (collapse 
      (match $space (nearEntity $type $dist $x $y $z)
         (if (isFoodAnimal $type)
            ($type $dist)
            (empty))))

      (if (== $animals ())
         ()
         (car-atom $animals))))

(= (getNearestFoodPos $space)
   (let $foodEntity (collapse 
      (match $space (nearEntity $type $dist $x $y $z)
         (if (isEdible $type)
            ($x $y $z $dist)
            (empty))))
      (if (== $foodEntity ())
         ()
         (let* (
            ($sorted (py-call (utils.sortEntities $foodEntity)))
            (($x $y $z $d) (car-atom $sorted))
         )
         ($x $y $z)
         )
      )
))
