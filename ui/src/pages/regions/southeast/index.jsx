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
  Image,
  Paragraph,
  Text,
} from 'theme-ui'

import { useSummaryData } from 'components/Data'

import { Link, OutboundLink } from 'components/Link'
import { Layout } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import {
  RegionActionLinks,
  RegionStats,
  RegionStatesTable,
} from 'components/Regions'

import { formatNumber } from 'util/format'
import SARPLogoImage from 'images/sarp_logo.png'

import { REGION_STATES } from '../../../../config/constants'

const SERegionPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    map: {
      childImageSharp: { gatsbyImageData: map },
    },
    forestStreamPhoto: {
      childImageSharp: { gatsbyImageData: forestStreamPhoto },
    },
    gaTeamPhoto: {
      childImageSharp: { gatsbyImageData: gaTeamPhoto },
    },
  },
}) => {
  const { se } = useSummaryData()

  const { dams } = se

  return (
    <Layout title="Southeast Region">
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
        <Heading as="h1">Southeast Region</Heading>

        <Grid columns={2} gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
              <GatsbyImage
                image={map}
                alt="Southeast region map"
                sx={{ border: '1px solid', borderColor: 'grey.3' }}
              />
            </Box>
            <Text sx={{ fontSize: 1, color: 'grey.7' }}>
              Map of {formatNumber(dams)} inventoried dams in the southeast.
            </Text>
          </Box>
          <Box>
            <Heading as="h4" sx={{ mb: '0.5rem' }}>
              Includes {REGION_STATES.se.length - 1} states and Puerto Rico
              with:
            </Heading>

            <RegionStats {...se} />
          </Box>
        </Grid>

        <RegionActionLinks region="se" />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Southeast Aquatic Connectivity Program
          </Heading>
          <Grid columns="2fr 1fr" sx={{ mt: '0.5rem' }}>
            <Paragraph sx={{ mr: '2rem', flex: '1 1 auto' }}>
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
            </Paragraph>

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

          <Grid columns="4fr 1fr" sx={{ mt: '1rem' }}>
            <Paragraph>
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
            <Image
              src={SARPLogoImage}
              width="224px"
              height="113px"
              alt="SARP logo"
            />
          </Grid>
        </Box>

        <Divider sx={{ my: '4rem' }} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Statistics by state:
          </Heading>
          <Box sx={{ mt: '0.5rem' }}>
            <RegionStatesTable region="se" {...se} />
          </Box>
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
    map: PropTypes.isRequired,
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
    map: file(relativePath: { eq: "maps/se.png" }) {
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
