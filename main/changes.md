# OpenPsi Pluggable Architecture Plan

This document describes the changes needed to make OpenPsi's modulators, demands, and action selection pluggable and configurable.

## Overview

The current implementation has hardcoded:
- 6 modulators with fixed update formulas
- 3 demands with hardcoded initialization
- 9 emotions with fixed modulator dependencies
- Action selection via a planner function

The goal is to make these components configurable via registries, allowing new modulators, demands, and emotions to be added by editing configuration only (plus optional custom update functions).

---

## File Changes Summary

| File | Action | Purpose |
|------|--------|---------|
| `psi-config.metta` | **CREATE** | Registry definitions for modulators, demands, emotions |
| `modulator.metta` | Modify | Add registry-based initialization |
| `modulator-updater.metta` | Modify | Add generic update loop, per-modulator compute functions |
| `demands.metta` | Modify | Add registry-based initialization |
| `feeling-updaters.metta` | Modify | Add generic emotion calculation |
| `feedback-loop.metta` | Modify | Use generic functions, integrate Thompson Sampling |
| `use-cases/curious-agent/setup-kb.metta` | Modify | Use new initialization |

---

## Phase 1: Create Registry Configuration

### New File: `main/psi-config.metta`

```metta
; ============================================
; OpenPsi Configuration Registry
; ============================================
; 
; This file defines all pluggable components of the OpenPsi motivation system.
; To add new components, simply add entries to these registries.
;

; -------------------------------------------
; MODULATOR REGISTRY
; -------------------------------------------
; Format: (modulator-name default-value (dependency-demands...))
;
; Dependencies determine which demand values affect this modulator's update.
; Each modulator needs a corresponding `compute-modulator-value` function 
; defined in modulator-updater.metta
;
(= (modulator-registry)
    (
        (arousal 0.5 (competence energy))
        (securing-threshold 0.5 (certainty integrity))
        (selection-threshold 0.5 (competence))
        (positive-valence 0.5 ())
        (goal-directedness 0.5 ())
        (resolution-level 0.5 ())
    )
)

; -------------------------------------------
; DEMAND REGISTRY
; -------------------------------------------
; Format: (demand-name min-value max-value)
;
; Demands are initialized with their min-value as the starting value.
; Each demand needs a corresponding `update-demand` function 
; defined in demand-updater.metta
;
(= (demand-registry)
    (
        (competence 0.3 0.5)
        (affiliation 0.5 0.6)
        (energy 0.4 0.7)
    )
)

; -------------------------------------------
; EMOTION REGISTRY
; -------------------------------------------
; Format: (emotion-name (num-modulators indicator-list))
;
; Indicators: high, low, medium, extremely-high, extremely-low, undefined
; Undefined means the modulator is not used in that emotion's calculation.
;
; The order of indicators must match: arousal, securing-threshold, 
; selection-threshold, resolution-level, positive-valence (pleasure)
;
(= (emotion-registry)
    (
        (happiness (4 high low undefined high high))
        (sadness (4 low high undefined extremely-low extremely-low))
        (anger (4 high low undefined low extremely-low))
        (fear (4 extremely-low extremely-high low undefined extremely-low))
        (excitement (4 high low undefined low high))
        (pride (4 undefined low high high high))
        (love (4 undefined extremely-low extremely-high extremely-high extremely-high))
        (hate (4 extremely-high extremely-low extremely-high undefined extremely-low))
        (gratitude (2 undefined undefined undefined high high))
    )
)

; -------------------------------------------
; THOMPSON SAMPLING CONFIG
; -------------------------------------------
; Format: (action demand prior-alpha prior-beta)
;
; Each action is associated with a demand it satisfies.
; Prior-alpha and prior-beta are Beta distribution parameters.
;
(= (thompson-action-registry)
    (
        (initiate-dialogue affiliation 1.0 1.0)
        (elicit-response affiliation 1.0 1.0)
        (interpret-mood competence 1.0 1.0)
        (ask-activities energy 1.0 1.0)
        (discuss-random-topic energy 1.0 1.0)
        (share-joke energy 1.0 1.0)
        (offer-advice competence 1.0 1.0)
        (summarize-preferences integrity 1.0 1.0)
    )
)

; -------------------------------------------
; INDICATOR THRESHOLDS
; -------------------------------------------
; These thresholds determine how modulator values map to indicators.
; Modify these to tune emotion sensitivity.
;
(= (indicator-thresholds)
    (
        (extremely-low 0.15)
        (low 0.30)
        (medium 0.50)
        (high 0.70)
        (extremely-high 0.85)
    )
)
```

