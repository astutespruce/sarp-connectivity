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
          total_barriers
          barriers
          crossings
          miles
          perennial_miles
          on_network_barriers
          on_network_dams
        }
        regions: region {
          id
          dams
          total_barriers
          barriers
          crossings
          miles
          perennial_miles
          on_network_barriers
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
