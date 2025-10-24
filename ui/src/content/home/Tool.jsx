import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage as Image } from 'gatsby-plugin-image'
import { ChartBar, SearchLocation } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Heading, Grid, Paragraph } from 'theme-ui'

import { MAP_SERVICES } from 'config'
import { Link, OutboundLink } from 'components/Link'

const Tool = () => {
  const {
    prioritize: {
      childImageSharp: { gatsbyImageData: prioritizeImage },
    },
    summarize: {
      childImageSharp: { gatsbyImageData: summarizeImage },
    },
  } = useStaticQuery(graphql`
    query {
      prioritize: file(relativePath: { eq: "prioritize.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            width: 640
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      summarize: file(relativePath: { eq: "summarize.png" }) {
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
  `)

  return (
    <Box variant="boxes.section">
      <Heading as="h2" variant="heading.section">
        Get started using this tool
      </Heading>

      <Paragraph>
        This inventory and prioritization tool is designed to guide users in
        identifying high priority barrier removal projects. To access
        information about to funding sources for barrier removal, please visit
        the{' '}
        <OutboundLink to="https://interagency-bil-fish-passage-project-1-fws.hub.arcgis.com/">
          Fish Passage Portal
        </OutboundLink>
        . The portal is a &quot;one-stop shop&quot; for anyone who needs
        information, funding, or resources to improve fish passage and aquatic
        connectivity projects. It provides landowners and public lands managers
        the tools to find funding across the federal government, as well as
        access to data, planning, and geospatial information.
      </Paragraph>

      <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '3rem' }}>
        <Box>
          <Heading as="h3">Summarize the inventory</Heading>

          <Paragraph sx={{ mt: '1rem' }}>
            Explore summaries of the inventory by state, county, or different
            levels of watersheds.
            <br />
            <br />
            These summaries are a good way to become familiar with the level of
            aquatic fragmentation for many states across the U.S. Find out how
            many aquatic barriers have already been inventoried in your area!
            Just remember, the inventory is a living database, and is not yet
            comprehensive across these states.
          </Paragraph>
        </Box>
        <Box>
          <Flex sx={{ justifyContent: 'flex-end', mb: '1rem' }}>
            <Link to="/explore">
              <Button variant="primary">
                <ChartBar size="1em" />
                &nbsp; Start exploring
              </Button>
            </Link>
          </Flex>
          <Box
            sx={{
              img: {
                border: '1px solid',
                borderColor: 'grey.3',
                boxShadow: '1px 1px 3px #AAA',
              },
            }}
          >
            <Link to="/explore">
              <Image image={summarizeImage} alt="Summarize View" />
            </Link>
          </Box>
        </Box>
      </Grid>

      <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '6rem' }}>
        <Box>
          <Heading as="h3">Prioritize aquatic barriers for removal</Heading>
          <Paragraph sx={{ mt: '1rem' }}>
            Identify barriers for further investigation based on the criteria
            that matter to you.
            <br />
            <br />
            You can select specific geographic areas for prioritization,
            including counties, states, and watersheds. You can filter the
            available barriers based on criteria such as likely feasibility for
            removal, height, and more. Once you have prioritized aquatic
            barriers, you can download a CSV file for further analysis.
          </Paragraph>
        </Box>
        <Box>
          <Flex sx={{ justifyContent: 'flex-end', mb: '1rem' }}>
            <Link to="/priority">
              <Button>
                <SearchLocation size="1em" />
                &nbsp; Start prioritizing
              </Button>
            </Link>
          </Flex>
          <Box sx={{ img: { border: '1px solid', borderColor: 'grey.3' } }}>
            <Link to="/priority">
              <Image image={prioritizeImage} alt="Priority View" />
            </Link>
          </Box>
        </Box>
      </Grid>
      <Heading as="h4" sx={{ mt: '4rem' }}>
        Map services
      </Heading>
      <Paragraph sx={{ mt: '0.5rem' }}>
        If you would like to access map services of a recent version of the
        aquatic barriers and connectivity results (may not match the exact
        version here), you can import one of the following connectivity analysis
        map services into your GIS tool of choice:
      </Paragraph>
      <Box as="ul" sx={{ mt: '0.5rem' }}>
        <li>
          <OutboundLink to={MAP_SERVICES.dams}>Dams</OutboundLink> based on
          networks that are cut by dams and waterfalls.
        </li>
        <li>
          <OutboundLink to={MAP_SERVICES.small_barriers}>
            Assessed road crossings
          </OutboundLink>{' '}
          based on networks that are cut by dams, waterfalls, and assessed
          crossings.
        </li>
        <li>
          <OutboundLink to={MAP_SERVICES.combined_barriers}>
            Dams and assessed road crossings
          </OutboundLink>{' '}
          based on networks that are cut by dams, waterfalls, and assessed
          crossings.
        </li>
      </Box>
    </Box>
  )
}

export default Tool