---

## Phase 2: Modify Modulator Module

### File: `main/modulator/modulator.metta`

**Add these functions after the existing code:**

```metta
; ============================================
; REGISTRY-BASED INITIALIZATION
; ============================================

;(: initialize-modulators (-> hyperon::space::DynSpace empty))
(= (initialize-modulators $space)
    (init-modulators-rec $space (modulator-registry)))

(= (init-modulators-rec $space ())
    ())

(= (init-modulators-rec $space (($name $default $deps) . $rest))
    (let* (
        ($_ (add-atom $space (modulator $name $default)))
    )
        (init-modulators-rec $space $rest)
    ))

; Get modulator config from registry
(= (get-modulator-config $name)
    (get-mod-config $name (modulator-registry)))

(= (get-mod-config $name (($n $default $deps) . $rest))
    (if (== $name $n)
        ($default $deps)
        (get-mod-config $name $rest)))

(= (get-mod-config $name ())
    (Error (modulator-not-in-registry $name)))

; List all registered modulator names
(= (list-modulators)
    (list-mods (modulator-registry)))

(= (list-mods (($name $default $deps) . $rest))
    ($name . (list-mods $rest)))

(= (list-mods ())
    ())
```

---

## Phase 3: Modify Modulator Updater

### File: `main/mind-agents/modulator-updater/modulator-updater.metta`

**Replace the existing hardcoded functions with:**

```metta
; ============================================
; GENERIC MODULATOR UPDATE FUNCTIONS
; ============================================

; Main entry point - updates all modulators from registry
(= (update-all-modulators $modSpace $demSpace)
    (update-mods-helper $modSpace $demSpace (modulator-registry)))

(= (update-mods-helper $modSpace $demSpace ())
    $modSpace)

(= (update-mods-helper $modSpace $demSpace (($name $default $deps) . $rest))
    (let* (
        ($_ (update-single-modulator $modSpace $demSpace $name $deps))
    )
        (update-mods-helper $modSpace $demSpace $rest)))

; Update a single modulator by fetching its dependencies and computing new value
(= (update-single-modulator $modSpace $demSpace $modName $deps)
    (let* (
        ($demVals (fetch-dem-vals $demSpace $deps))
        ($newVal (compute-modulator-value $modName $demVals))
        ($newVal' (normalizeWithSpecificRange $newVal 0.0 1.0))
        ($oldMod (fetch-modulator $modSpace $modName))
        ($_ (update-atom $modSpace $oldMod (modulator $modName $newVal')))
    ) ()))

; Fetch demand values for given dependency list
(= (fetch-dem-vals $space ())
    ())

(= (fetch-dem-vals $space ($dep . $rest))
    (let $val (fetchDemandVal $space $dep)
        ($val . (fetch-dem-vals $space $rest))))

; ============================================
; PER-MODULATOR COMPUTE FUNCTIONS
; ============================================
; Add a new function here for each modulator in the registry.
; The function takes a list of dependency demand values.
;

(= (compute-modulator-value arousal ($competence $energy))
    (* (/ $competence (+ $competence 0.5))
       (/ $energy (+ 0.05 $energy))))

(= (compute-modulator-value securing-threshold ($certainty $integrity))
    (let* (
        ($integrity 0.5)
        ($certainty 0.5)
    )
        (* (/ $certainty (+ $certainty 0.05))
           (pow-math $integrity 3))))

(= (compute-modulator-value selection-threshold ($competence))
    (fuzzy_equal $competence 1 15))

; Fallback for modulators without dependencies
(= (compute-modulator-value $name ())
    0.5)

; ============================================
; LEGACY FUNCTION (for backward compatibility)
; ============================================
; Keep this until all callers are updated
(= (modulatorUpdaterAgent $modulatorSpace $competence-demand $affiliation-demand $energy-demand)
    (update-all-modulators $modulatorSpace &demandspace))
```

