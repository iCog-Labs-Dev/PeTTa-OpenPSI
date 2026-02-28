(: Demand Type)
(: SkipDemand Type)
; (: demand (-> Symbol Number Demand))
(: skip (-> Symbol SkipDemand))


(: alpha (-> Number))
(= (alpha) 150)

!(bind! &demandspace (new-space))

(= (addDemand $space $name $value)
    (let* (
            ($demand (demand $name $value))
            ; ($duplicateDemandList  (match $space (demand $name $v) (demand $name $v)))
            ($_ (add-atom $space $demand))
        )
     ()
    )
    )

(= (fetchDemand $space $name) (
    match $space (demand $name $min $max $val) (demand $name $min $max $val)
))

(= (fetchDemandVal $space $name) (
    let (demand $n $min $max $val) (fetchDemand $space $name) $val
))

(= (fetchDemandMinVal $space $name) (
    let (demand $n $min $max $val) (fetchDemand $space $name) $min
))

(= (fetchDemandMaxVal $space $name) (
    let (demand $n $min $max $val) (fetchDemand $space $name) $max
))

(= (getAllDemands $space)
    (collapse (match $space (demand $x $min $max $val) (demand $x $min $max $val)))
)


(= (skipDemand $space $demand) 
    (let* (
        ($skip (collapse (match $space (skip $demand) (skip $demand))))
        ( $isNotFound (== $skip ()))
    )
    (if $isNotFound 
        (add-atom $space (skip $demand)) 
        ()
    )
    )
)

(= (getEnabledDemands $space)
    (let* (
       ( $skippedDemands (collapse (match $space (, (demand $x $min $max $val) (skip $x)) (demand $x $min $max $val)) ))
    
       ( $allDemands (getAllDemands $space))
    
       ( $enabledDemands (collapse (subtraction  (superpose $allDemands)  (superpose $skippedDemands))))
     
    ) 
        $enabledDemands
    )
)

(= (setDemandValue $space $demandName $newValue)
    (let* (
        ((demand $demandName $oldValue ) (match $space (demand $demandName $oldValue) (demand $demandName $oldValue)))
        ($_ (remove-atom $space (demand $demandName $oldValue)))
        ($_ (add-atom $space (demand $demandName $newValue)))
    )
    ()
    )

)
(= (getDemandByName $space $name) (match $space (demand $name $min $max $x) (demand $name $min $max $x)))



(= (demandDecay $space $demand $value)
    (let* (
        ((demand $name $min $max $oldValue) $demand)
        ($newValue (- $oldValue $value))
    )
    (if (>= $newValue 0)
        (updateDemandValue $space $name $newValue)
        (let* (
            (() (remove-atom $space $demand))
            (() (remove-atom $space (skip $name)))
        ) ()
        )
    )
))

; Apply decay only to skipped demands
(= (decaySkippedDemands $space $decayValue)
    (let* (
        ($skippedDemandNames (collapse (match $space (skip $x) $x)))
        ($skippedDemands (collapse (let $demandName (superpose $skippedDemandNames) (fetchDemand $space $demandName))))
    )
    (if (== (size-atom $skippedDemands) 0)
        (There are no skipped demands) 
        (demandDecay $space (superpose $skippedDemands) $decayValue)
    ))
)

; Apply decay to all demands (both enabled and skipped)
(= (decayAllDemands $space $decayValue)
    (let* (
        ($allDemands (getAllDemands $space))
    )
    (if (== (size-atom $allDemands) 0)
        (No demands in the space)
        (let $demand (superpose $allDemands) (demandDecay $space $demand $decayValue))
    ))
)

; Apply different decay rates to enabled vs skipped demands
(= (decayDemandsWithDifferentRates $space $enabledDecayRate $skippedDecayRate)
    (let* (
        ($enabledDemandNames (getEnabledDemands $space))
        ($enabledDemands (collapse (unify $enabledDemandNames (demand $name $minVal $maxVal $val) $name ())))
        ($skippedDemandNames (collapse (match $space (skip $name) $name)))
        ($_ (decaySkippedDemands $space $skippedDecayRate))
    )
    (if (== (size-atom $enabledDemands) 0)
        (There is no skipped demand)
        (demandDecay $space (superpose $enabledDemands) $enabledDecayRate)
    ))
)


;; Function to calculate demand satisfaction according to Ben's Paper
;; Requires random function which should be imported from utils
(= (calculateDemandSatisfaction $space $demandName) (
    let* (
        ((demand $demandName $minVal $maxVal $currentValue) (fetchDemand $space $demandName))
        ($alpha (alpha))
    ) (if (not (and (< $currentValue $minVal) (> $currentValue $maxVal)))
        (+ 0.8 (* 0.2 (py-call (random.uniform 0 1))))
        (if (< $currentValue $minVal)
            (fuzzy_equal $currentValue $minVal $alpha)
            (+ 0.9 (* 0.1 (py-call (random.uniform 0 1))))
        )
    )
))

(= (checkEmpty $l) (if (== $l ()) true false))

;; Function to fetch the least satisfied demand from a list of demands
(= (fetchLeastSatisfiedDemand' $space $demands $leastSatisfiedDemand)
    (if (== $demands ())
        $leastSatisfiedDemand
        (let* (
            (($currentDemand $restDemands) (decons-atom $demands))
            ((demand $currentName $currentMin $currentMax $currentValue) $currentDemand)
            ((demand $leastName $leastMin $leastMax $leastValue) $leastSatisfiedDemand)
            ($currentSatisfaction (calculateDemandSatisfaction $space $currentName))
            ($leastSatisfaction (calculateDemandSatisfaction $space $leastName))
        )
        (if (< $currentSatisfaction $leastSatisfaction)
            (fetchLeastSatisfiedDemand' $space $restDemands $currentDemand)
            (fetchLeastSatisfiedDemand' $space $restDemands $leastSatisfiedDemand)
        )
    )
))

;; Function to fetch the least satisfied demand
(= (fetchLeastSatisfiedDemand $space) (
    let* (
        ($activeDemands (getEnabledDemands $space))
        ($leastSatisfiedDemand (car-atom $activeDemands))
    ) (if (== $activeDemands ())
        ("No active demands found")
        (fetchLeastSatisfiedDemand' $space $activeDemands $leastSatisfiedDemand)
    )
))

(= (updateDemandValue $space $demandName $urgValue) (
    let* (
        ($newValue (- 1 $urgValue))
        ; ($_ (println! ("Updating Demand:" $demandName " to New Value:" $newValue)))
        ((demand $demandName $min $max $oldValue) (match $space (demand $demandName $min $max $oldValue) (demand $demandName $min $max $oldValue)))
        ($_ (remove-atom $space (demand $demandName $min $max $oldValue)))
    )
    (add-atom $space (demand $demandName $min $max $newValue))
))
