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
          total_small_barriers
          small_barriers
          crossings
          miles
          perennial_miles
          on_network_small_barriers
          on_network_dams
        }
        regions: region {
          id
          dams
          total_small_barriers
          small_barriers
          crossings
          miles
          perennial_miles
          on_network_small_barriers
          on_network_dams
        }
      }
    }
  `)

  return {
    total,
    ...groupBy(regions, 'id'),
  }
}
