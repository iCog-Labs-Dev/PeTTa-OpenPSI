!(import! &self ../rule)
!(import! &self ../../type)
; !(import! &self ../../../utils)

!(bind! &r (new-space)) 

!(test (addAndLink &r (a b) c) (AND_LINK ((a b) c)))

; add the same AND_LINK the second time, it should not be added again. It should 
; return the Already existing AND_LINK.
!(test (addAndLink &r (a b) c) (AND_LINK ((a b) c)))

;if rule is added with the addRule function then the &psiRules index knows 
;about it

!(addRule  &r x (x1 x2) y z (TTV 1 (STV 1.0 1.0)))
!(test (getContext  &r x) (x1 x2))
!(test (getAction  &r x) y)
!(test (getGoal  &r x) z)
!(test (getTV x &r) (TTV 1 (STV 1.0 1.0)))
!(test (getImplication x &r) (IMPLICATION (AND_LINK ((x1 x2) y)) z))

!(addRule  &r w (x3 x2) y z (TTV 1 (STV 1.0 1.0)))
; ;if rule is not added with the addRule function then the &psiRules index does not know
; about it
; but we can get context, action and goal of the rule

!(add-atom &r (: rule1 (IMPLICATION_LINK 
                            (AND_LINK ((c1 c2) action))
                            goal )))
!(test (getContext &r rule1) (c1 c2))
!(test (getGoal &r rule1) goal)
!(test (getAction &r rule1) action)
!(test (getImplication rule1 &r) (IMPLICATION (AND_LINK ((c1 c2) action)) goal))


!(test (existsIn &psiRules rule1) False)

!(test (existsIn &psiRules x) True)

!(test (addGoal reduceHunger 1 0 &self) reduceHunger)
!(test (addGoal reduceHunger 1 1 &self)  (Goal With Id reduceHunger Already Exists))
!(test (addGoal reduceHunger 10 1 &self) (Invalid goal/dgv Value))
!(test (addGoal reduceHunger 1 10 &self) (Invalid goal/dgv Value))
!(test (addGoal run 1 () &self) run)


!(test (relatedGoals &r y) (z))

;Category tests
!(test (addCategory testI) testI)

!(test (addToCategory x testII) x)
!(test (addToCategory x testII ) (addToCategory: Rule x Already Exists in testII))

!(test (len (getCategories)) 2)
!(test (contextStv ((STV 0.5 0.4) (STV 0.6 0.8))) (STV 0.315 0.4))
!(test (contextStv ((STV 1 1) (STV 1 1))) (STV 1 1))
!(test (contextStv ((STV 0 0) (STV 0 0))) (STV 0 0))

; ;urge Tests 

!(addGoal (pinged) 0.75 1.0 &self)
!(test (goal-value  (pinged) &self) 0.75)
!(test (urge-value  (pinged) &self) 0.25)

!(increase-urge (pinged) 0.15 &self)
!(test (urge-value  (pinged) &self) 0.4)
!(increase-urge (pinged) 0.3 &self)
!(test (urge-value  (pinged) &self) 0.7)

!(decrease-urge (pinged) 0.45 &self)
!(test (urge-value  (pinged) &self) 0.25)