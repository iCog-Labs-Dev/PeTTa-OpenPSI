!(import! &self ../../../utils)
!(import! &self ../emotion)

!(bind! &test-space (new-space))

;;Tests for emotion 
!(test (create-emotion &test-space (emotion new-emotion 0)) True)
;; !(get-emotions &test-space)
!(test (create-emotion &test-space (emotion new-emotion 5)) (ERROR is Available))
!(test (isAvailable? &test-space (emotion old-emotion 6)) False)
!(test (isAvailable? &test-space (emotion new-emotion 5)) True)
!(test (create-emotion &test-space old-emotion) (ERROR Wrong Format))
