export type SummaryUnit = {
	layer: string
	id: string
	state: string // may be blank
	dams: number
	rankedDams: number
	smallBarriers: number
	rankedSmallBarriers: number
	rankedLargefishBarriersDams: number
	rankedLargefishBarriersSmallBarriers: number
	rankedSmallfishBarriersDams: number
	rankedSmallfishBarriersSmallBarriers: number
	totalRoadCrossings: number

	removedDams: number
	removedDamsByYear: string
	removedDamsGainMiles: number
	removedSmallBarriers: number
	removedSmallBarriersByYear: string
	removedSmallBarriersGainMiles: number

	// not defined until populated dynamically
	removedBarriersByYear?: {
		label: string
		dams: number
		damsNoNetwork: number
		damsUpstreamMiles: number
		damsDownstreamMiles: number
		smallBarriers: number
		smallBarriersNoNetwork: number
		smallBarriersUpstreamMiles: number
		smallBarriersDownstreamMiles: number
	}[]
}
