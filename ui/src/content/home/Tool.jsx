import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage as Image } from 'gatsby-plugin-image'
import { ChartBar, SearchLocation } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Heading, Grid, Paragraph } from 'theme-ui'

import { Link } from 'components/Link'

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
      prioritize: file(relativePath: { eq: "prioritize.jpg" }) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            width: 640
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      summarize: file(relativePath: { eq: "summarize.jpg" }) {
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
        The Southeast Aquatic Barrier Prioritization Tool empowers you with the
        latest inventory data:
      </Heading>

      <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '3rem' }}>
        <Box>
          <Heading as="h3">Summarize the inventory across the region</Heading>

          <Paragraph sx={{ mt: '1rem' }}>
            Explore summaries of the inventory across the region by state,
            county, or different levels of watersheds and ecoregions.
            <br />
            <br />
            These summaries are a good way to become familiar with the level of
            aquatic fragmentation across the Southeast. Find out how many
            aquatic barriers have already been inventoried in your area! Just
            remember, the inventory is a living database, and is not yet
            comprehensive across the region.
          </Paragraph>
        </Box>
        <Box>
          <Flex sx={{ justifyContent: 'center', mb: '2rem' }}>
            <Link to="/summary">
              <Button variant="primary">
                <ChartBar size="1em" />
                &nbsp; Start summarizing
              </Button>
            </Link>
          </Flex>
          <Link to="/summary">
            <Image image={summarizeImage} alt="Summarize View" />
          </Link>
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
            including counties, states, watersheds, and ecoregions. You can
            filter the available barriers based on criteria such as likely
            feasibility for removal, height, and more. Once you have prioritized
            aquatic barriers, you can download a CSV file for further analysis.
          </Paragraph>
        </Box>
        <Box>
          <Flex sx={{ justifyContent: 'center', mb: '2rem' }}>
            <Link to="/priority">
              <Button>
                <SearchLocation size="1em" />
                &nbsp; Start prioritizing
              </Button>
            </Link>
          </Flex>
          <Link to="/priority">
            <Image image={prioritizeImage} alt="Priority View" />
          </Link>
        </Box>
      </Grid>
    </Box>
  )
}

export default Tool
