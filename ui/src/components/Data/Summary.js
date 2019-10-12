import { graphql, useStaticQuery } from 'gatsby'

export const useSummaryData = () => {
  return useStaticQuery(graphql`
    query summaryQuery {
      summaryStatsJson {
        southeast {
          dams
          barriers
          crossings
          miles
          off_network_barriers
          off_network_dams
        }
      }
    }
  `).summaryStatsJson.southeast
}
