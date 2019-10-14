import { graphql, useStaticQuery } from 'gatsby'

export const useSummaryData = () => {
  return useStaticQuery(graphql`
    query summaryQuery {
      summaryStatsJson {
        southeast {
          dams
          total_barriers
          barriers
          crossings
          miles
          on_network_barriers
          on_network_dams
        }
      }
    }
  `).summaryStatsJson.southeast
}
