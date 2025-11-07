 
!(import! &self ../normalization)

; Test sigmoid function
!(test (sigmoid 0) 0.5)
!(test (sigmoid 1) 0.7310585786300049)
!(test (sigmoid -1) 0.2689414213699951)

; Test normalize function
!(test (normalize 0.5) 0.5) 
!(test (normalize 2) 0.8807970779778823)  
!(test (normalize -2) 0.11920292202211757)

; Test normalizeWithSpecificRange
!(test (normalizeWithSpecificRange 0.5 0 10) 0.5)  
!(test (normalizeWithSpecificRange 2 0 10) 2)
!(test (normalizeWithSpecificRange -2 0 10) 1.1920292202211757)  
!(test (normalizeWithSpecificRange 5 10 20) 19.93307149075715)

; Test sumAtom
!(assertEqual (sumAtom (5 4 3)) 12)
!(assertEqual (sumAtom ()) 0)  
!(assertEqual (sumAtom (1)) 1)

; Test mean
!(test (mean (5 4 3)) 4)
!(test (mean ()) 0)  
!(test (mean (2)) 2)

; Test sumSquaredDifference
!(test (sumSquaredDifference (5 4 3) 4) 2)
!(test (sumSquaredDifference (2) 2) 0)  
!(test (sumSquaredDifference () 0) 0)

; Test standardDeviation
!(test (standardDeviation (5 4 3)) 0.816496580927726)  
!(test (standardDeviation ()) ())  
!(test (standardDeviation (2)) 0.0)
!(test (standardDeviation (2 2 2)) 0.0)

; Test normalizeUsingMinMax
!(test (normalizeUsingMinMax 6.0 1 10) 0.5555555555555556)   
!(test (normalizeUsingMinMax 0.5 0 1) 0.5)   
!(test (normalizeUsingMinMax 5 5 5) 0) 

; Test normalizeList
!(test (normalizeList (5 4 3)) (1.0 0.5 0.0))
!(test (normalizeList (0 40 45 92 100)) (0.0 0.4 0.45 0.92 1.0))
!(test (normalizeList ()) ())   
!(test (normalizeList (2)) (0.0))   
!(test (normalizeList (2 2 2)) (0.0 0.0 0.0)) 

; Test normalizeUsingZScore
!(test (normalizeUsingZScore 6.0 4 0.816496580927726) 2.449489742783178)   
!(test (normalizeUsingZScore 0.5 0 1) 0.5)   
!(test (normalizeUsingZScore 5 5 0) 0)

; Test normalizeUsingZScoreDataset
!(test (normalizeUsingZScoreDataset 6.0 (5 4 3)) 2.449489742783178)  
!(test (normalizeUsingZScoreDataset 0.5 (5 4 3)) -4.286607049870562)   
!(test (normalizeUsingZScoreDataset 2 ()) ())   
!(test (normalizeUsingZScoreDataset 2 (2)) 0.0)   
!(test (normalizeUsingZScoreDataset 2 (2 2 2)) 0.0)
 