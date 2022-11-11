import React from 'react'
import { Box, Button, Divider, Flex, Grid, Heading, Text } from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'
import { ChartBar, SearchLocation } from '@emotion-icons/fa-solid'
import { useStaticQuery, graphql } from 'gatsby'

import { Link } from 'components/Link'
import { useSummaryData } from 'components/Data'
import { RegionStats } from 'components/Regions'
import { REGION_STATES } from 'config'

const Regions = () => {
  const { gpiw, pnw, se, sw } = useSummaryData()
  const {
    gpiwMap: {
      childImageSharp: { gatsbyImageData: gpiwMap },
    },
    pnwMap: {
      childImageSharp: { gatsbyImageData: pnwMap },
    },
    seMap: {
      childImageSharp: { gatsbyImageData: seMap },
    },
    swMap: {
      childImageSharp: { gatsbyImageData: swMap },
    },
  } = useStaticQuery(graphql`
    query {
      gpiwMap: file(relativePath: { eq: "maps/gpiw.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      pnwMap: file(relativePath: { eq: "maps/pnw.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      seMap: file(relativePath: { eq: "maps/se.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      swMap: file(relativePath: { eq: "maps/sw.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
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
        Explore the inventory by region:
      </Heading>

      <Box sx={{ mt: '2rem' }}>
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ flex: '1 1 auto' }}>
            <Link to="/regions/southeast">
              <Heading
                as="h3"
                sx={{
                  fontWeight: 'normal',
                }}
              >
                Southeast
              </Heading>
            </Link>
          </Box>
          <Flex sx={{ flex: '0 0 auto' }}>
            <Box sx={{ flex: '1 1 auto', mr: '2rem' }}>
              <Link to="summary/?region=se">
                <Button variant="primary">
                  <ChartBar size="1em" />
                  &nbsp; Start summarizing
                </Button>
              </Link>
            </Box>
            <Box sx={{ flex: '0 0 auto' }}>
              <Link to="/priority">
                <Button>
                  <SearchLocation size="1em" />
                  &nbsp; Start prioritizing
                </Button>
              </Link>
            </Box>
          </Flex>
        </Flex>
        <Text>
          Includes <b>{REGION_STATES.se.length - 1}</b> states and Puerto Rico
        </Text>

        <Grid columns={[0, '1fr 2fr']} gap={4}>
          <Box>
            <Link to="/regions/southeast">
              <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
                <GatsbyImage image={seMap} alt="Southeast region map" />
              </Box>
            </Link>
          </Box>

          <Flex sx={{ flexDirection: 'column' }}>
            <Box sx={{ flex: '0 0 auto' }}>
              <RegionStats {...se} />
            </Box>
            <Box sx={{ height: '100%', flex: '1 1 auto' }} />

            <Flex sx={{ justifyContent: 'flex-end' }}>
              <Link to="/regions/southeast">
                Learn more about the Southeast region
              </Link>
            </Flex>
          </Flex>
        </Grid>
      </Box>

      <Box
        sx={{
          mt: '5rem',
          pt: '2rem',
          borderTop: '1px solid',
          borderTopColor: 'grey.3',
        }}
      >
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ flex: '1 1 auto' }}>
            <Link to="/regions/great_plains_intermountain_west">
              <Heading as="h3" sx={{ fontWeight: 'normal' }}>
                Great Plains &amp; Intermountain West
              </Heading>
            </Link>
          </Box>
          <Flex sx={{ flex: '0 0 auto' }}>
            <Box sx={{ flex: '1 1 auto', mr: '2rem' }}>
              <Link to="summary/?region=gpiw">
                <Button variant="primary">
                  <ChartBar size="1em" />
                  &nbsp; Start summarizing
                </Button>
              </Link>
            </Box>
            <Box sx={{ flex: '0 0 auto' }}>
              <Link to="/priority">
                <Button>
                  <SearchLocation size="1em" />
                  &nbsp; Start prioritizing
                </Button>
              </Link>
            </Box>
          </Flex>
        </Flex>

        <Text>
          Includes <b>{REGION_STATES.gpiw.length}</b> states
        </Text>

        <Grid columns={[0, '1fr 2fr']} gap={4}>
          <Box>
            <Link to="/regions/great_plains_intermountain_west">
              <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
                <GatsbyImage
                  image={gpiwMap}
                  alt="Mountain / Prairie region map"
                />
              </Box>
            </Link>
          </Box>
          <Flex sx={{ flexDirection: 'column' }}>
            <Box sx={{ flex: '0 0 auto' }}>
              <RegionStats {...gpiw} />
            </Box>
            <Box sx={{ height: '100%', flex: '1 1 auto' }} />

            <Flex sx={{ justifyContent: 'flex-end' }}>
              <Link to="/regions/great_plains_intermountain_west">
                Learn more about the Great Plains &amp; Intermountain West
                region
              </Link>
            </Flex>
          </Flex>
        </Grid>
      </Box>

      <Box
        sx={{
          mt: '5rem',
          pt: '2rem',
          borderTop: '1px solid',
          borderTopColor: 'grey.3',
        }}
      >
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ flex: '1 1 auto' }}>
            <Link to="/regions/southwest">
              <Heading as="h3" sx={{ fontWeight: 'normal' }}>
                Southwest
              </Heading>
            </Link>
          </Box>
          <Flex sx={{ flex: '0 0 auto' }}>
            <Box sx={{ flex: '1 1 auto', mr: '2rem' }}>
              <Link to="summary/?region=sw">
                <Button variant="primary">
                  <ChartBar size="1em" />
                  &nbsp; Start summarizing
                </Button>
              </Link>
            </Box>
            <Box sx={{ flex: '0 0 auto' }}>
              <Link to="/priority">
                <Button>
                  <SearchLocation size="1em" />
                  &nbsp; Start prioritizing
                </Button>
              </Link>
            </Box>
          </Flex>
        </Flex>

        <Text>
          Includes <b>{REGION_STATES.sw.length}</b> states
        </Text>

        <Grid columns={[0, '1fr 2fr']} gap={4}>
          <Box>
            <Link to="/regions/southwest">
              <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
                <GatsbyImage image={swMap} alt="Southwest region map" />
              </Box>
            </Link>
          </Box>

          <Flex sx={{ flexDirection: 'column' }}>
            <Box sx={{ flex: '0 0 auto' }}>
              <RegionStats {...sw} />
            </Box>
            <Box sx={{ height: '100%', flex: '1 1 auto' }} />

            <Flex sx={{ justifyContent: 'flex-end' }}>
              <Link to="/regions/southwest">
                Learn more about the Southwest region
              </Link>
            </Flex>
          </Flex>
        </Grid>
      </Box>

      <Box
        sx={{
          mt: '5rem',
          pt: '2rem',
          borderTop: '1px solid',
          borderTopColor: 'grey.3',
        }}
      >
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ flex: '1 1 auto' }}>
            <Link to="/regions/northwest">
              <Heading as="h3" sx={{ fontWeight: 'normal' }}>
                Pacific Northwest
              </Heading>
            </Link>
          </Box>
          <Flex sx={{ flex: '0 0 auto' }}>
            <Box sx={{ flex: '1 1 auto', mr: '2rem' }}>
              <Link to="summary/?region=pnw">
                <Button variant="primary">
                  <ChartBar size="1em" />
                  &nbsp; Start summarizing
                </Button>
              </Link>
            </Box>
            <Box sx={{ flex: '0 0 auto' }}>
              <Link to="/priority">
                <Button>
                  <SearchLocation size="1em" />
                  &nbsp; Start prioritizing
                </Button>
              </Link>
            </Box>
          </Flex>
        </Flex>

        <Text>
          Includes <b>{REGION_STATES.pnw.length}</b> states
        </Text>

        <Grid columns={[0, '1fr 2fr']} gap={4}>
          <Box>
            <Link to="/regions/northwest">
              <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
                <GatsbyImage
                  image={pnwMap}
                  alt="Pacific Northwest region map"
                />
              </Box>
            </Link>
          </Box>

          <Flex sx={{ flexDirection: 'column' }}>
            <Box sx={{ flex: '0 0 auto' }}>
              <RegionStats {...pnw} />
            </Box>
            <Box sx={{ height: '100%', flex: '1 1 auto' }} />

            <Flex sx={{ justifyContent: 'flex-end' }}>
              <Link to="/regions/northwest">
                Learn more about the Pacific Northwest region
              </Link>
            </Flex>
          </Flex>
        </Grid>
      </Box>
    </Box>
  )
}

export default Regions
