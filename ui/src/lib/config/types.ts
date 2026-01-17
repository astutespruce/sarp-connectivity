export type BarrierTypeSingular = 'dam' | 'small_barrier' | 'road_crossing' | 'waterfall'
export type BarrierTypePlural = 'dams' | 'small_barriers' | 'road_crossings' | 'waterfalls'
export type NetworkType =
	| BarrierTypePlural
	| 'combined_barriers'
	| 'largefish_barriers'
	| 'smallfish_barriers'

export type SummaryUnits = {
	[key: string]: (string | number)[]
}

export type Filters = {
	[key: string]: Set<string | number>
}
