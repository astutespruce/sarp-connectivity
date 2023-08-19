import { graphql, useStaticQuery } from 'gatsby'
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
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          rankedSmallBarriers: ranked_small_barriers
          rankedLargefishBarriersSmallBarriers: ranked_largefish_barriers_small_barriers
          rankedSmallfishBarriersSmallBarriers: ranked_smallfish_barriers_small_barriers
          removedSmallBarriers: removed_small_barriers
          removedSmallBarriersGainMiles: removed_small_barriers_gain_miles
          crossings
        }
        regions: region {
          id
          dams
          rankedDams: ranked_dams
          reconDams: recon_dams
          removedDams: removed_dams
          removedDamsGainMiles: removed_dams_gain_miles
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          rankedSmallBarriers: ranked_small_barriers
          removedSmallBarriers: removed_small_barriers
          removedSmallBarriersGainMiles: removed_small_barriers_gain_miles
          crossings
        }
      }
    }
  `)

  return {
    total,
    ...groupBy(regions, 'id'),
  }
}
