import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Divider, Grid, Heading, Paragraph } from 'theme-ui'

import { useSummaryData } from 'components/Data'
import { Layout } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { formatNumber } from 'util/format'

import { REGION_STATES, STATES } from '../../../../config/constants'

const GPIWRegionPage = ({ data: { headerImage } }) => {
  const {
    gpiw: {
      dams,
      onNetworkDams,
      miles,
      totalSmallBarriers,
      smallBarriers,
      onNetworkSmallBarriers,
      crossings,
    },
  } = useSummaryData()

  const offNetworkDams = dams - onNetworkDams
  const offNetworkBarriers = smallBarriers - onNetworkSmallBarriers

  const totalRoadBarriers = totalSmallBarriers + crossings

  return (
    <Layout title="Great Plains & Intermountain West Aquatic Connectivity">
      <HeaderImage
        image={headerImage.childImageSharp.gatsbyImageData}
        height="20vh"
        minHeight="18rem"
        credits={{
          author: 'Dillon Fancher',
          url: 'https://unsplash.com/photos/E1FpiiUhRJ0',
        }}
      />

      <Container>
        <Heading as="h1">
          Great Plains &amp; Intermountain West Aquatic Connectivity
        </Heading>

        <Grid columns="2fr 1fr" gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Paragraph>Content about this region goes here</Paragraph>
          </Box>

          <Box>
            <Heading as="h4">
              Includes <b>{REGION_STATES.gpiw.length}</b> states:
            </Heading>
            <Box
              as="ul"
              sx={{
                'li + li': {
                  mt: 0,
                },
              }}
            >
              {REGION_STATES.gpiw.map((id) => (
                <li key={id}>{STATES[id]}</li>
              ))}
            </Box>
          </Box>
        </Grid>

        <Divider sx={{ my: '4rem' }} />

        <Box>
          <Heading as="h2">Regional statistics:</Heading>

          <Grid columns={3} gap={4} sx={{ mt: '2rem' }}>
            <Box
              as="ul"
              sx={{
                listStyle: 'none',
                fontSize: '1.25rem',
                mt: '1rem',
                ml: 0,
                p: 0,
                lineHeight: 1.3,
                li: {
                  mb: '2rem',
                },
              }}
            >
              <li>
                <b>{formatNumber(dams, 0)}</b> inventoried dams.
              </li>
              <li>
                <b>{formatNumber(onNetworkDams, 0)}</b> dams that have been
                analyzed for their impacts to aquatic connectivity in this tool.
              </li>
              <li>
                <b>{formatNumber(miles, 0)}</b> miles of connected rivers and
                streams on average across the region.
              </li>
            </Box>
            <Paragraph variant="help" sx={{ mt: '2rem' }}>
              Note: These statistics are based on <i>inventoried</i> dams and
              road-related barriers. Because the inventory is incomplete in many
              areas, areas with a high number of dams may simply represent areas
              that have a more complete inventory.
              <br />
              <br />
              {formatNumber(offNetworkDams, 0)} dams and{' '}
              {formatNumber(offNetworkBarriers, 0)} road-related barriers were
              not analyzed because they could not be correctly located on the
              aquatic network or were otherwise excluded from the analysis.
            </Paragraph>
          </Grid>
        </Box>
      </Container>
    </Layout>
  )
}

GPIWRegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
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
  }
`

export default GPIWRegionPage
