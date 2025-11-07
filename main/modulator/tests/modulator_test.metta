!(import! &self ../modulator)
;!(import! &self ../../../psi-utilities/psi_uitls)

!(bind! &test-space (new-space))
!(insert-modulators &test-space)

!(test(normalize-value 6.0) 0.8571428571428571)
!(test(normalize-value 9.0) (ERROR (provide unique values)))
!(test (fetch-modulator &test-space securing-threshold) (modulator securing-threshold 0.5))
!(fetch-modulator &test-space securing-threshold)
!(fetch-modulator-val &test-space securing-threshold)
!(test (fetch-modulator-val &test-space securing-threshold) 0.5)
!(test (add-modulator &test-space (modulator custom 1.8)) (Error (value is incorrect) BadType))
!(test (add-modulator &test-space (modulator custom 0.8)) true)