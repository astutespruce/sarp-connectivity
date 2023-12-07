import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import {
  Box,
  Flex,
  Container,
  Divider,
  Grid,
  Heading,
  Image,
  Paragraph,
  Text,
} from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { useRegionSummary } from 'components/Data'
import { StateDownloadTable } from 'components/Download'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { RegionActionLinks, RegionStats } from 'components/Regions'
import { Chart } from 'components/Restoration'
import { REGIONS, STATE_DATA_PROVIDERS } from 'config'
import { formatNumber } from 'util/format'
import { dynamicallyLoadImage } from 'util/dom'

const regionID = 'pnw'
const {
  [regionID]: { name, states },
} = REGIONS

const dataProviders = []
states.forEach((state) => {
  dataProviders.push(...(STATE_DATA_PROVIDERS[state] || []))
})

const PNWRegionPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    salmonPhoto: {
      childImageSharp: { gatsbyImageData: salmonPhoto },
    },
    map: {
      childImageSharp: { gatsbyImageData: map },
    },
  },
}) => {
  const [metric, setMetric] = useState('gainmiles')
  const { [regionID]: summary } = useRegionSummary()
  const { removedBarriersByYear } = summary

  return (
    <Layout>
      <HeaderImage
        image={headerImage}
        height="20vh"
        minHeight="18rem"
        credits={{
          author: 'Bureau of Land Management',
          url: 'https://www.flickr.com/photos/blmoregon/47700011012/',
        }}
      />

      <Container>
        <Flex
          sx={{
            alignItems: 'baseline',
            justifyContent: 'space-between',
            borderBottom: '1px solid',
            borderBottomColor: 'grey.2',
            pb: '0.25rem',
          }}
        >
          <Heading as="h1" sx={{ flex: '1 1 auto' }}>
            {name} Region
          </Heading>
        </Flex>

        <Grid columns={2} gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
              <GatsbyImage
                image={map}
                alt={`${name} region map`}
                sx={{ border: '1px solid', borderColor: 'grey.3' }}
              />
            </Box>
            <Text sx={{ fontSize: 1, color: 'grey.7' }}>
              Map of {formatNumber(summary.dams)} inventoried dams and{' '}
              {formatNumber(summary.smallBarriers)} road-related barriers likely
              to impact aquatic organisms in the {name} region.
            </Text>
          </Box>
          <Box>
            <Heading as="h4" sx={{ mb: '1rem' }}>
              Includes {states.length} states with:
            </Heading>

            <RegionStats {...summary} />
          </Box>
        </Grid>

        <Box sx={{ mt: '3rem' }}>
          <Heading as="h3">
            Progress toward restoring aquatic connectivity:
          </Heading>
          <Box sx={{ mt: '1rem' }}>
            <Chart
              barrierType="combined_barriers"
              removedBarriersByYear={removedBarriersByYear}
              metric={metric}
              onChangeMetric={setMetric}
            />
          </Box>
        </Box>

        <RegionActionLinks region={regionID} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Statistics by state:
          </Heading>
          <Box sx={{ mt: '0.5rem' }}>
            <StateDownloadTable region={regionID} {...summary} />
          </Box>
        </Box>

        {dataProviders.length > 0 ? (
          <Box variant="boxes.section">
            <Heading as="h2" variant="heading.section">
              Data Sources
            </Heading>

            {dataProviders.map(({ key, description, logo, logoWidth }) => (
              <Grid
                key={key}
                columns="2fr 1fr"
                gap={5}
                sx={{
                  '&:not(:first-of-type)': {
                    mt: '2rem',
                  },
                }}
              >
                <Box sx={{ fontSize: [2, 3] }}>
                  <div dangerouslySetInnerHTML={{ __html: description }} />
                </Box>
                {logo ? (
                  <Box sx={{ maxWidth: logoWidth }}>
                    <Image src={dynamicallyLoadImage(logo)} />
                  </Box>
                ) : null}
              </Grid>
            ))}
          </Box>
        ) : null}

        <Divider sx={{ my: '4rem' }} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            You can help!
          </Heading>
          <Grid columns="3fr 1fr" gap={4} sx={{ mt: '1rem' }}>
            <Box>
              <Paragraph>
                You can help improve the inventory You can help improve the
                inventory by sharing data, assisting with field reconnaissance
                to evaluate the impact of aquatic barriers, or even by reporting
                issues with the inventory data in this tool.
                <br />
                <br />
                <a href="mailto:kat@southeastaquatics.net">Contact us</a> to
                learn more about how you can help improve aquatic connectivity
                in the {name} region.
              </Paragraph>
            </Box>

            <Box>
              <GatsbyImage
                image={salmonPhoto}
                alt="Chum salmon, Allison Springs, WA"
              />

              <Box sx={{ fontSize: 0 }}>
                Photo:{' '}
                <OutboundLink to="https://www.flickr.com/photos/usfwspacific/51047491597/">
                  Chum salmon, Allison Springs, WA. Roger Tabor / U.S. Fish and
                  Wildlife Service.
                </OutboundLink>
              </Box>
            </Box>
          </Grid>
        </Box>
      </Container>
    </Layout>
  )
}

PNWRegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    salmonPhoto: PropTypes.object.isRequired,
    map: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query PNWRegionPageQuery {
    headerImage: file(relativePath: { eq: "47700011012_3ca83183ec_5k.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    salmonPhoto: file(relativePath: { eq: "51047491597_9e44ea2b53_c.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 960
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    map: file(relativePath: { eq: "maps/pnw.png" }) {
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

export default PNWRegionPage

export const Head = () => <SEO title={`${name} Region`} />
