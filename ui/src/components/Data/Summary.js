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
          reconDams: recon_dams
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          rankedSmallBarriers: ranked_small_barriers
          crossings
        }
        regions: region {
          id
          dams
          rankedDams: ranked_dams
          reconDams: recon_dams
          totalSmallBarriers: total_small_barriers
          smallBarriers: small_barriers
          rankedSmallBarriers: ranked_small_barriers
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
