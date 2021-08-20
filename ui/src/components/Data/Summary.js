import { graphql, useStaticQuery } from 'gatsby'

// FIXME: temporary shim to support Southeast data in new data structure
export const useSummaryData = () =>
  useStaticQuery(graphql`
    query summaryQuery {
      summaryStatsJson {
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
  `).summaryStatsJson.regions.filter(({ id }) => id === 'se')[0]
