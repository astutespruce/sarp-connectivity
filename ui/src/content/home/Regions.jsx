import React from 'react'
import { Box, Button, Divider, Flex, Grid, Heading, Text } from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'
import { useStaticQuery, graphql } from 'gatsby'

import { Link } from 'components/Link'
import { useSummaryData } from 'components/Data'
import { RegionStats } from 'components/Regions'

import { REGION_STATES } from '../../../config/constants'

const Regions = () => {
  const { gpiw, se, sw } = useSummaryData()
  const {
    gpiwMap: {
      childImageSharp: { gatsbyImageData: gpiwMap },
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
          <Box>
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
            <Box sx={{ textAlign: 'center', flex: '0 0 auto' }}>
              <Link to="/regions/southeast">
                <Button>Explore Southeast</Button>
              </Link>
            </Box>
          </Flex>
        </Grid>
      </Box>

      <Box sx={{ mt: '5rem' }}>
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Box>
            <Link to="/regions/great_plains_intermountain_west">
              <Heading as="h3" sx={{ fontWeight: 'normal' }}>
                Great Plains &amp; Intermountain West
              </Heading>
            </Link>
          </Box>
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
            <Box sx={{ textAlign: 'center', flex: '0 0 auto' }}>
              <Link to="/regions/great_plains_intermountain_west">
                <Button>Explore Great Plains &amp; Intermountain West</Button>
              </Link>
            </Box>
          </Flex>
        </Grid>
      </Box>

      <Box sx={{ mt: '5rem' }}>
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Box>
            <Link to="/regions/southwest">
              <Heading as="h3" sx={{ fontWeight: 'normal' }}>
                Southwest
              </Heading>
            </Link>
          </Box>
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
            <Box sx={{ textAlign: 'center', flex: '0 0 auto' }}>
              <Link to="/regions/southwest">
                <Button>Explore Southwest</Button>
              </Link>
            </Box>
          </Flex>
        </Grid>
      </Box>
    </Box>
  )
}

export default Regions
