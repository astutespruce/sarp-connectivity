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
          onNetworkDams: on_network_dams
          reconDams: recon_dams
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          onNetworkSmallBarriers: on_network_small_barriers
          crossings
        }
        regions: region {
          id
          dams
          onNetworkDams: on_network_dams
          reconDams: recon_dams
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          onNetworkSmallBarriers: on_network_small_barriers
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
