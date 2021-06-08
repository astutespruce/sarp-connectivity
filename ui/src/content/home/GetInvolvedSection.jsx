import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import { Box, Heading, Paragraph, Grid, Image } from 'theme-ui'

import { Link, OutboundLink } from 'components/Link'

import SARPLogoImage from 'images/sarp_logo.png'

const SARP = () => {
  const {
    forestStreamPhoto: {
      childImageSharp: { gatsbyImageData: forestStreamPhoto },
    },
    gaTeamPhoto: {
      childImageSharp: { gatsbyImageData: gaTeamPhoto },
    },
  } = useStaticQuery(graphql`
    query {
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
  `)

  return (
    <>
      <Box variant="boxes.section">
        <Heading as="h2" variant="heading.section">
          How to get involved?
        </Heading>

        <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '2rem' }}>
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
            </Paragraph>
          </Box>
          <Box>
            <Image src={SARPLogoImage} sx={{ maxWidth: '250px' }} />
          </Box>
        </Grid>
      </Box>

      <Box variant="boxes.section" sx={{ mt: '4rem' }}>
        <Grid columns={[0, '3fr 5fr']} gap={5}>
          <Box>
            <GatsbyImage
              image={forestStreamPhoto}
              alt="Sam D. Hamilton Noxubee National Wildlife Refuge"
            />

            <Box sx={{ fontSize: 0 }}>
              Photo:{' '}
              <OutboundLink to="https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/">
                Sam D. Hamilton Noxubee National Wildlife Refuge in Mississippi.
                U.S. Fish and Wildlife Service.
              </OutboundLink>
            </Box>
          </Box>

          <Paragraph>
            SARP works with partners to protect, conserve, and restore aquatic
            resources including habitats throughout the Southeast for the
            continuing benefit, use, and enjoyment of the American people. SARP
            is also one of the first Fish Habitat Partnerships under the the
            National Fish Habitat Partnership umbrella that works to conserve
            and protect the nation’s fisheries and aquatic systems through a
            network of 20 Fish Habitat Partnerships.
          </Paragraph>
        </Grid>
      </Box>

      <Box variant="boxes.section" sx={{ mt: '4rem' }}>
        <Grid columns={[0, '5fr 3fr']} gap={5}>
          <Paragraph>
            SARP and partners have been working to build a community of practice
            surrounding barrier removal through the development of state-based
            Aquatic Connectivity Teams (ACTs). These teams create a forum that
            allows resource managers from all sectors to work together and share
            resources, disseminate information, and examine regulatory
            streamlining processes as well as project management tips and
            techniques. These teams are active in Arkansas, Florida, Georgia,
            North Carolina, South Carolina, Tennessee, and Virginia.
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

      <Box variant="boxes.section" sx={{ mt: '4rem' }}>
        <Grid columns={[0, '5fr 3fr']} gap={5}>
          <Box>
            <Heading as="h2" sx={{ fontWeight: 'normal' }}>
              Get involved!
            </Heading>
            <Paragraph sx={{ mt: '1rem' }}>
              You can help improve the inventory by sharing data, assisting with
              field reconnaissance to evaluate the impact of aquatic barriers,
              joining an{' '}
              <Link to="/regions/southeast/teams">
                Aquatic Connectivity Team
              </Link>
              , or even by reporting issues with the inventory data in this
              tool.
              <br />
              <br />
              <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
              more about how you can help improve aquatic connectivity in the
              Southeast.
            </Paragraph>
          </Box>

          <Box>
            <Heading as="h2" sx={{ fontWeight: 'normal' }}>
              Need Help?
            </Heading>
            <Paragraph sx={{ mt: '1rem' }}>
              If you are not able to get what you need from this tool or if you
              need to report an issue, please&nbsp;
              <a href="mailto:kat@southeastaquatics.net">let us know</a>!
            </Paragraph>
          </Box>
        </Grid>
      </Box>
    </>
  )
}

export default SARP
