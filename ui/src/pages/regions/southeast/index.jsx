import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import {
  Box,
  Container,
  Divider,
  Flex,
  Grid,
  Heading,
  Image,
  Paragraph,
} from 'theme-ui'

import { useSummaryData } from 'components/Data'
import { Link, OutboundLink } from 'components/Link'
import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { formatNumber } from 'util/format'
import SARPLogoImage from 'images/sarp_logo.png'

import { REGION_STATES, STATES } from '../../../../config/constants'

const SERegionPage = ({ data: { headerImage } }) => {
  const {
    se: {
      dams,
      on_network_dams,
      miles,
      total_barriers,
      barriers,
      on_network_barriers,
      crossings,
    },
  } = useSummaryData()

  const offNetworkDams = dams - on_network_dams
  const offNetworkBarriers = barriers - on_network_barriers

  const totalRoadBarriers = total_barriers + crossings

  return (
    <Layout title="Southeast Aquatic Connectivity Program">
      <HeaderImage
        image={headerImage.childImageSharp.gatsbyImageData}
        height="20vh"
        minHeight="18rem"
        credits={{
          author: 'Dillon Groves',
          url: 'https://unsplash.com/photos/cyxtMIhirDw',
        }}
      />

      <Container>
        <Heading as="h1">Southeast Aquatic Connectivity Program</Heading>

        <Grid columns="2fr 1fr" gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Paragraph>
              The&nbsp;
              <OutboundLink to="https://southeastaquatics.net/">
                Southeast Aquatic Resources Partnership
              </OutboundLink>
              &nbsp; (SARP) was formed by the Southeastern Association of Fish
              and Wildlife Agencies (SEAFWA) to protect aquatic resources across
              political boundaries as many of our river systems cross multiple
              jurisdictional boundaries.
              <br />
              <br />
              SARP and partners within the region have been working for several
              years to compile a comprehensive inventory of aquatic barriers
              across the region. This inventory is the foundation of{' '}
              <OutboundLink to="https://southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap">
                SARP&apos;s Connectivity Program
              </OutboundLink>{' '}
              because it empowers{' '}
              <Link to="/regions/southeast/teams">
                Aquatic Connectivity Teams
              </Link>{' '}
              and other collaborators with the best available information on
              aquatic barriers.
            </Paragraph>
            <Flex sx={{ justifyContent: 'center', width: '100%', mt: '2rem' }}>
              <Image src={SARPLogoImage} width="224px" alt="SARP logo" />
            </Flex>
          </Box>

          <Box>
            <Heading as="h4">
              Includes <b>{REGION_STATES.se.length - 1}</b> states and Puerto
              Rico:
            </Heading>
            <Box
              as="ul"
              sx={{
                'li + li': {
                  mt: 0,
                },
              }}
            >
              {REGION_STATES.se.map((id) => (
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
                <b>{formatNumber(dams, 0)}</b> inventoried dams
              </li>
              <li>
                <b>{formatNumber(on_network_dams, 0)}</b> dams that have been
                analyzed for their impacts to aquatic connectivity in this tool
              </li>
              <li>
                <b>{formatNumber(miles, 0)}</b> miles of connected rivers and
                streams on average across the region
              </li>
              <li>
                <b>{formatNumber(miles, 0)}</b> miles of connected perennial
                rivers and streams on average across the region (excluding
                ephemeral and intermittent streams)
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

SERegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query SERegionPagePageQuery {
    headerImage: file(
      relativePath: { eq: "dillon-groves-cyxtMIhirDw-unsplash.jpg" }
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

export default SERegionPage