---

## Phase 4: Modify Demands Module

### File: `main/demands/demands.metta`

**Add these functions:**

```metta
; ============================================
; REGISTRY-BASED INITIALIZATION
; ============================================

;(: initialize-demands (-> hyperon::space::DynSpace empty))
(= (initialize-demands $space)
    (init-demands-rec $space (demand-registry)))

(= (init-demands-rec $space ())
    ())

(= (init-demands-rec $space ((demand-config $name $min $max) . $rest))
    (let* (
        ($_ (add-atom $space (demand $name $min $max $min)))
    )
        (init-demands-rec $space $rest)))

;(: initialize-demands-with-values (-> hyperon::space::DynSpace empty))
; Alternative: Initialize with specific starting values per demand
(= (initialize-demands-with-values $space)
    (init-demands-vals-rec $space (demand-initial-values)))

(= (demand-initial-values)
    (
        (competence 0.3 0.5 0.95)
        (affiliation 0.5 0.6 0.55)
        (energy 0.4 0.7 0.85)
    ))

(= (init-demands-vals-rec $space ())
    ())

(= (init-demands-vals-rec $space ((demand-config $name $min $max $val) . $rest))
    (let* (
        ($_ (add-atom $space (demand $name $min $max $val)))
    )
        (init-demands-vals-rec $space $rest)))

; Get demand config from registry
(= (get-demand-config $name)
    (get-dem-config $name (demand-registry)))

(= (get-dem-config $name ((demand-config $n $min $max) . $rest))
    (if (== $name $n)
        ($min $max)
        (get-dem-config $name $rest)))

(= (get-dem-config $name ())
    (Error (demand-not-in-registry $name)))

; List all registered demand names
(= (list-demands)
    (list-dems (demand-registry)))

(= (list-dems ((demand-config $name $min $max) . $rest))
    ($name . (list-dems $rest)))

(= (list-dems ())
    ())
```

---

## Phase 5: Modify Feeling Updaters

### File: `main/mind-agents/feeling-updaters/feeling-updaters.metta`

**Add these functions:**

```metta
; ============================================
; GENERIC EMOTION CALCULATION
; ============================================

; Main entry point - calculate all emotions from registry
(= (calculate-all-feelings $modSpace)
    (calc-feelings-helper $modSpace (emotion-registry)))

(= (calc-feelings-helper $modSpace ())
    ())

(= (calc-feelings-helper $modSpace (($emotion $params) . $rest))
    (let $value (generic-feeling-calculator $modSpace $emotion $params)
        (($emotion $value) . (calc-feelings-helper $modSpace $rest))))

; Generic feeling calculator from registry config
(= (generic-feeling-calculator $modSpace $emotionName ($numMods $a $b $c $d $e))
    (let* (
        ($arousal (fetch-mod-val $modSpace arousal))
        ($securing (fetch-mod-val $modSpace securing-threshold))
        ($selection (fetch-mod-val $modSpace selection-threshold))
        ($resolution (fetch-mod-val $modSpace resolution-level))
        ($pleasure (get_pleasure_value))
        
        ($f-a (indicator-to-feeling $arousal $a))
        ($f-b (indicator-to-feeling $resolution $b))
        ($f-c (indicator-to-feeling $securing $c))
        ($f-d (indicator-to-feeling $selection $d))
        ($f-e (indicator-to-feeling $pleasure $e))
        
        ($total (+ $f-a (if (== $b undefined) 0 $f-b)
                   (if (== $c undefined) 0 $f-c)
                   (if (== $d undefined) 0 $f-d)
                   (if (== $e undefined) 0 $f-e)))
    )
        (/ $total $numMods)))

(= (fetch-mod-val $space $name)
    (let (modulator $n $v) (fetch-modulator $space $name) $v))

; Convert indicator name to threshold comparison
(= (indicator-to-feeling $value undefined)
    0)

(= (indicator-to-feeling $value extremely-low)
    (fuzzy_less_than $value (modulator_extremely_low_threshold) 50))

(= (indicator-to-feeling $value low)
    (fuzzy_less_than $value (modulator_low_threshold) 50))

(= (indicator-to-feeling $value medium)
    (fuzzy_equal $value (modulator_medium_threshold) 50))

(= (indicator-to-feeling $value high)
    (fuzzy_greater_than $value (modulator_high_threshold) 50))

(= (indicator-to-feeling $value extremely-high)
    (fuzzy_greater_than $value (modulator_extremely_high_threshold) 50))

; ============================================
; LEGACY FUNCTIONS (for backward compatibility)
; ============================================
; Keep these until all callers are updated
(= (happinessFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace happiness 
        (4 high low undefined high high)))

(= (sadnessFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace sadness
        (4 low high undefined extremely-low extremely-low)))

(= (angerFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace anger
        (4 high low undefined low extremely-low)))

(= (fearFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace fear
        (4 extremely-low extremely-high low undefined extremely-low)))

(= (excitementFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace excitement
        (4 high low undefined low high)))

(= (prideFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace pride
        (4 undefined low high high high)))

(= (loveFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace love
        (4 undefined extremely-low extremely-high extremely-high extremely-high)))

(= (hateFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace hate
        (4 extremely-high extremely-low extremely-high undefined extremely-low)))

(= (gratitudeFeelingUpdater $modSpace)
    (generic-feeling-calculator $modSpace gratitude
        (2 undefined undefined undefined high high)))
```

