; Standalone tests for perception.metta.
; These fake observation atoms model one Minecraft snapshot without calling Python,
; Vereya, or the live agent loop.
!(import! &self ../../perception)

; Fake perception facts: position, needs, inventory, and nearby entities.
!(add-atom &testPerceptionSpace (at 1.0 64.0 2.0))
!(add-atom &testPerceptionSpace (health 18.0))
!(add-atom &testPerceptionSpace (hunger 7.0))
!(add-atom &testPerceptionSpace (air 240.0))
!(add-atom &testPerceptionSpace (isDay True))
!(add-atom &testPerceptionSpace (hasItem apple 3))
!(add-atom &testPerceptionSpace (hasItem stone 10))
!(add-atom &testPerceptionSpace (nearEntity zombie 4.0 2 64 2))
!(add-atom &testPerceptionSpace (nearEntity apple 3.0 3 64 2))

; Basic getters should read the current symbolic observation exactly.
!(test (getPosition &testPerceptionSpace) (at 1.0 64.0 2.0))
!(test (getHealth &testPerceptionSpace) 18.0)
!(test (getHunger &testPerceptionSpace) 7.0)
!(test (getAir &testPerceptionSpace) 240.0)
!(test (isDaytime &testPerceptionSpace) True)

; Inventory and threat helpers are used later by context predicates and rules.
!(test (hostileNearBy &testPerceptionSpace) True)
!(test (hasItem &testPerceptionSpace apple) True)
!(test (hasItem &testPerceptionSpace bread) False)
!(test (getItemCount &testPerceptionSpace apple) 3)
!(test (getItemCount &testPerceptionSpace bread) 0)

; Urgency helpers normalize raw Minecraft values into OpenPsi-style pressure.
!(test (hungerUrgency &testPerceptionSpace) 0.65)
!(test (healthUrgency &testPerceptionSpace) 0.1)
!(test (airUrgency &testPerceptionSpace) 0.2)

; Food classification should distinguish useful survival items from blocks.
!(test (isEdible apple) True)
!(test (isEdible stone) False)
!(test (hasEdibleFood &testPerceptionSpace) True)
!(test (hasFoodNearby &testPerceptionSpace) True)
