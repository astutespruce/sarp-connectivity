import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'

import { Box, Grid, Heading, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { CONNECTIVITY_TEAMS, STATES, REGIONS } from 'config'
import { groupBy } from 'util/data'
import { extractNodes } from 'util/graphql'

const SARPGetInvolvedSection = () => {
  const { imagesSharp } = useStaticQuery(graphql`
    query SARPGetInvolvedSection {
      imagesSharp: allFile(filter: { relativeDirectory: { eq: "teams" } }) {
        edges {
          node {
            state: name
            childImageSharp {
              gatsbyImageData(
                layout: CONSTRAINED
                width: 640
                formats: [AUTO, WEBP]
                placeholder: BLURRED
              )
            }
          }
        }
      }
    }
  `)
  const images = groupBy(extractNodes(imagesSharp), 'state')

  return (
    <Box variant="boxes.section">
      <Heading as="h2" variant="heading.section">
        How to get involved?
      </Heading>

      <Grid columns={[0, 2]} gap={5}>
        <Box>
          <Paragraph>
            SARP and partners have been working to build a community of practice
            surrounding barrier removal through the development of state-based
            Aquatic Connectivity Teams (ACTs). These teams create a forum that
            allows resource managers from all sectors to work together and share
            resources, disseminate information, and examine regulatory
            streamlining processes as well as project management tips and
            techniques.
            <br />
            <br />
            To join a team click{' '}
            <OutboundLink to="https://www.americanrivers.org/aquatic-connectivity-groups/">
              here
            </OutboundLink>
            .
          </Paragraph>
        </Box>
        <Box>
          <Heading as="h4">Aquatic connectivity teams:</Heading>
          <Box as="ul" sx={{ mt: '0.5rem' }}>
            {REGIONS.southeast.states
              .filter((state) => CONNECTIVITY_TEAMS[state])
              .map((state) => (
                <li key={state}>
                  {STATES[state]}:{' '}
                  {CONNECTIVITY_TEAMS[state].url ? (
                    <OutboundLink to={CONNECTIVITY_TEAMS[state].url}>
                      {CONNECTIVITY_TEAMS[state].name}
                    </OutboundLink>
                  ) : (
                    CONNECTIVITY_TEAMS[state].name
                  )}
                </li>
              ))}
          </Box>
        </Box>
      </Grid>

      <Grid columns={Object.keys(images).length} gap={2} sx={{ mt: '2rem' }}>
        {Object.entries(images)
          .slice(0, 4)
          .map(
            ([
              state,
              {
                childImageSharp: { gatsbyImageData },
              },
            ]) => (
              <Box key={state} sx={{ maxHeight: '8rem', overflow: 'hidden' }}>
                <GatsbyImage
                  image={gatsbyImageData}
                  alt={`${state} aquatic connectivity team photo`}
                />
              </Box>
            )
          )}
      </Grid>
    </Box>
  )
}

export default SARPGetInvolvedSection
