!(bind! &satisfiabilityCache (new-space))
!(import! &self ../../../lib/lib_he)


;; This function fetches queries based on handles
;; it returns the handle and the query as one being the type of the other.
;; The template return type is (: handle $query)
(= (getQueryByHandle $handle $space)
   (let $queries (collapse (match $space (: $handle $queryBody) (: $handle $queryBody)))
        (if (== $queries ())
            ()
            (car-atom $queries)
        )
   
   )
)

;; changes the rule to the query that can match to the rule
;; hence every rule is going to be unique since the handle for 
;; every rule is going to be different.
(= (changeRuleToQuery $rule)
    (if (== $rule ())
        ()
        (let* (
                ($handle (car-atom (cdr-atom $rule)))
                ($queryTTV (: $handle ((TTV $time (STV $bel $conf)) (IMPLICATION_LINK (AND_LINK ($context $action)) $goal))))
                ($queryTV (: $handle ((STV $bel $conf) (IMPLICATION_LINK (AND_LINK ($context $action)) $goal))))
                
            )
            (unify (quote $rule) (quote $queryTTV)
                (: $handle ((TTV $time' (STV $bel' $conf')) (IMPLICATION_LINK (AND_LINK ($context' $action')) $goal')))
                (unify (quote $rule) (quote $queryTV)
                    (: $handle ((STV $bel' $conf') (IMPLICATION_LINK (AND_LINK ($context' $action')) $goal')))
                    ()

                )
            )
        )

    )
)


;;This function is a function that can be used as a helper for 
;; one instance which is used as a helper function for checkSatisfier
;; which works with a list.
(= (checkSatisfier' $rule $cacheInstance)
    (unify $rule $cacheInstance True False)
)

;;checks if the rules pattern exists in the satisfiability cache
;;The satisfiability cache is a space to cache already grounded satisfiable code.
(= (checkSatisfier $handle $satisfiabilityCache)
    (let* (
        ($rule (getQueryByHandle $handle $satisfiabilityCache))
        ($caches (collapse (get-atoms $satisfiabilityCache)))
        ($_ (println! (caches $caches)))
        ($truthValues (if (> (size-atom $caches) 0)(collapse (checkSatisfier' $rule (superpose $caches))) (False)))
        ($_ (println! (truthValues $truthValues)))
    ) 
        (any $truthValues)
    )

)

;;Implements a simple grounding mechanism for metta
(= (satisfy $satisfiabilityCache $rule)
    (let* ( 
        ($_ (println! (rules in satisfy $rule)))
        ($query (changeRuleToQuery $rule))
        ($_ (println! (queryToSatisfy $query)))
        ($handle (cadr-atom $rule))
        ($_ (println! (handle $handle)))
        ($exists (checkSatisfier $handle $satisfiabilityCache))
    
    )
        (if $exists
            ()
            (add-atom $satisfiabilityCache $query)
        )
    )
)
;;This is a helper function to assist the recursion process.
(=(removeBasedOnPattern $pattern $space-pattern $space)
    (unify $pattern $space-pattern
        (let $_ (remove-atom $space $space-pattern) (pass) )
        (fail)
    )
)
;; Removes a pattern based on a list of patterns stored in a space.
;; This function expects a signal from removeBasedOnPattern every step.
(=(removeBasedOnPatternList $pattern $patternList $space)
    (if (== () $patternList)
        ()
        (let* (
            (($head $tail) (decons-atom $patternList))
            ($_ (println! (headonRemove $head)))
            ($_ (println! (pattern $pattern)))
            ($state (removeBasedOnPattern $pattern $head $space))
        )
            (if (== $state (pass))
                ()
                (removeBasedOnPatternList $pattern $tail $space)

            )
        )
    )
)

;; checks if a rule is grounded using the satisfy function.
(= (checkSatisfiability $handle $satisfiabilityCache)
    (let* ( 
        ($query (getQueryByHandle $handle $satisfiabilityCache))
        ($_ (println! (querySatisfiability $query)))
        ($caches (collapse (get-atoms $satisfiabilityCache)))
        ($_ (println! (handleSatisfiability $handle)))
    )
    
       (if  (== $query ()) 
            (FALSE_TV)
            (let* (
                ($x (removeBasedOnPatternList  $query $caches $satisfiabilityCache))
                ($_ (println! (after-remove (collapse (get-atoms $satisfiabilityCache)))))
                ($y (satisfy $satisfiabilityCache $query))
            )
                (if (checkSatisfier $handle $satisfiabilityCache)
                    (TRUE_TV)
                    (FALSE_TV)
                )
            )

        )
    )
)