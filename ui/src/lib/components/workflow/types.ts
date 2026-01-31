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
}

export type Status = { isLoading: boolean; error?: string | null }

export type Step = 'select-layer' | 'select-units' | 'filter' | 'results'
