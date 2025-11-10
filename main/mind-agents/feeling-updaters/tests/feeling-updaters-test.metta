!(import! &self ../../../../utils)
!(import! &self ../../../../psi-utilities/psi_utils)
!(import! &self ../feeling-updaters)
; !(import! &self ../../../modulator/modulator)

!(bind! &test-space (new-space))

!(insert-modulators &test-space)


!(test (modulator_to_feeling_dimension 0.85 1) 1)
!(test (feeling_calculator &test-space 1 1 1 1 1 5) 0.2666666666666667)
!(test (happinessFeelingUpdater &test-space) 0.25000000000000006)
!(test (sadnessFeelingUpdater &test-space) 0.15350877192982454)
!(test (angerFeelingUpdater &test-space) 0.2017543859649123)
!(test (hateFeelingUpdater &test-space) 0.10526315789473686)
!(test (gratitudeFeelingUpdater &test-space) 0.3333333333333334)
!(test (excitementFeelingUpdater &test-space) 0.2017543859649123)