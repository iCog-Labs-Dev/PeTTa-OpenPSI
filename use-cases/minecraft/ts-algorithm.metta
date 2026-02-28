(= (import $name) (py-call (importlib.import_module $name)))
(= (get-attribute $obj $name) (py-call (getattr $obj $name)))

(= (eulerNumber) (get-attribute (import math) e))


(= (np) (import numpy))
(= (np.random) (get-attribute (np) random))

(= (np-rand) 
   (py-call (".rand" (np.random))))

(= (np-randint $min $max) 
   (py-call (".randint" (np.random) $min $max)))

(= (np-beta $a $b $n)
    (py-call (".beta" (np.random) $a $b $n)))
   
(= (thompson-sampler $a $b $n) (
    np-beta $a $b $n))
    
; c -> n
(= (confidenceToCount $confidence) (
    / (* $confidence 800) (- 1 $confidence)
))

; n -> c
(= (countToConfindence $count) (
    / $count (+ 800 $count)
))

; stv -> beta
(= (stvToBeta ($strength $confidence)) (
    let* (
        ($count (confidenceToCount $confidence))
        ($alpha (* $strength $count))
        ($beta (- $count $alpha))
    ) ($alpha $beta)
))

; beta -> stv
(= (betaToSTV ($alpha $beta)) (
    let* (
        ($count (+ $alpha $beta))
        ($strength (round (/ $alpha $count) 3))
        ($confidence (+ 0.001 (round (countToConfindence $count) 3)))
    ) ($strength $confidence)
))



(= (getSTV $ruleId $space) (
    match $space (: Rule $ruleId $ttv (STV $s $c) $comp $impl) ($s $c)
))


(= (getAction $ruleId $space) (
    match $space (: Rule $ruleId $ttv $stv $comp (IMPLICATION (AND $context (Action $action)) $goal)) $action
))

(= (getContext $ruleId $space) (
    match $space (: Rule $ruleId $ttv $stv $comp (IMPLICATION (AND $context $action) $goal)) $context
))

(= (getContextAtoms $ruleId $space) (
    match $space (: Rule $ruleId $ttv $stv $comp (IMPLICATION (AND (Context $cstv (AND $atoms)) $action) $goal)) $atoms
))


(= (matchGoal $goalName $space) (
    collapse (let* (
        ($rule (match $space (: Rule $id $ttv $stv $comp (IMPLICATION $ant (Goal $gstv (AND $goalList)))) ($id $goalList)))
        (($id $goalList) $rule)
        ($goalListName (map-atom $goalList $g (car-atom $g)))
        ($isMatch (intersection-atom ($goalName) $goalListName))
        ; ($_ (println! ("Is Match" $isMatch " for Goal: " $goalName " in Rule ID: " $id)))
    ) (if (> (size-atom $isMatch) 0)
            $id
            (empty)
    )))
)


(= (matchRules $currentContext $space) (
    collapse (
        let* (
            ($ruleAtom (match $space (: Rule $id $ttv $stv $comp (IMPLICATION (AND (Context $cstv (AND $ctxAtoms)) $action) $goal)) (: $id $ttv $stv $comp (IMPLICATION (AND (Context $cstv (AND $ctxAtoms)) $action) $goal))))
            ((: $id $ttv $stv $comp (IMPLICATION (AND (Context $cstv (AND $ctxAtoms)) $action) $goal)) $ruleAtom)
            ($isMatch (isContextApplicable $ctxAtoms $currentContext))
            ($_ (println! ("Rule ID:" $id " Match:" $isMatch)))
        ) (if $isMatch $id (empty))
    )
))

(= (updateAtom $space $old $new) (
        let $_ (remove-atom $space $old) 
            (add-atom $space $new)))

(= (round $x $d) 
   (py-call ("round" $x $d)))

(= (updateRule $ruleId $result $space) (
    let* (
        ($rule (match $space (: Rule $ruleId $ttv (STV $s $c) $comp $impl) (: Rule $ruleId $ttv (STV $s $c) $comp $impl)))
        ((: Rule $id $ttv (STV $s $c) $comp $impl) $rule)
        (($alpha $beta) (stvToBeta ($s $c)))
        ($newAlpha (if (== $result 1) (+ $alpha 1) $alpha))
        ($newBeta (if (== $result 1) $beta (+ $beta 1)))
        (($ns $nc) (betaToSTV ($newAlpha $newBeta)))
        ($_ (println! ("New STV Params: (" $ns ", " $nc ")")))

        
        ($newRule (: Rule $id $ttv (STV $ns $nc) $comp $impl))
        ($_ (println! ("Updating Rule ID: " $id " | Old STV: (" $s ", " $c ") | New STV: (" $ns ", " $nc ")")))
        ($_ (remove-atom $space $rule))
        ($_ (add-atom $space $newRule))
    ) ()
))

; Thompson Sampling
(= (sampler $ids $space) (
    if (== () $ids)
        (-1 0)
        (let* (
            (($head $tail) (decons-atom $ids))
            (($s $c) (getSTV $head $space))
            (($alpha $beta) (stvToBeta ($s $c)))
            (($sample) (thompson-sampler $alpha $beta 1))
            (($chosenId $chosenSample) (sampler $tail $space))
        ) (
            if (> $sample $chosenSample)
                ($head $sample)
                ($chosenId $chosenSample)
        ))
))
(= (update-atom $space $oatom $natom) (let $_ (remove-atom $space $oatom) (add-atom $space $natom)))



;; The following are utility functions for the planner when the agent is in curios mode 
;; and wants to explore actions with uncertain outcomes. 
;; These functions are not currently used in the main planner loop but can be integrated for enhanced exploration strategies.

;; derived from beta distribution variance

;; variance of Beta distribution
(= (getBetaVariance $alpha $beta) (
    let* (
        ($sum (+ $alpha $beta))
        ($numerator (* $alpha $beta))
        ($denominator (* (* $sum $sum) (+ $sum 1)))
    ) (/ $numerator $denominator)
))

;; Exploration Sampling: Select rule with highest variance (uncertainty)
(= (explorationSample $ruleIds $space) (
    if (== $ruleIds ())
        (-1 0)
    (let* (
        (($ruleId $rest) (decons-atom $ruleIds))
        ($_ (println! ("Exploration considering rule: " $ruleId)))
        (($strength $confidence) (getSTV $ruleId $space))
        (($alpha $beta) (stvToBeta ($strength $confidence)))
        ($variance (getBetaVariance $alpha $beta))
        ($_ (println! ("Rule " $ruleId " variance: " $variance)))
        (($chosenId $chosenVariance) (explorationSample $rest $space))
    ) (if (>= $variance $chosenVariance) 
        ($ruleId $variance) 
        ($chosenId $chosenVariance)
    ))
))

