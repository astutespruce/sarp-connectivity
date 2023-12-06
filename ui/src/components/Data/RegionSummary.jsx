import { graphql, useStaticQuery } from 'gatsby'

import { extractYearRemovedStats } from 'components/Restoration/util'
import { groupBy } from 'util/data'

export const useRegionSummary = () => {
  const {
    allRegionStatsJson: { regions },
  } = useStaticQuery(graphql`
    query regionSummaryQuery {
      allRegionStatsJson {
        regions: edges {
          node {
            id: jsonId
            bounds
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
    }
  `)

  return groupBy(
    regions.map(
      ({
        node: {
          removedDamsByYear = '',
          removedSmallBarriersByYear = '',
          ...region
        },
      }) => ({
        ...region,
        removedBarriersByYear: extractYearRemovedStats(
          removedDamsByYear,
          removedSmallBarriersByYear
        ),
      })
    ),
    'id'
  )
}
