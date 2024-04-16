import { graphql, useStaticQuery } from 'gatsby'

// this is only used for state download tables
export const useStateSummary = () => {
  const {
    allStateStatsJson: { states },
  } = useStaticQuery(graphql`
    query stateSummaryQuery {
      allStateStatsJson {
        states: edges {
          node {
            id: jsonId
            dams
            rankedDams: ranked_dams
            reconDams: recon_dams
            smallBarriers: small_barriers
            rankedSmallBarriers: ranked_small_barriers
            totalSmallBarriers: total_small_barriers
          }
        }
      }
    }
  `)

  return states.map(({ node }) => node)
}
