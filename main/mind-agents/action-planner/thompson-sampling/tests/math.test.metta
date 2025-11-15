!(import! &self ../math)

; Unit tests for math functions
!(test (isBetween 5 1 10) True)
!(test (isBetween 0 1 10) False)

!(test (round 3.14159 2) 3.14)

!(test (let $val (getRandomInt 1 3) (isBetween $val 1 3)) True)
!(test (let $val (getRandom) (isBetween $val 0 1)) True)
!(test (natural-log 1) 0.0)
!(test (sqrt-math 4) 2.0)
!(test (exp 0) 1.0)

!(test (let $val (betaSample 20.0 10.0) (isBetween $val 0 1)) True)