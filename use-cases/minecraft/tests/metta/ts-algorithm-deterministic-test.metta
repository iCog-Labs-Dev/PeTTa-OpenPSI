; Standalone tests for deterministic helpers in ts-algorithm.metta.
; Random sampling paths are intentionally excluded from this unit test.
!(import! &self ../../ts-algorithm)

; Confidence/count and STV/Beta conversions are used before rule sampling.
!(test (confidenceToCount 0.5) 800.0)
!(test (countToConfindence 800.0) 0.5)
!(test (stvToBeta (0.5 0.5)) (400.0 400.0))
!(test (stvToBeta (0.25 0.2)) (50.0 150.0))

; Beta variance is deterministic and supports exploration-oriented rule choice.
!(test (getBetaVariance 2.0 2.0) 0.05)
!(test (getBetaVariance 1.0 3.0) 0.0375)

; updateAtom should replace a fact in a space without needing planner execution.
!(add-atom &updateAtomSpace (status old))
!(updateAtom &updateAtomSpace (status old) (status new))
!(test (collapse (match &updateAtomSpace (status $value) $value)) (new))