---

## Phase 6: Add Thompson Sampling Module

### New File: `main/mind-agents/thompson-sampling/thompson-sampling.metta`

```metta
; ============================================
; THOMPSON SAMPLING ACTION SELECTION
; ============================================
;
; Thompson Sampling for OpenPsi implements Bayesian action selection
; using Beta distributions as priors for each (demand, action) pair.
;
; Workflow:
; 1. Sample from posterior Beta distribution for each action
; 2. Select action with highest sampled value
; 3. Execute action and observe reward
; 4. Update posterior: alpha += reward, beta += (1 - reward)
;

!(import! &self ../../demands/demands)
!(import! &self ../../psi-utilities/psi_utils)

; -------------------------------------------
; THOMPSON SAMPLING BELIEFS STORAGE
; -------------------------------------------

!(bind! &ts-beliefs (new-space))

; Initialize beliefs for all actions in registry
(= (initialize-thompson-beliefs)
    (init-ts-helper (thompson-action-registry)))

(= (init-ts-helper ())
    ())

(= (init-ts-helper (($action $demand $alpha $beta) . $rest))
    (let* (
        ($_ (add-atom &ts-beliefs (ts-belief $action $demand $alpha $beta)))
    )
        (init-ts-helper $rest)))

; -------------------------------------------
; SAMPLE FROM POSTERIOR
; -------------------------------------------

;(: thompson-sample (-> Symbol Number))
; Sample a single action using Thompson Sampling
(= (thompson-sample $action)
    (let (ts-belief $action $demand $alpha $beta) 
          (fetch-ts-belief $action)
        (sample-beta $alpha $beta)))

; Get belief for an action
(= (fetch-ts-belief $action)
    (match &ts-beliefs (ts-belief $action $d $a $b) 
           (ts-belief $action $d $a $b)))

; -------------------------------------------
; SELECT ACTION
; -------------------------------------------

;(: thompson-select (-> hyperon::space::DynSpace Expression Expression))
; Select action using Thompson Sampling, filtered by current demand
(= (thompson-select $ruleSpace $demandSpace $currentDemand)
    (let* (
        ($demandName (get-demand-from-expression $currentDemand))
        ($candidateActions (get-actions-for-demand $ruleSpace $demandName))
        ($samples (thompson-sample-all $candidateActions))
        ($selected (argmax-sample $samples))
    )
        $selected))

; Get the demand name from a demand expression
(= (get-demand-from-expression (demand $name $min $max $val))
    $name)

; Get all candidate actions for a demand
(= (get-actions-for-demand $ruleSpace $demandName)
    (collapse (match $ruleSpace 
        ((: $handle ((TTV $time (STV $bel $conf)) 
           (IMPLICATION_LINK (AND_LINK ((Goal $goalName $g1 $g2) $action)) $goal))) $val)
        ((Goal $goalName $g1 $g2) $action))))

; Sample all candidate actions
(= (thompson-sample-all ())
    ())

(= (thompson-sample-all ($action . $rest))
    (let $sample (thompson-sample $action)
        (($action . $sample) . (thompson-sample-all $rest))))

; Select action with highest sample value
(= (argmax-sample (($action $value)))
    $action)

(= (argmax-sample (($a $v) . $rest))
    (let $best (argmax-sample $rest)
        (let ($b $bv) $best
            (if (>= $v $bv) $a $b))))

; -------------------------------------------
; UPDATE BELIEFS
; -------------------------------------------

;(: thompson-update (-> Symbol Number))
; Update beliefs after observing reward (0 or 1)
(= (thompson-update $action $reward)
    (let* (
        ((ts-belief $action $demand $oldAlpha $oldBeta) (fetch-ts-belief $action))
        ($newAlpha (+ $oldAlpha $reward))
        ($newBeta (+ $oldBeta (- 1 $reward)))
        ($_ (remove-atom &ts-beliefs (ts-belief $action $demand $oldAlpha $oldBeta)))
        ($_ (add-atom &ts-beliefs (ts-belief $action $demand $newAlpha $newBeta)))
    )
        (ts-belief $action $demand $newAlpha $newBeta)))

; -------------------------------------------
; INTEGRATION WITH DEMAND SELECTION
; -------------------------------------------

;(: thompson-select-demand-action (-> hyperon::space::DynSpace hyperon::space::DynSpace Expression))
; Full selection: pick demand first, then pick action via Thompson Sampling
(= (thompson-select-demand-action $ruleSpace $demandSpace)
    (let* (
        ($leastSatisfied (fetchLeastSatisfiedDemand $demandSpace))
        ($selectedAction (thompson-select $ruleSpace $demandSpace $leastSatisfied))
    )
        ($leastSatisfied $selectedAction)))

; -------------------------------------------
; LEGACY COMPATIBILITY
; -------------------------------------------
; Wrapper to use Thompson Sampling as drop-in for planner
(= (ts-planner $ruleSpace $state $goal)
    (let* (
        ($goalName (get-goal-name $goal))
        ($actions (collapse (match $ruleSpace
            ((: $handle ((TTV $time (STV $bel $conf)) 
               (IMPLICATION_LINK (AND_LINK ((Goal $goalName $g1 $g2) $action)) $goal))) $val)
            $action)))
    )
        (if (== $actions ())
            ()
            (thompson-sample-all $actions))))
```

