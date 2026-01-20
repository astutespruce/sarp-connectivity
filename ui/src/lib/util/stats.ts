import { YEAR_REMOVED_BINS } from '$lib/config/constants'
import { isEmptyString } from '$lib/util/string'

const unpackYearRemoved = (text: string) => {
	if (isEmptyString(text)) {
		return Object.keys(YEAR_REMOVED_BINS).map(() => ({
			count: 0,
			countNoNetwork: 0,
			gainmiles: 0
		}))
	}

	return text.split(',').map((part) => {
		if (!part) {
			return { count: 0, gainmiles: 0 }
		}
		const [rawCount = '0', gainmiles = '0'] = part.split('|')
		const [count, countNoNetwork] = rawCount.split('/')
		return {
			count: parseFloat(count),
			countNoNetwork: countNoNetwork !== undefined ? parseFloat(countNoNetwork) : 0,
			gainmiles: parseFloat(gainmiles)
		}
	})
}

type YearRemovedBinStat = {
	count: number
	countNoNetwork: number
	gainmiles: number
}

export const extractYearRemovedStats = (
	removedDamsByYearText: string,
	removedSmallBarriersByYearText: string
) => {
	const removedDamsByYear = unpackYearRemoved(removedDamsByYearText)
	const removedSmallBarriersByYear = unpackYearRemoved(removedSmallBarriersByYearText)

	return Object.entries(YEAR_REMOVED_BINS)
		.map(([bin, label]) => {
			const {
				count: dams = 0,
				countNoNetwork: damsNoNetwork = 0,
				gainmiles: damsGainMiles = 0
			} = (removedDamsByYear[bin as keyof typeof removedDamsByYear] || {}) as YearRemovedBinStat
			const {
				count: smallBarriers = 0,
				countNoNetwork: smallBarriersNoNetwork = 0,
				gainmiles: smallBarriersGainMiles = 0
			} = (removedSmallBarriersByYear[bin as keyof typeof removedSmallBarriersByYear] ||
				{}) as YearRemovedBinStat
			return {
				label,
				dams,
				damsNoNetwork,
				damsGainMiles,
				smallBarriers,
				smallBarriersNoNetwork,
				smallBarriersGainMiles
			}
		})
		.reverse()
}

export const classifySARPScore = (score: number) => {
	// assumes -1 (NODATA) already filtered out
	if (score < 0.2) {
		return 'severe barrier'
	}
	if (score < 0.4) {
		return 'significant barrier'
	}
	if (score < 0.6) {
		return 'moderate barrier'
	}
	if (score < 0.8) {
		return 'minor barrier'
	}
	if (score < 1) {
		return 'insignificant barrier'
	}
	if (score >= 1) {
		return 'no barrier'
	}
	return 'not calculated'
}
