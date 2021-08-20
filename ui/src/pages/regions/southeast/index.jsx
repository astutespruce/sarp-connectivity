import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
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

const SERegionPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    forestStreamPhoto: {
      childImageSharp: { gatsbyImageData: forestStreamPhoto },
    },
    gaTeamPhoto: {
      childImageSharp: { gatsbyImageData: gaTeamPhoto },
    },
  },
}) => {
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
        image={headerImage}
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
              jurisdictional boundaries. SARP works with partners to protect,
              conserve, and restore aquatic resources including habitats
              throughout the Southeast for the continuing benefit, use, and
              enjoyment of the American people. SARP is also one of the first
              Fish Habitat Partnerships under the the National Fish Habitat
              Partnership umbrella that works to conserve and protect the
              nation’s fisheries and aquatic systems through a network of 20
              Fish Habitat Partnerships.
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

          <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
            <Box
              as="ul"
              sx={{
                listStyle: 'none',
                fontSize: '1.25rem',
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
                <b>{formatNumber(on_network_dams, 0)}</b> dams that have been
                analyzed for their impacts to aquatic connectivity in this tool.
              </li>
              <li>
                <b>{formatNumber(miles, 0)}</b> miles of connected rivers and
                streams on average across the region.
              </li>
            </Box>
            <Box>
              <GatsbyImage
                image={forestStreamPhoto}
                alt="Sam D. Hamilton Noxubee National Wildlife Refuge"
              />

              <Box sx={{ fontSize: 0 }}>
                Photo:{' '}
                <OutboundLink to="https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/">
                  Sam D. Hamilton Noxubee National Wildlife Refuge in
                  Mississippi. U.S. Fish and Wildlife Service.
                </OutboundLink>
              </Box>
            </Box>
          </Grid>
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <i>inventoried</i> dams and
            road-related barriers. Because the inventory is incomplete in many
            areas, areas with a high number of dams may simply represent areas
            that have a more complete inventory.
            <br />
            <br />
            {formatNumber(offNetworkDams, 0)} dams and{' '}
            {formatNumber(offNetworkBarriers, 0)} road-related barriers were not
            analyzed because they could not be correctly located on the aquatic
            network or were otherwise excluded from the analysis.
          </Paragraph>
        </Box>

        <Divider sx={{ my: '4rem' }} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            How to get involved?
          </Heading>

          <Grid columns={[0, '5fr 3fr']} gap={5}>
            <Paragraph>
              SARP and partners have been working to build a community of
              practice surrounding barrier removal through the development of
              state-based Aquatic Connectivity Teams (ACTs). These teams create
              a forum that allows resource managers from all sectors to work
              together and share resources, disseminate information, and examine
              regulatory streamlining processes as well as project management
              tips and techniques. These teams are active in Arkansas, Florida,
              Georgia, North Carolina, South Carolina, Tennessee, and Virginia.
              <br />
              <br />
              <Link to="/regions/southeast/teams">
                Learn more about aquatic connectivity teams in the Southeast.
              </Link>
            </Paragraph>

            <Box>
              <GatsbyImage
                image={gaTeamPhoto}
                alt="Georgia Aquatic Connectivity Team"
              />
              <Box sx={{ fontSize: 0 }}>
                Photo:{' '}
                <OutboundLink to="https://www.southeastaquatics.net/news/white-dam-removal-motivates-georgia-conservation-practitioners">
                  Georgia Aquatic Connectivity Team
                </OutboundLink>
              </Box>
            </Box>
          </Grid>
        </Box>
        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            You can help!
          </Heading>
          <Paragraph sx={{ mt: '1rem' }}>
            You can help improve the inventory by sharing data, assisting with
            field reconnaissance to evaluate the impact of aquatic barriers,
            joining an{' '}
            <Link to="/regions/southeast/teams">Aquatic Connectivity Team</Link>
            , or even by reporting issues with the inventory data in this tool.
            <br />
            <br />
            <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
            more about how you can help improve aquatic connectivity in the
            Southeast.
          </Paragraph>
        </Box>
      </Container>
    </Layout>
  )
}

SERegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    forestStreamPhoto: PropTypes.object.isRequired,
    gaTeamPhoto: PropTypes.object.isRequired,
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
    forestStreamPhoto: file(
      relativePath: { eq: "6882770647_60c0d68a9c_z.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 960
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    gaTeamPhoto: file(relativePath: { eq: "GA_ACT_small.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 640
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
  }
`

export default SERegionPage
