;; Helper functions that are going to be useful for writing any metta code
(: ~= (-> Atom Atom Bool))
(= (~= $a $b) (not (== $a $b)))

;; INFO: Uncomment for the use of MeTTaLog.
;; (: >= (-> Number Number Bool))
;; (= (>= $a $b) (or (== $a $b) (> $a $b)))

;Function to cocatinate two tuples (A B) (C D) ==> (A B C D)
(: cocatTuple (-> Expression Expression Expression))
(= (concatTuple $x $y)
    (union-atom $x $y)
)


;; It will decrement the input by 1.
(: decrement (-> Number Number))
(= (decrement $x) (- $x 1))

;; It will increment the input by 1.
(: increment (-> Number Number))
(= (increment $x) (+ $x 1))


; (: isMember (-> $a $aa Bool))
(= (isMember $x $list)
    ; (let $netVal (intersection-atom ($x) $list) (not (== $netVal ())))
    (let* (
        ($netVal (intersection-atom ($x) $list))
        ; ($_ (println! ("isMember check: " $x " in " $list " => " $netVal)))
    )
    (not (== $netVal ()))
    )
)
; This function assumes it receives a set1 and set2 expression as parameters.
; It then removes similar elements found in set2 that already exist in set1.
; The function uses isMember from general helpers functions.

(: setDifference (-> Expression Expression Expression))
(= (setDifference $set1 $set2) 
    (if (== $set1 ()) () ; Base case: return empty set when $set1 is empty
        (let* (
            ($head (car-atom $set1))  ; Extract the head of set1
            ($tail (cdr-atom $set1))  ; Extract the tail of set1
            ($newtail (setDifference $tail $set2))  ; Recursively process the tail
        )
            ; Check if the $head is in set2, if so, skip it

            (if (isMember $head $set2)
                $newtail 
                ; Otherwise, add the head to the new tail, avoiding unnecessary parentheses
                (if (== (get-metatype $newtail) Expression) (cons-atom $head $newtail) $head)  ; Avoid wrapping the head if it's already properly structured
            )
        )
    )
)

;; A helper function for the findAndReplace function.
;; It handles the replacement of a single atom.
(= (replace $old $new $current) (if (== $old $current) $new $current))

;; A function to replace a specific atom
;;    with a new one from a list of atoms.
;; INFO: This function needs to change so that it can preserve the
;;        operator's position when MeTTa version is upgraded.
(= (findAndReplace $old $new $list) 
  (if (== $list ())
   $list 
   (let* ( 
    ($head (car-atom $list)) 
    ($tail (cdr-atom $list)) 
    ($rest (findAndReplace $old $new $tail))
        ) 
  (if (== $head $old) 
    (union-atom ($new) $rest)
    (union-atom ($head) $rest) 

  ) 
)))



;; Apply a given function to every element of a tuple
(: map (-> (-> $a $b) $c $d))
(= (map $f $xs)
   (if (== $xs ())
       ()
       (let* (($h (car-atom $xs))
              ($t (cdr-atom $xs))
              ($fh ($f $h))
              ($ft (map $f $t)))
         (cons-atom $fh $ft))))


;; Add numbers in an atom list
(= (sum $list) (foldr + 0 $list))


;; Function to replace a given atom from a space.
; (: update-atom (-> Grounded Atom Atom (->)))
(= (update-atom $space $oatom $natom) 
    (let $_ (remove-atom $space $oatom)
        (add-atom $space $natom)
    ))

;; Function to replace a given atom from a space.
(: appendAtom (-> Atom Atom Atom))
(= (appendAtom $a $atom) (foldr cons-atom ($a) $atom))


;; Finds length of a tuple
(= (len $expr)
    (if (== $expr ())
        0
        (let $tail (cdr-atom $expr)
            (+ 1 (len $tail))
        )
    )
)
