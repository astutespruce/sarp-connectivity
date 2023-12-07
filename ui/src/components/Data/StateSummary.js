import { graphql, useStaticQuery } from 'gatsby'

import { extractYearRemovedStats } from 'components/Restoration/util'

export const useStateSummary = () => {
  const {
    allStateStatsJson: { states },
  } = useStaticQuery(graphql`
    query stateSummaryQuery {
      allStateStatsJson {
        states: edges {
          node {
            id: jsonId
            dams
            reconDams: recon_dams
            removedDams: removed_dams
            removedDamsGainMiles: removed_dams_gain_miles
            removedDamsByYear: removed_dams_by_year
            totalSmallBarriers: total_small_barriers
            smallBarriers: small_barriers
            removedSmallBarriers: removed_small_barriers
            removedSmallBarriersGainMiles: removed_small_barriers_gain_miles
            removedSmallBarriersByYear: removed_small_barriers_by_year
            crossings
          }
        }
      }
    }
  `)

  return states.map(
    ({
      node: {
        removedDamsByYear = '',
        removedSmallBarriersByYear = '',
        ...state
      },
    }) => ({
      ...state,
      removedBarriersByYear: extractYearRemovedStats(
        removedDamsByYear,
        removedSmallBarriersByYear
      ),
    })
  )
}
