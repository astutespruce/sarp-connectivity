import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Grid, Heading, Flex, Button, Text, Paragraph } from 'theme-ui'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'

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

      <Box sx={{ p: '2rem' }}>
        <Grid columns="1fr 2fr" gap={5}>
          <Box
            sx={{
              h4: {
                fontSize: '1.25rem',
              },
            }}
          >
            <Heading as="h3">How to prioritize barriers:</Heading>

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
                <br />
                <br />
                Prioritization is limited to areas with dams or assessed
                barriers depending on the scenario.
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

          <Box>
            <Heading as="h3" sx={{ mb: '1rem' }}>
              Prioritization scenarios available:
            </Heading>

            <Grid
              columns={[1, 2, 3]}
              gap={3}
              sx={{
                '&>div': {
                  border: '1px solid',
                  borderColor: 'grey.2',
                  borderRadius: '0.5rem',
                  boxShadow: '2px 2px 4px #EEE',
                  p: '1rem',
                },
                '& h4': {
                  borderBottom: '1px solid',
                  borderBottomColor: 'grey.9',
                  pb: '0.25rem',
                  mb: '0.5rem',
                },
              }}
            >
              <Flex sx={{ flexDirection: 'column' }}>
                <Box sx={{ flex: '1 1 auto', mb: '1rem' }}>
                  <Heading as="h4">Dams</Heading>
                  <Text sx={{ lineHeight: 1.2 }}>
                    Prioritize dams based on aquatic networks cut by dams and
                    waterfalls.
                  </Text>
                </Box>

                <Box sx={{ flex: '0 0 auto' }}>
                  <Link to="/priority/dams">
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <AngleDoubleRight
                        size="1.25rem"
                        style={{ marginRight: '0.5rem', marginTop: '-0.25rem' }}
                      />
                      Start prioritizing
                    </Button>
                  </Link>
                  <Text
                    sx={{
                      textAlign: 'center',
                      fontSize: 1,
                      color: 'grey.7',
                      mt: '0.5rem',
                    }}
                  >
                    {formatNumber(rankedDams)} available
                  </Text>
                </Box>
              </Flex>
              <Flex sx={{ flexDirection: 'column' }}>
                <Box sx={{ flex: '1 1 auto', mb: '1rem' }}>
                  <Heading as="h4">Road-related barriers</Heading>
                  <Text sx={{ lineHeight: 1.2 }}>
                    Prioritize road-related barriers based on aquatic networks
                    cut by dams, waterfalls, and road-related barriers with at
                    least moderate barrier severity.
                  </Text>
                </Box>
                <Box sx={{ flex: '0 0 auto' }}>
                  <Link to="/priority/small_barriers">
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <AngleDoubleRight
                        size="1.25rem"
                        style={{ marginRight: '0.5rem', marginTop: '-0.25rem' }}
                      />
                      Start prioritizing
                    </Button>
                  </Link>
                  <Text
                    sx={{
                      textAlign: 'center',
                      fontSize: 1,
                      color: 'grey.7',
                      mt: '0.5rem',
                    }}
                  >
                    {formatNumber(rankedSmallBarriers)} available
                  </Text>
                </Box>
              </Flex>
              <Flex sx={{ flexDirection: 'column' }}>
                <Box sx={{ flex: '1 1 auto', mb: '1rem' }}>
                  <Heading as="h4">Dams & road-related barriers</Heading>
                  <Text sx={{ lineHeight: 1.2 }}>
                    Prioritize dams and road-related barriers based on aquatic
                    networks cut by dams, waterfalls, and road-related barriers
                    with at least moderate barrier severity.
                  </Text>
                </Box>
                <Box sx={{ flex: '0 0 auto' }}>
                  <Link to="/priority/combined_barriers">
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <AngleDoubleRight
                        size="1.25rem"
                        style={{ marginRight: '0.5rem', marginTop: '-0.25rem' }}
                      />{' '}
                      Start prioritizing
                    </Button>
                  </Link>
                  <Text
                    sx={{
                      textAlign: 'center',
                      fontSize: 1,
                      color: 'grey.7',
                      mt: '0.5rem',
                    }}
                  >
                    {formatNumber(rankedDams + rankedSmallBarriers)} available
                  </Text>
                </Box>
              </Flex>

              <Flex sx={{ flexDirection: 'column' }}>
                <Box sx={{ flex: '1 1 auto', mb: '1rem' }}>
                  <Heading as="h4">Large-bodied fish barriers</Heading>
                  <Text sx={{ lineHeight: 1.2 }}>
                    Prioritize dams and road-related barriers that are likely to
                    impact large-bodied fish species based on aquatic networks
                    cut by dams and waterfalls that do not have partial or
                    seasonal passability to salmonids and non-salmonids, and
                    road-related barriers with severe or significant barrier
                    severity.
                  </Text>
                </Box>
                <Box sx={{ flex: '0 0 auto' }}>
                  <Link to="/priority/largefish_barriers">
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <AngleDoubleRight
                        size="1.25rem"
                        style={{ marginRight: '0.5rem', marginTop: '-0.25rem' }}
                      />
                      Start prioritizing
                    </Button>
                  </Link>
                  <Text
                    sx={{
                      textAlign: 'center',
                      fontSize: 1,
                      color: 'grey.7',
                      mt: '0.5rem',
                    }}
                  >
                    {formatNumber(
                      rankedLargefishBarriersDams +
                        rankedLargefishBarriersSmallBarriers
                    )}{' '}
                    available
                  </Text>
                </Box>
              </Flex>

              <Flex sx={{ flexDirection: 'column' }}>
                <Box sx={{ flex: '1 1 auto', mb: '1rem' }}>
                  <Heading as="h4">Small-bodied fish barriers</Heading>
                  <Text sx={{ lineHeight: 1.2 }}>
                    Prioritize dams and road-related barriers based on aquatic
                    networks cut by dams, waterfalls, and road-related barriers
                    with at least minor barrier severity.
                  </Text>
                </Box>
                <Box sx={{ flex: '0 0 auto' }}>
                  <Link to="/priority/smallfish_barriers">
                    <Button sx={{ width: '100%', textAlign: 'left' }}>
                      <AngleDoubleRight
                        size="1.25rem"
                        style={{ marginRight: '0.5rem', marginTop: '-0.25rem' }}
                      />
                      Start prioritizing
                    </Button>
                  </Link>
                  <Text
                    sx={{
                      textAlign: 'center',
                      fontSize: 1,
                      color: 'grey.7',
                      mt: '0.5rem',
                    }}
                  >
                    {formatNumber(
                      rankedSmallfishBarriersDams +
                        rankedSmallfishBarriersSmallBarriers
                    )}{' '}
                    available
                  </Text>
                </Box>
              </Flex>
            </Grid>
          </Box>
        </Grid>
      </Box>
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
