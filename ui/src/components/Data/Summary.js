import { graphql, useStaticQuery } from 'gatsby'
import { groupBy } from 'util/data'

export const useSummaryData = () => {
  const {
    summaryStatsJson: { total, regions },
  } = useStaticQuery(graphql`
    query summaryQuery {
      summaryStatsJson {
        total {
          dams
          onNetworkDams: on_network_dams
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          onNetworkSmallBarriers: on_network_small_barriers
          crossings
          miles
          perennialMiles: perennial_miles
        }
        regions: region {
          id
          dams
          onNetworkDams: on_network_dams
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          onNetworkSmallBarriers: on_network_small_barriers
          crossings
          miles
          perennialMiles: perennial_miles
        }
      }
    }
  `)

  return {
    total,
    ...groupBy(regions, 'id'),
  }
}
