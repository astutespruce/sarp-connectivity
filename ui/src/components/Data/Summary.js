import { graphql, useStaticQuery } from 'gatsby'

export const useSummaryData = () =>
  useStaticQuery(graphql`
    query summaryQuery {
      summaryStatsJson {
        # FIXME:
        total: southeast {
          dams
          total_barriers
          barriers
          crossings
          miles
          on_network_barriers
          on_network_dams
        }
        se: southeast {
          dams
          total_barriers
          barriers
          crossings
          miles
          on_network_barriers
          on_network_dams
        }
        # FIXME:
        sw: southeast {
          dams
          total_barriers
          barriers
          crossings
          miles
          on_network_barriers
          on_network_dams
        }
        # FIXME:
        gpiw: southeast {
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
  `).summaryStatsJson
