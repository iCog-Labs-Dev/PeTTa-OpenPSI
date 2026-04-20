; OpenPsi central registry
;
; This file is intended to be the single place where pluggable OpenPsi
; components are declared. Runtime code can gradually be refactored to
; read these registries instead of hardcoding modulators, demands, and
; feelings in the main loop.

(: ModulatorConfig Type)
(: DemandConfig Type)
(: FeelingConfig Type)
(: ThresholdConfig Type)
(: PluginConfig Type)

; Registry format:
; (modulator-config <name> <default-value> <updater-symbol> (<dependency-demand-names>))
;
; Notes:
; - The first three modulators mirror the current updater logic.
; - `securing-threshold` is modeled with `(certainty integrity)` to preserve
;   the intended architecture, even though those demands are not yet fully
;   initialized in the current runtime path.
(= (modulator-registry)
    (
        (modulator-config arousal 0.5 activation-updater (competence energy))
        (modulator-config positive-valence 0.5 positive-valence-updater ())
        (modulator-config selection-threshold 0.5 selection-threshold-updater (competence))
        (modulator-config securing-threshold 0.5 securing-threshold-updater (certainty integrity))
        (modulator-config goal-directedness 0.5 goal-directedness-updater ())
        (modulator-config resolution-level 0.5 resolution-level-updater ())
    )
)

; Registry format:
; (demand-config <name> <min> <max> <initial-value> <updater-symbol>)
;
; Notes:
; - The first three entries mirror the current curious-agent bootstrap.
; - `certainty` and `integrity` are included because other parts of the codebase
;   already reference them as domain concepts, but they are not fully active yet.
(= (demand-registry)
    (
        (demand-config affiliation 0.5 0.6 0.55 affiliation-demand-updater)
        (demand-config energy 0.4 0.7 0.85 energy-demand-updater)
        (demand-config competence 0.3 0.5 0.95 competence-demand-updater)
        (demand-config certainty 0.3 0.7 0.5 certainty-demand-updater)
        (demand-config integrity 0.3 0.7 0.5 integrity-demand-updater)
    )
)

; Feeling registry format:
; (feeling-config <name> (<activation> <resolution> <securing> <selection> <pleasure>) <used-count>)
;
; Indicator vocabulary:
; - extremely-low
; - low
; - medium
; - high
; - extremely-high
; - undefined
(= (feeling-registry)
    (
        (feeling-config happiness (high low undefined high high) 4)
        (feeling-config sadness (low high undefined extremely-low extremely-low) 4)
        (feeling-config anger (high low undefined low extremely-low) 4)
        (feeling-config fear (extremely-low extremely-high low undefined extremely-low) 4)
        (feeling-config excitement-high (high low undefined low extremely-high) 4)
        (feeling-config excitement-low (high low undefined low extremely-low) 4)
        (feeling-config pride (undefined low high high high) 4)
        (feeling-config love (undefined extremely-low extremely-high extremely-high extremely-high) 4)
        (feeling-config hate (extremely-high extremely-low extremely-high undefined extremely-low) 4)
        (feeling-config gratitude (undefined undefined undefined high high) 2)
    )
)

; Threshold registry for mapping modulator values to feeling dimensions.
(= (indicator-threshold-registry)
    (
        (threshold-config extremely-low 0.15)
        (threshold-config low 0.30)
        (threshold-config medium 0.50)
        (threshold-config high 0.70)
        (threshold-config extremely-high 0.85)
    )
)

; Optional plugin registry placeholder.
; A later refactor can populate this with external config files or use-case
; specific component bundles.
(= (plugin-registry)
    ()
)
