export type BarrierTypeSingular = 'dam' | 'small_barrier' | 'road_crossing' | 'waterfall'
export type BarrierTypePlural = 'dams' | 'small_barriers' | 'road_crossings' | 'waterfalls'
export type NetworkType =
	| BarrierTypePlural
	| 'combined_barriers'
	| 'largefish_barriers'
	| 'smallfish_barriers'

// used for explore / restoration pages
export type FocalBarrierType = 'dams' | 'small_barriers' | 'combined_barriers'

// set of filter values per filter field
export type Filters = Record<string, Set<string | number>>