---

## Phase 7: Modify Feedback Loop

### File: `main/feedback-loop/feedback-loop.metta`

**Replace the hardcoded modulator/demand/feeling calls (lines 320-335):**

**BEFORE:**
```metta
$competenceDemand (getDemandByName &demandspace competence)) 
$affiliationDemand (getDemandByName &demandspace affiliation))
$energyDemand (getDemandByName &demandspace energy))
($_ (modulatorUpdaterAgent &modulator-space $competenceDemand $affiliationDemand $energyDemand))
($happinessValue (happinessFeelingUpdater &modulator-space))
($sadnessValue (sadnessFeelingUpdater &modulator-space))
($angerValue (angerFeelingUpdater &modulator-space))
($fearValue (fearFeelingUpdater &modulator-space))
($excitementValue (excitementFeelingUpdater &modulator-space))
($loveValue (loveFeelingUpdater &modulator-space))
($hateValue (hateFeelingUpdater &modulator-space))
($gratitude (gratitudeFeelingUpdater &modulator-space))
```

**AFTER:**
```metta
; Update all modulators based on current demand values
($_ (update-all-modulators &modulator-space &demandspace))

; Calculate all emotions
($emotions (calculate-all-feelings &modulator-space))
```

**Replace action selection (line 316):**

**BEFORE:**
```metta
($actions (planner &ruleSpace $state $goal))
```

**AFTER:**
```metta
; Thompson Sampling action selection
($actions (ts-planner &ruleSpace $state $goal))
```

