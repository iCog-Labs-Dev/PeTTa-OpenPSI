!(import! &self "utils.py")
!(import! &self ../../main/modulator/modulator)
!(import! &self ../../main/feedback-loop/feedback-loop)
!(import! &self utils)
!(import! &self ts-algorithm)


!(bind! &kb (new-space))
!(bind! &perceptionSpace (new-space))
!(bind! &modulatorSpace (new-space))
!(bind! &ruleSpace (new-space))
!(bind! &demandSpace (new-space))

!(import! &self perception)
!(import! &self rules)

(= (kbInitializer $kb)
   (let* (
      ($rules (collapse (get-atoms &ruleSpace)))
      ($modulators (collapse (get-atoms &modulatorSpace)))
      ($demands (collapse (get-atoms &demandSpace)))
      ($partialKb (union-atom $rules $modulators))
      ($kbExp (union-atom $partialKb $demands))
      ($_ (collapse (let $atom (superpose $kbExp) (add-atom $kb $atom))))
   )
   ()
   )
)

(= (cognitiveStep)
   (let* (
      ($_ (updatePerception &perceptionSpace))
      ($_ (perceptionToDemands &perceptionSpace &demandSpace))
      
      ($demands (queryAll &demandSpace demand))
      ; ($_ (println! (Demands: $demands)))
      
      ($currDemand (getLeastSatisfiedDemandEpsilonGreedy &demandSpace))
      ; ($_ (println! (Selected-Demand: $currDemand)))
      
      ((demand $demandName $minVal $maxVal $demandValue) $currDemand)
      
      ($goalObj (minecraftGoalSelector $demandName))
      ((Goal $goal $goalVal1 $goalVal2) $goalObj)
      ($_ (println! (Selected-Goal: $goal)))
      
      
      (($actions $id) (actionPlanner &ruleSpace $goal))
      ($_ (println! (Planned Actions: $actions)))
      
      ($result (performAction $actions))
      ; ($_ (println! (Action Result: $result)))
      ($_ (updateRule $id $result &ruleSpace))
      
      ;; To be implemented later - Update modulators based on demands and action results
      ;; ($_ (modulatorUpdaterAgent &modulatorSpace $))
   )
   (Step Completed)
   )
)


(= (cognitiveLoop $maxSteps $currentStep)
   (if (> $currentStep $maxSteps)
      ()
      (let* (
         ($_ (println! (Step $currentStep / $maxSteps)))
         ($_ (cognitiveStep))
      )
      (cognitiveLoop $maxSteps (+ $currentStep 1))
      )
   )
)


(= (runInteractive)
   (let $_ (println! (Minecraft OpenPsi Agent Starting ...))
   (cognitiveLoop 1 1))
)




(= (addObservation $space) (
   let $atoms (py-call (utils.getObservation))
   (addIndividualObservation $atoms $space)
))


!(py-call (utils.connectToMinecraft))
!(addObservation &perceptionSpace)
; !(collapse(get-atoms &perceptionSpace))

!(insert-modulators &modulatorSpace)
!(collapse(kbInitializer &kb))
; !(collapse(get-atoms &kb))

; !(get-atoms &modulatorSpace)

!(runInteractive)