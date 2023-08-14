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
import { Tooltip } from 'components/Tooltip'
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
                  <Tooltip
                    content="Prioritize dams based on aquatic networks cut by dams and waterfalls."
                    direction="left"
                    maxWidth="360px"
                  >
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <SearchLocation
                        size="1em"
                        style={{ marginRight: '0.5rem' }}
                      />
                      Dams
                    </Button>
                  </Tooltip>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  {formatNumber(rankedDams)} available
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/small_barriers">
                  <Tooltip
                    content={
                      <>
                        <Text>
                          Prioritize road-related barriers based on aquatic
                          networks cut by dams, waterfalls, and road-related
                          barriers with at least moderate barrier severity.
                        </Text>
                        <Text sx={{ fontSize: 0, color: 'grey.8', mt: '1rem' }}>
                          Note: prioritization is limited to areas with assessed
                          road-related barriers.
                        </Text>
                      </>
                    }
                    direction="left"
                    maxWidth="360px"
                  >
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <SearchLocation
                        size="1em"
                        style={{ marginRight: '0.5rem' }}
                      />
                      Road-related barriers
                    </Button>
                  </Tooltip>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  {formatNumber(rankedSmallBarriers)} available
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/combined_barriers">
                  <Tooltip
                    content={
                      <>
                        <Text>
                          Prioritize dams and road-related barriers based on
                          aquatic networks cut by dams, waterfalls, and
                          road-related barriers with at least moderate barrier
                          severity.
                        </Text>
                        <Text sx={{ fontSize: 0, color: 'grey.8', mt: '1rem' }}>
                          Note: prioritization is limited to areas with assessed
                          road-related barriers.
                        </Text>
                      </>
                    }
                    direction="left"
                    maxWidth="360px"
                  >
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <SearchLocation
                        size="1em"
                        style={{ marginRight: '0.5rem' }}
                      />
                      Dams & road-related barriers
                    </Button>
                  </Tooltip>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  {formatNumber(rankedDams + rankedSmallBarriers)} available
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/largefish_barriers">
                  <Tooltip
                    content={
                      <>
                        <Text>
                          Prioritize dams and road-related barriers that are
                          likely to impact large-bodied fish species based on
                          aquatic networks cut by dams and waterfalls that do
                          not have partial or seasonal passability to salmonids
                          and non-salmonids, and road-related barriers with
                          severe or significant barrier severity.
                        </Text>
                        <Text sx={{ fontSize: 0, color: 'grey.8', mt: '1rem' }}>
                          Note: prioritization is limited to areas with assessed
                          road-related barriers.
                        </Text>
                      </>
                    }
                    direction="left"
                    maxWidth="360px"
                  >
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <SearchLocation
                        size="1em"
                        style={{ marginRight: '0.5rem' }}
                      />
                      Large-bodied fish barriers
                    </Button>
                  </Tooltip>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  {formatNumber(
                    rankedLargefishBarriersDams +
                      rankedLargefishBarriersSmallBarriers
                  )}{' '}
                  available
                </Text>
              </Box>
              <Box sx={{ mt: '2rem' }}>
                <Link to="/priority/smallfish_barriers">
                  <Tooltip
                    content={
                      <>
                        <Text>
                          Prioritize dams and road-related barriers based on
                          aquatic networks cut by dams, waterfalls, and
                          road-related barriers with at least minor barrier
                          severity.
                        </Text>
                        <Text sx={{ fontSize: 0, color: 'grey.8', mt: '1rem' }}>
                          Note: prioritization is limited to areas with assessed
                          road-related barriers.
                        </Text>
                      </>
                    }
                    direction="left"
                    maxWidth="360px"
                  >
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <SearchLocation
                        size="1em"
                        style={{ marginRight: '0.5rem' }}
                      />
                      Small-bodied fish barriers
                    </Button>
                  </Tooltip>
                </Link>
                <Text sx={{ fontSize: 1, color: 'grey.7' }}>
                  {formatNumber(
                    rankedSmallfishBarriersDams +
                      rankedSmallfishBarriersSmallBarriers
                  )}{' '}
                  available
                </Text>
              </Box>
            </Box>
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
