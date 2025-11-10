
!(import! &self ../../../modulator/modulator)
!(import! &self ../../modulator-updater/modulator-updater)
!(import! &self modulator-updater-test-helpers)

; !(import! &self ../../../../utils)
; !(import! &self ../../../../psi-utilities/psi_utils)
; !(import! &self ../../../demands/demands)
; !(import! &self ../../../../psi-utilities/normalization)

!(bind! &demandspace (new-space))
!(bind! &modulator-space (new-space))

!(addDemand &demandspace energy 0.6)
!(addDemand &demandspace affiliation 0.5)
!(addDemand &demandspace competence 0.2)
; !(get-atoms &demandspace)

!(insert-modulators &modulator-space)

!(test (ActivationHelper 4 3 2) 4.8743169398907105)
!(test (SecuringThresholdHelper 4 3) 70)
!(test (SelectionThresholdHelper 3 4) 8.01639344262295)

!(test (compareModulatorValues (modulator arousal 0.5) (modulator arousal 0.5)) True)
!(test (compareModulatorValues (modulator selection-threshold 0.5) (modulator arousal 0.5)) False)
!(test (compareModulatorValues (modulator arousal 0.4) (modulator arousal 0.5)) False)
!(test (compareModulators &modulator-space &demandspace) True)
; !(compareModulators &modulator-space &demandspace)