import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'

import {
  Box,
  Container,
  Divider,
  Grid,
  Heading,
  Paragraph,
  Text,
} from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { useSummaryData } from 'components/Data'
import { StateDownloadTable } from 'components/Download'
import { Layout } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { RegionActionLinks, RegionStats } from 'components/Regions'

import { formatNumber } from 'util/format'

import { REGION_STATES } from '../../../../config/constants'

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
  const { pnw } = useSummaryData()

  return (
    <Layout title="Pacific Northwest Region">
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
        <Heading as="h1">Pacific Northwest Region</Heading>

        <Grid columns={2} gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
              <GatsbyImage
                image={map}
                alt="Northwest region map"
                sx={{ border: '1px solid', borderColor: 'grey.3' }}
              />
            </Box>
            <Text sx={{ fontSize: 1, color: 'grey.7' }}>
              Map of {formatNumber(pnw.dams)} inventoried dams in the Northwest
              region.
            </Text>
          </Box>
          <Box>
            <Heading as="h4" sx={{ mb: '1rem' }}>
              Includes {REGION_STATES.pnw.length} states with:
            </Heading>

            <RegionStats {...pnw} />
          </Box>
        </Grid>

        <RegionActionLinks region="pnw" />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Data Sources
          </Heading>

          <Grid columns="2fr 1fr" sx={{ mt: '0.5rem' }}>
            <Paragraph sx={{ mr: '2rem', flex: '1 1 auto' }}>
              TODO: content from SARP to indicate data sources in the PNW
            </Paragraph>

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

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Statistics by state:
          </Heading>
          <Box sx={{ mt: '0.5rem' }}>
            <StateDownloadTable region="pnw" {...pnw} />
          </Box>
        </Box>

        <Divider sx={{ my: '4rem' }} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            You can help!
          </Heading>
          <Paragraph sx={{ mt: '1rem' }}>
            You can help improve the inventory You can help improve the
            inventory by sharing data, assisting with field reconnaissance to
            evaluate the impact of aquatic barriers, or even by reporting issues
            with the inventory data in this tool.
            <br />
            <br />
            <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
            more about how you can help improve aquatic connectivity in the
            Northwest.
          </Paragraph>
        </Box>
      </Container>
    </Layout>
  )
}

PNWRegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    forestStreamPhoto: PropTypes.object.isRequired,
    map: PropTypes.isRequired,
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
