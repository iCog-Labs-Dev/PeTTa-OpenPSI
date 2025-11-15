!(import! &self ../utils)
; !(import! &self ../math)

;; Unit tests for utility functions
!(test (confidenceToCount 0.5) 800.0)
!(test (countToConfindence 800.0) 0.5)

!(test (stvToBeta (0.25 0.5)) (200.0 600.0))
!(test (betaToSTV (200.0 600.0)) (0.25 0.501))

