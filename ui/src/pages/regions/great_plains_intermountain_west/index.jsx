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

import { useSummaryData } from 'components/Data'
import { StateDownloadTable } from 'components/Download'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { RegionActionLinks, RegionStats } from 'components/Regions'

import { formatNumber } from 'util/format'

import { REGION_STATES } from '../../../../config/constants'

const GPIWRegionPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    map: {
      childImageSharp: { gatsbyImageData: map },
    },
  },
}) => {
  const { gpiw } = useSummaryData()

  return (
    <Layout>
      <HeaderImage
        image={headerImage}
        height="20vh"
        minHeight="18rem"
        credits={{
          author: 'Dillon Fancher',
          url: 'https://unsplash.com/photos/E1FpiiUhRJ0',
        }}
      />

      <Container>
        <Heading as="h1">Great Plains & Intermountain West Region</Heading>

        <Grid columns={2} gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
              <GatsbyImage
                image={map}
                alt="Great Plains & Intermountain West region map"
                sx={{ border: '1px solid', borderColor: 'grey.3' }}
              />
            </Box>
            <Text sx={{ fontSize: 1, color: 'grey.7' }}>
              Map of {formatNumber(gpiw.dams)} inventoried dams in the Great
              Plains & Intermountain West region.
            </Text>
          </Box>
          <Box>
            <Heading as="h4" sx={{ mb: '1rem' }}>
              Includes {REGION_STATES.gpiw.length} states with:
            </Heading>

            <RegionStats {...gpiw} />
          </Box>
        </Grid>

        <RegionActionLinks region="gpiw" />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Statistics by state:
          </Heading>
          <Box sx={{ mt: '0.5rem' }}>
            <StateDownloadTable region="gpiw" {...gpiw} />
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
            Great Plains & Intermountain West.
          </Paragraph>
        </Box>
      </Container>
    </Layout>
  )
}

GPIWRegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    map: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query GPIWRegionPageQuery {
    headerImage: file(
      relativePath: { eq: "dillon-fancher-E1FpiiUhRJ0-unsplash.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    map: file(relativePath: { eq: "maps/gpiw.png" }) {
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

export default GPIWRegionPage

export const Head = () => (
  <SEO title="Great Plains & Intermountain West Region" />
)
