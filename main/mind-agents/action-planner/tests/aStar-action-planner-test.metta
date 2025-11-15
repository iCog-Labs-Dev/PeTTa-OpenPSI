!(import! &self ../aStar-action-planner)


!(bind! &ruleSpace (new-space)) 
!(bind! &priorityQueueTest (new-space))


; Temporarily using global visited space until new-space works on PeTTa
!(bind! &visitedTest1 (new-space))
!(bind! &visitedTest2 (new-space))


!(add-atom &ruleSpace (: r1 (IMPLICATION_LINK (AND_LINK (Goal init 0.9 0.6) explore) (Goal found_target 1.0 1.0))))
!(add-atom &ruleSpace (: r2 (IMPLICATION_LINK (AND_LINK (Goal init 0.9 0.6) activate) (Goal active 0.8 0.5))))

 
;test case 

;addNewStates
;!(addNewStates 
;   ((explore (Goal found_target 1.0 1.0))) 
;   0 
;   () 
;   &pq 
;   (Goal found_target 1.0 1.0) 
;   &ruleSpace)  ; returns [(), ()]
;!(get-atoms &testedActions)  ; returns [(((Goal found_target 1.0 1.0)) explore)]
;!(assertEqual 
;   (getTestedActions (Goal found_target 1.0 1.0) &testedActions) 
;   (explore))
;!(getTestedActions (Goal found_target 1.0 1.0) &testedActions) ; returns [(explore)]


;findMinEntry
!(add-atom &priorityQueueTest (5 (Goal init 0.9 0.6) ())) 
!(add-atom &priorityQueueTest (2 (Goal found_target 1.0 1.0) (explore))) 
!(add-atom &priorityQueueTest (10 (Goal active 0.8 0.5) (move)))
!(test (findMinEntry &priorityQueueTest) (2 (Goal found_target 1.0 1.0) (explore)))


;popMin
!(test (popMin &priorityQueueTest) (2 (Goal found_target 1.0 1.0) (explore)))
; !(get-atoms &priorityQueue); returns [(5 (Goal init 0.9 0.6) ()), (10 (Goal active 0.8 0.5) (move))]
!(test (findMinEntry &priorityQueueTest) (5 (Goal init 0.9 0.6) ()))


;applyActions
; !(applyActions (explore) (Goal init 0.9 0.6) () &ruleSpace) ; results [((explore (Goal found_target 1.0 1.0)))]
!(test 
 (applyActions (explore) (Goal init 0.9 0.6) () &ruleSpace) 
 ((explore (Goal found_target 1.0 1.0))))


;filterUntriedRulesList
!(add-atom &testedActions ((Goal init 0.9 0.6) move))
!(test (filterUntriedRulesList ((explore) (move)) () ()) ((move) (explore)))
!(test (filterUntriedRulesList ((explore) (move)) ((move)) ()) ((explore))) 
!(test (filterUntriedRulesList ((explore) (move) (activate)) ((explore) (move) (activate)) ()) ())
!(test (filterUntriedRulesList ((explore) (move) (activate)) () ()) ((activate) (move) (explore)))
!(test (filterUntriedRulesList ((explore) (move) (activate)) ((move) (explore)) ()) ((activate)))

;isMember
!(test (isMember (Goal active 0.8 0.5) &testedActions) False)
!(test (isMember (Goal init 0.9 0.6) &testedActions) True)


;goal-value
;!(add-atom &ruleSpace (: r3 (IMPLICATION_LINK (AND_LINK (Goal init 0.9 0.6) search) (Goal intermediate 0.95 0.65))))
!(test (goal-value (Goal init 0.9 0.6) &ruleSpace) 0.9)
!(test (desired-goal-value (Goal init 0.9 0.6) &ruleSpace) 0.6)


;distance
!(test (distance (Goal init 0.9 0.6) (Goal found_target 1.0 1.0) &ruleSpace) 0.5)
!(test (distance (Goal init 0.9 0.6) (Goal unknown 0.0 0.0) &ruleSpace) 1.5)


;aStarPlanner

!(test (aStarPlanner (Goal found_target 1.0 1.0) (Goal found_target 1.0 1.0) &testedActions &ruleSpace &visitedTest1) ())  
!(test (aStarPlanner (Goal init 0.9 0.6) (Goal found_target 1.0 1.0) &testedActions &ruleSpace &visitedTest2) (explore))

; !(add-atom &ruleSpace (: r3 (IMPLICATION_LINK (AND_LINK (Goal active 0.8 0.5) move) (Goal reached 0.9 0.7)))) ;uncomment the above ruleSpaces and also the tests for the the planner, since aStarPlanner’s sequential rule evaluation 
; !(test (aStarPlanner (Goal active 0.8 0.5) (Goal reached 0.9 0.7) &testedActions &ruleSpace) (move))