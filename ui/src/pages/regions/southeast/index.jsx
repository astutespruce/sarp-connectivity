import React from 'react'
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

import { useSummaryData } from 'components/Data'
import { StateDownloadTable } from 'components/Download'
import { OutboundLink } from 'components/Link'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { RegionActionLinks, RegionStats } from 'components/Regions'
import { CONNECTIVITY_TEAMS, REGIONS, STATES } from 'config'
import { groupBy } from 'util/data'
import { formatNumber } from 'util/format'
import { extractNodes } from 'util/graphql'
import SARPLogoImage from 'images/sarp_logo.png'

const regionID = 'se'
const {
  [regionID]: { name, states },
} = REGIONS

const SERegionPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    map: {
      childImageSharp: { gatsbyImageData: map },
    },
    imagesSharp,
    forestStreamPhoto: {
      childImageSharp: { gatsbyImageData: forestStreamPhoto },
    },
  },
}) => {
  const { [regionID]: summary } = useSummaryData()

  const images = groupBy(extractNodes(imagesSharp), 'state')

  return (
    <Layout>
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
              Includes {states.length - 2} states, Puerto Rico, and U.S. Virgin
              Islands with:
            </Heading>

            <RegionStats {...summary} />
          </Box>
        </Grid>

        <RegionActionLinks region={regionID} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Southeast Aquatic Connectivity Program
          </Heading>
          <Grid columns="2fr 1fr" sx={{ mt: '0.5rem' }}>
            <Paragraph sx={{ mr: '2rem', flex: '1 1 auto' }}>
              The&nbsp;
              <OutboundLink to="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
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
              nation&apos;s fisheries and aquatic systems through a network of
              20 Fish Habitat Partnerships.
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
              because it empowers Aquatic Connectivity Teams and other
              collaborators with the best available information on aquatic
              barriers.
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
            <StateDownloadTable region={regionID} {...summary} />
          </Box>
        </Box>

        <Divider sx={{ my: '4rem' }} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            How to get involved?
          </Heading>

          <Grid columns={[0, 2]} gap={5}>
            <Box>
              <Paragraph>
                SARP and partners have been working to build a community of
                practice surrounding barrier removal through the development of
                state-based Aquatic Connectivity Teams (ACTs). These teams
                create a forum that allows resource managers from all sectors to
                work together and share resources, disseminate information, and
                examine regulatory streamlining processes as well as project
                management tips and techniques.
              </Paragraph>
            </Box>
            <Box>
              <Heading as="h4">Aquatic connectivity teams:</Heading>
              <Box as="ul" sx={{ mt: '0.5rem' }}>
                {Object.entries(CONNECTIVITY_TEAMS.southeast).map(
                  ([state, team]) => (
                    <li key={state}>
                      {STATES[state]}:{' '}
                      <OutboundLink to={team.url}>{team.name}</OutboundLink>
                    </li>
                  )
                )}
              </Box>
            </Box>
          </Grid>

          <Grid
            columns={Object.keys(images).length}
            gap={2}
            sx={{ mt: '2rem' }}
          >
            {Object.entries(images)
              .slice(0, 4)
              .map(
                ([
                  state,
                  {
                    childImageSharp: { gatsbyImageData },
                  },
                ]) => (
                  <Box
                    key={state}
                    sx={{ maxHeight: '8rem', overflow: 'hidden' }}
                  >
                    <GatsbyImage
                      image={gatsbyImageData}
                      alt={`${state} aquatic connectivity team photo`}
                    />
                  </Box>
                )
              )}
          </Grid>
        </Box>
        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            You can help!
          </Heading>
          <Paragraph sx={{ mt: '1rem' }}>
            You can help improve the inventory by sharing data, assisting with
            field reconnaissance to evaluate the impact of aquatic barriers,
            joining an Aquatic Connectivity Team, or even by reporting issues
            with the inventory data in this tool.
            <br />
            <br />
            <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
            more about how you can help improve aquatic connectivity in the{' '}
            {name} region.
          </Paragraph>
        </Box>
      </Container>
    </Layout>
  )
}

SERegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    map: PropTypes.object.isRequired,
    forestStreamPhoto: PropTypes.object.isRequired,
    imagesSharp: PropTypes.object.isRequired,
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
    imagesSharp: allFile(filter: { relativeDirectory: { eq: "teams" } }) {
      edges {
        node {
          state: name
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
    }
  }
`

export default SERegionPage

export const Head = () => <SEO title={`${name} Region`} />
