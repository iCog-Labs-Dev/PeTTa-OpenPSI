;using sigmoid function
;doesn't require dataset statistics 

;declare e, euler's number 
(= (eulerNumber) 2.718281828459045)
;sigmoid function
(= (sigmoid $x)
   (/ 1.0 (+ 1.0 (pow-math (eulerNumber) (* -1.0 $x))))
)
;normalization function
(= (normalize $x)
   (if (and (>= $x 0.0) (<= $x 1.0))
       $x
       (sigmoid $x)
    )
)
; normalize to range [a, b]
(= (normalizeWithSpecificRange $x $a $b)
   (if (and (>= $x $a) (<= $x $b)) $x (+ $a (* (- $b $a) (sigmoid $x))))
)
;normalization using minmax
;normalize single value given min and max 
(= (normalizeUsingMinMax $x $min $max)
  (if (== $min $max)
    0
    (if (and (>= $x 0) (<= $x 1))
      $x
      (/ (- $x $min) (- $max $min))
    )
  )
)
;normalize list of values using min-max
;main
;base-case
;normalize list of values using min-max
;main
;base-case
(= (normalizeList ()) ())
(= (normalizeList $list)
  (if (== (size-atom $list) 0)
    ()  
    (let* (($min (min-atom $list))
          ($max (max-atom $list))
          ($normalized
            (if (== $min $max)
                (map-atom $list $x 0.0)  
                (map-atom $list $x (/ (- $x $min) (* 1.0 (- $max $min)))))))
      $normalized
    )
  )
)
;normalize using z-score
;given value,mean,standard deviation 
(= (normalizeUsingZScore $x $mean $standardDeviation)
  (if (== $standardDeviation 0)
    0
    (if (and (>= $x 0) (<= $x 1))
      $x
      (let $z (/ (- $x $mean) $standardDeviation)
        $z
      )
    )
  )
)
;normalize using z-score given value and dataset
; Compute sum of list using foldl-atom
(= (sumAtom $list)
  (foldl-atom $list 0 $acc $x (+ $acc $x)))

;mean
(= (mean $list)
  (let $len (size-atom $list)
    (if (== $len 0)
      0  
      (/ (sumAtom $list) $len)
    )
  )
)

;sum of squared differences  
(= (sumSquaredDifference $list $mean)
  (sumAtom (map-atom $list $x (* (- $x $mean) (- $x $mean))))
)

;standard deviation
(= (standardDeviation $list)
  (let $m (mean $list)
    (if (== $m ())
      ()   
      (let $len (size-atom $list)
        (if (== $len 0)
          ()   
          (sqrt-math (/ (sumSquaredDifference $list $m) $len))
        )
      )
    )
  )
)
;main
(= (normalizeUsingZScoreDataset $x $data)
  (let $m (mean $data)
    (if (== $m ())
      ()   
      (let $s (standardDeviation $data)
        (if (== $s ())
          ()   
          (if (== $s 0.0)
            0.0 
            (/ (- $x $m) $s))
        )
      )
    )
  )
)
