import { graphql, useStaticQuery } from 'gatsby'

import { extractYearRemovedStats } from 'components/Restoration/util'
import { groupBy } from 'util/data'

export const useSummaryData = () => {
  const {
    stats: { total, regions },
  } = useStaticQuery(graphql`
    query summaryQuery {
      stats: summaryStatsJson {
        total {
          dams
          rankedDams: ranked_dams
          rankedLargefishBarriersDams: ranked_largefish_barriers_dams
          rankedSmallfishBarriersDams: ranked_smallfish_barriers_dams
          reconDams: recon_dams
          removedDams: removed_dams
          removedDamsGainMiles: removed_dams_gain_miles
          removedDamsByYear: removed_dams_by_year
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          rankedSmallBarriers: ranked_small_barriers
          rankedLargefishBarriersSmallBarriers: ranked_largefish_barriers_small_barriers
          rankedSmallfishBarriersSmallBarriers: ranked_smallfish_barriers_small_barriers
          removedSmallBarriers: removed_small_barriers
          removedSmallBarriersGainMiles: removed_small_barriers_gain_miles
          removedSmallBarriersByYear: removed_small_barriers_by_year
          crossings
        }
        regions: region {
          id
          dams
          rankedDams: ranked_dams
          reconDams: recon_dams
          removedDams: removed_dams
          removedDamsGainMiles: removed_dams_gain_miles
          removedDamsByYear: removed_dams_by_year
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          rankedSmallBarriers: ranked_small_barriers
          removedSmallBarriers: removed_small_barriers
          removedSmallBarriersGainMiles: removed_small_barriers_gain_miles
          removedSmallBarriersByYear: removed_small_barriers_by_year
          crossings
        }
      }
    }
  `)

  return {
    total: {
      ...total,
      removedBarriersByYear: extractYearRemovedStats(
        total.removedDamsByYear || '',
        total.removedSmallBarriersByYear || ''
      ),
    },
    ...groupBy(
      regions.map(
        ({
          removedDamsByYear = '',
          removedSmallBarriersByYear = '',
          ...region
        }) => ({
          ...region,
          removedBarriersByYear: extractYearRemovedStats(
            removedDamsByYear,
            removedSmallBarriersByYear
          ),
        })
      ),
      'id'
    ),
  }
}
