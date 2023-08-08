import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { SearchLocation } from '@emotion-icons/fa-solid'
import {
  Box,
  Container,
  Grid,
  Heading,
  Flex,
  Button,
  Text,
  Paragraph,
} from 'theme-ui'

import { useSummaryData } from 'components/Data'
import { Link } from 'components/Link'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { formatNumber } from 'util/format'

const PrioritizePage = ({ data: { headerImage } }) => {
  const {
    total: {
      rankedDams,
      rankedSmallBarriers,
      rankedLargefishBarriersDams,
      rankedLargefishBarriersSmallBarriers,
      rankedSmallfishBarriersDams,
      rankedSmallfishBarriersSmallBarriers,
    },
  } = useSummaryData()

  return (
    <Layout>
      <HeaderImage
        image={headerImage.childImageSharp.gatsbyImageData}
        height="20vh"
        minHeight="12rem"
        credits={{
          author: 'Zach Dutra',
          url: 'https://unsplash.com/photos/2d7Y5Yi3aq8',
        }}
      />

      <Container>
        <Grid columns="1.75fr 1fr" gap={5}>
          <Box
            sx={{
              h4: {
                fontSize: '1.25rem',
              },
            }}
          >
            <Heading as="h3">To prioritize barriers:</Heading>

            <Box sx={{ mt: '1rem' }}>
              <Flex sx={{ alignItems: 'center' }}>
                <Box variant="boxes.step">1</Box>
                <Heading as="h4" sx={{ flex: '1 1 auto' }}>
                  Select area of interest.
                </Heading>
              </Flex>
              <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
                You can select areas using state, county, and watershed
                boundaries.
              </Paragraph>
            </Box>

            <Box sx={{ mt: '1rem' }}>
              <Flex sx={{ alignItems: 'center' }}>
                <Box variant="boxes.step">2</Box>
                <Heading as="h4" sx={{ flex: '1 1 auto' }}>
                  Filter barriers.
                </Heading>
              </Flex>
              <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
                You can filter barriers by feasibility, height, and other key
                characteristics to select those that best meet your needs.
              </Paragraph>
            </Box>

            <Box sx={{ mt: '1rem' }}>
              <Flex sx={{ alignItems: 'center' }}>
                <Box variant="boxes.step">3</Box>
                <Heading as="h4" sx={{ flex: '1 1 auto' }}>
                  Explore priorities on the map.
                </Heading>
              </Flex>
              <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
                Once you have defined your area of interest and selected the
                barriers you want, you can explore them on the map.
              </Paragraph>
            </Box>

            <Box sx={{ mt: '1rem' }}>
              <Flex sx={{ alignItems: 'center' }}>
                <Box variant="boxes.step">4</Box>
                <Heading as="h4" sx={{ flex: '1 1 auto' }}>
                  Download prioritized barriers.
                </Heading>
              </Flex>
              <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
                You can download the inventory for your area of interest and
                perform offline work.
              </Paragraph>
            </Box>
          </Box>

          <Box
            sx={{
              bg: 'grey.0',
              borderRadius: '0.5rem',
              p: '1rem',
            }}
          >
            <Heading as="h3">Prioritize:</Heading>
            <Box
              sx={{
                mt: '1rem',
                fontSize: '1.1rem',
              }}
            >
              <Box>
                <Link to="/priority/dams">
                  <Button sx={{ width: '100%', textAlign: 'left' }}>
                    <SearchLocation
                      size="1em"
                      style={{ marginRight: '0.5rem' }}
                    />
                    Dams
                  </Button>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  ({formatNumber(rankedDams)} available)
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/small_barriers">
                  <Button sx={{ width: '100%', textAlign: 'left' }}>
                    <SearchLocation
                      size="1em"
                      style={{ marginRight: '0.5rem' }}
                    />
                    Road-related barriers*
                  </Button>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  ({formatNumber(rankedSmallBarriers)} available)
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/combined_barriers">
                  <Button sx={{ width: '100%', textAlign: 'left' }}>
                    <SearchLocation
                      size="1em"
                      style={{ marginRight: '0.5rem' }}
                    />
                    Dams & road-related barriers*
                  </Button>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  ({formatNumber(rankedDams + rankedSmallBarriers)} available)
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/largefish_barriers">
                  <Button sx={{ width: '100%', textAlign: 'left' }}>
                    <SearchLocation
                      size="1em"
                      style={{ marginRight: '0.5rem' }}
                    />
                    Dams & road-related barriers (for large-bodied fish)*
                  </Button>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  (
                  {formatNumber(
                    rankedLargefishBarriersDams +
                      rankedLargefishBarriersSmallBarriers
                  )}{' '}
                  available)
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/smallfish_barriers">
                  <Button sx={{ width: '100%', textAlign: 'left' }}>
                    <SearchLocation
                      size="1em"
                      style={{ marginRight: '0.5rem' }}
                    />
                    Dams & road-related barriers (for small-bodied fish)*
                  </Button>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  (
                  {formatNumber(
                    rankedSmallfishBarriersDams +
                      rankedSmallfishBarriersSmallBarriers
                  )}{' '}
                  available)
                </Text>
              </Box>
            </Box>
            <Paragraph variant="help" sx={{ mt: '2rem' }}>
              *limited to areas with assessed road-related barriers
            </Paragraph>
          </Box>
        </Grid>
      </Container>
    </Layout>
  )
}
PrioritizePage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query PrioritizeStartPageQuery {
    headerImage: file(
      relativePath: { eq: "zack-dutra-2d7Y5Yi3aq8-unsplash.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
  }
`

export default PrioritizePage

export const Head = () => (
  <SEO title="Prioritize dams and road-related barriers" />
)
