import camelcaseKeys from 'camelcase-keys'

import {extractYearRemovedStats} from '$lib/util/stats'

import rawStats from '$data/summary_stats.json'

// FIXME: bbox previously aliased to bounds
const coreStats = camelcaseKeys(rawStats)

export const summaryStats = {
    ...coreStats,
    removedBarriersByYear: extractYearRemovedStats(
      coreStats.removedDamsByYear || '',
      coreStats.removedSmallBarriersByYear || ''
    ),
}
