; Standalone tests for additional perception.metta query helpers.
; These cover observation collections that rule contexts and action planning read.
!(import! &self ../../perception)

; Fake observation with repeated action status, inventory, and multiple entity types.
!(add-atom &queryPerceptionSpace (onGround True))
!(add-atom &queryPerceptionSpace (actionStatus move_forward 1.0))
!(add-atom &queryPerceptionSpace (actionStatus jump 0.0))
!(add-atom &queryPerceptionSpace (hasItem apple 3))
!(add-atom &queryPerceptionSpace (hasItem bread 2))
!(add-atom &queryPerceptionSpace (hasItem stone 8))
!(add-atom &queryPerceptionSpace (nearEntity cow 6.0 6 64 6))
!(add-atom &queryPerceptionSpace (nearEntity zombie 4.0 2 64 2))
!(add-atom &queryPerceptionSpace (nearEntity cow 3.0 3 64 3))

; Direct collection helpers should return all matching symbolic facts.
!(test (getOnGround &queryPerceptionSpace) True)
!(test (getActionStatus &queryPerceptionSpace) ((actionStatus move_forward 1.0) (actionStatus jump 0.0)))
!(test (getNearbyEntities &queryPerceptionSpace cow) ((nearEntity cow 6.0 6 64 6) (nearEntity cow 3.0 3 64 3)))

; Inventory food extraction should keep edible items and ignore non-food blocks.
!(test (getInventoryFood &queryPerceptionSpace) ((FoodItem apple 3) (FoodItem bread 2)))
!(test (hasEdibleFood &queryPerceptionSpace) True)

; Food-animal helpers are used by higher-level food search behavior.
!(test (isFoodAnimal cow) True)
!(test (isFoodAnimal zombie) False)
!(test (getNearestFoodAnimal &queryPerceptionSpace) (cow 6.0))
!(test (getNearestFoodAnimal &emptyAnimalSpace) ())
