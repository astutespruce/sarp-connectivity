import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage as Image } from 'gatsby-plugin-image'
import { ChartBar, SearchLocation } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Divider, Heading, Grid, Paragraph } from 'theme-ui'

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
      <Divider sx={{ mb: '4rem' }} />

      <Heading as="h2" variant="heading.section">
        Get started using this tool:
      </Heading>

      <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '3rem' }}>
        <Box>
          <Heading as="h3">Summarize the inventory</Heading>

          <Paragraph sx={{ mt: '1rem' }}>
            Explore summaries of the inventory by state, county, or different
            levels of watersheds and ecoregions.
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
            <Link to="/summary">
              <Button variant="primary">
                <ChartBar size="1em" />
                &nbsp; Start summarizing
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
            <Link to="/summary">
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
            including counties, states, watersheds, and ecoregions. You can
            filter the available barriers based on criteria such as likely
            feasibility for removal, height, and more. Once you have prioritized
            aquatic barriers, you can download a CSV file for further analysis.
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
    </Box>
  )
}

export default Tool
