export type SummaryUnit = {
	layer: string
	id: string
	dams: number
	rankedDams: number
	smallBarriers: number
	rankedSmallBarriers: number
	rankedLargefishBarriersDams: number
	rankedLargefishBarriersSmallBarriers: number
	rankedSmallfishBarriersDams: number
	rankedSmallfishBarriersSmallBarriers: number
	totalRoadCrossings: number

	// not defined until populated dynamically
	removedBarriersByYear?: {
		label: string
		dams: number
		damsNoNetwork: number
		damsGainMiles: number
		smallBarriers: number
		smallBarriersNoNetwork: number
		smallBarriersGainMiles: number
	}[]
}
