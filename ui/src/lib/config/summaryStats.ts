import camelcaseKeys from 'camelcase-keys'

import { extractYearRemovedStats } from '$lib/util/stats'

// @ts-expect-error not creating types for the JSON object right now
import rawStats from '$data/summary_stats.json'

const coreStats = camelcaseKeys(rawStats)

export const summaryStats = {
	...coreStats,
	removedBarriersByYear: extractYearRemovedStats(
		coreStats.removedDamsByYear || '',
		coreStats.removedSmallBarriersByYear || ''
	)
}
