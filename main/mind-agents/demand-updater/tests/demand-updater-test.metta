!(import! &self ../demand-updater)


; due to the randomness of CertaintyDemandUpdater and AffiliationDemandUpdater we have range of return values 
!(test (and (> (CertaintyDemandUpdater  (10 20 30  40 50) 25) 0.80) (< (CertaintyDemandUpdater  (10 20 30  40 50) 25) 1.07)) True)
!(test (and (> (AffiliationDemandUpdater  (10 20 30) 25) 0.74) (< (AffiliationDemandUpdater  (10 20 30) 25) 1.02)) True)
!(test (CompetenceDemandUpdater 12 20 ) 0.1182933591140401)
!(test (CompetenceDemandUpdater 12 4) 0.6)