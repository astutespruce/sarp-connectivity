import { graphql, useStaticQuery } from 'gatsby'

export const useStateSummary = () =>
  useStaticQuery(graphql`
    query stateSummaryQuery {
      allSummaryStatsJson {
        edges {
          node {
            State {
              id
              dams
              reconDams: recon_dams
              totalSmallBarriers: total_small_barriers
            }
          }
        }
      }
    }
  `).allSummaryStatsJson.edges[0].node.State.sort((a, b) => {
    if (a < b) return -1
    if (a > b) return 1
    return 0
  })
