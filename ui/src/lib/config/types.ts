export type BarrierTypeSingular = 'dam' | 'small_barrier' | 'road_crossing' | 'waterfall'
export type BarrierTypePlural = 'dams' | 'small_barriers' | 'road_crossings' | 'waterfalls'
export type NetworkType =
	| BarrierTypePlural
	| 'combined_barriers'
	| 'largefish_barriers'
	| 'smallfish_barriers'

// used for explore / restoration pages
export type FocalBarrierType = 'dams' | 'small_barriers' | 'combined_barriers'

// list of summary unit IDs per summary unit layer: {<layer>: [unit1,...]}
export type SummaryUnits = Record<string, string[] | number[]>

// set of filter values per filter field
export type Filters = Record<string, Set<string | number>>