---

## Phase 8: Update Curious Agent Setup

### File: `use-cases/curious-agent/setup-kb.metta`

**Replace hardcoded demand initialization (lines 168-178):**

**BEFORE:**
```metta
(= (populateDemandSpace $demandspace) 
   (let $demand (superpose 
      (
        (demand affiliation 0.5 0.6 0.55)
        (demand energy      0.4 0.7 0.85)
        (demand competence  0.3 0.5 0.95)
      )
    )
    (add-atom $demandspace $demand)
))
```

**AFTER:**
```metta
(= (populateDemandSpace $demandspace)
    (initialize-demands-with-values $demandspace))
```

**Add modulator initialization:**

```metta
(= (populateModulatorSpace $modspace)
    (initialize-modulators $modspace))
```

---

## How to Add New Components

### Adding a New Modulator

**1. Add to `psi-config.metta` (modulator-registry):**
```metta
(= (modulator-registry)
    (
        (arousal 0.5 (competence energy))
        (new-modulator 0.5 (competence energy))  ; NEW
        ; ... existing modulators ...
    )
)
```

**2. Add compute function in `modulator-updater.metta`:**
```metta
(= (compute-modulator-value new-modulator ($comp $ene))
    (* $comp (- 1 $ene)))
```

### Adding a New Demand

**1. Add to `psi-config.metta` (demand-registry):**
```metta
(= (demand-registry)
    (
        (competence 0.3 0.5)
        (new-demand 0.2 0.8)  ; NEW
        ; ... existing demands ...
    )
)
```

**2. Add to `demand-initial-values` in `demands.metta`:**
```metta
(= (demand-initial-values)
    (
        (competence 0.3 0.5 0.95)
        (new-demand 0.2 0.8 0.5)  ; NEW
        ; ... existing demands ...
    ))
```

### Adding a New Emotion

**1. Add to `psi-config.metta` (emotion-registry):**
```metta
(= (emotion-registry)
    (
        (happiness (4 high low undefined high high))
        (new-emotion (3 high high undefined undefined high))  ; NEW
        ; ... existing emotions ...
    )
)
```

### Adding a New Action (Thompson Sampling)

**1. Add to `psi-config.metta` (thompson-action-registry):**
```metta
(= (thompson-action-registry)
    (
        (initiate-dialogue affiliation 1.0 1.0)
        (new-action competence 1.0 1.0)  ; NEW
        ; ... existing actions ...
    )
)
```

---

## File Locations

```
main/
├── psi-config.metta                    # NEW - Registry definitions
├── modulator/
│   └── modulator.metta                 # MODIFY - Add initialize-modulators
├── demands/
│   └── demands.metta                   # MODIFY - Add initialize-demands
├── mind-agents/
│   ├── modulator-updater/
│   │   └── modulator-updater.metta     # MODIFY - Add generic update loop
│   ├── feeling-updaters/
│   │   └── feeling-updaters.metta      # MODIFY - Add generic emotion calc
│   └── thompson-sampling/             # NEW - Thompson Sampling module
│       └── thompson-sampling.metta
└── feedback-loop/
    └── feedback-loop.metta             # MODIFY - Use generic functions
use-cases/
└── curious-agent/
    └── setup-kb.metta                  # MODIFY - Use new initialization
```

---

## Migration Path

To maintain backward compatibility during migration:

1. **Keep legacy functions** (marked with "LEGACY COMPATIBILITY" comments)
2. **New code uses generic functions** via registries
3. **Old code continues to work** via legacy wrappers
4. **Gradually migrate** callers to use new functions
5. **Remove legacy wrappers** once all callers are updated

---

## Testing Checklist

After implementation, verify:

- [ ] `initialize-modulators` creates all modulators from registry
- [ ] `initialize-demands` creates all demands from registry
- [ ] `update-all-modulators` updates every modulator correctly
- [ ] `calculate-all-feelings` returns values for all emotions
- [ ] Thompson Sampling selects actions based on sampled values
- [ ] `thompson-update` correctly updates Beta posterior
- [ ] Legacy functions still work for backward compatibility
- [ ] Adding a new modulator requires only registry + compute function
