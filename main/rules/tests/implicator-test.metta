!(import! &self ../rule)
!(import! &self ../implicator)
; !(import! &self ../../../utils)


!(bind! &test-space (new-space)) ;; a mock space used to test my functions.
; A helper function that serves as a testing mechanism.
(= (patternTester $pattern)
    (unify $pattern (: $handle ((TTV $time (STV $bel $conf)) (IMPLICATION_LINK (AND_LINK ($context $action)) $goal))) True False)
)


!(test (patternTester (changeRuleToQuery (: x ((TTV 1 (STV 0.5 0.6)) (IMPLICATION_LINK (AND_LINK ((a b) act)) (y)))))) True)

!(test (patternTester (changeRuleToQuery (x y z))) False)
!(test (checkSatisfiability x &test-space) (False (STV 0.0 1.0)))
!(satisfy &test-space (: x ((TTV 1 (STV 0.5 0.6)) (IMPLICATION_LINK (AND_LINK ((a b) act)) (y)))))
!(let $test-atoms (collapse (get-atoms &test-space)) (test (patternTester (car-atom $test-atoms)) True))
!(add-atom &test-space (x y z))
!(get-atoms &test-space)
!(test (checkSatisfier x &test-space) True)
!(test (checkSatisfier y &test-space) False)