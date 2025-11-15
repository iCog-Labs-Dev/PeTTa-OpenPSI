;; Math utilities for Metta

; (: isBetween (-> Number Number Number Bool))
(= (isBetween $val $low $high) (and (>= $val $low) (<= $val $high)))

; (: round (-> Number Number Number))
(= (round-sig $num $sig) (py-call ("round" $num $sig)))

(= (getRandomInt $a $b) (py-call ("random.randint" $a $b)))

; (: getRandom (-> Number))
(= (getRandom) (py-call ("random.random")))

; (: natural-log (-> Number Number))
(= (natural-log $x) (py-call ("math.log" $x)))

; (: sampleEngine (-> Number Number Number Number Number Number))
(= (sampleEngine $alpha $beta $a $b $gamma) (
    let* (
        ($u1 (getRandom))
        ($u2 (getRandom))
        ($v (* $beta (natural-log (/ $u1 (- 1 $u1)))))
        ($w (* $a (exp $v)))
        ($temp (natural-log (/ $alpha (+ $b $w))))
        ($left (+ (* $alpha $temp) (* $gamma $v)))
        ($right (+ (natural-log 4) (natural-log (* (* $u1 $u1) $u2))))
    ) (if (>= $left $right)
        (round-sig (/ $w (+ $b $w)) 4)
        (sampleEngine $alpha $beta $a $b $gamma)
    )
))

; (: betaSample (-> Number Number Number))
(= (betaSample $a $b) (
    let* (
        ($alpha (+ $a $b))
        ($beta (if (<= (min $a $b) 1) (max (/ 1 $a) (/ 1 $b)) (sqrt-math (/ (- $alpha 2) (- (* 2 (* $a $b)) $alpha))))) 
        ($gamma (/ (+ $a 1) $beta))
    ) (sampleEngine $alpha $beta $a $b $gamma)
))