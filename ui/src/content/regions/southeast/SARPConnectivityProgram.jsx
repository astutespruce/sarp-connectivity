import React from 'react'
import { useStaticQuery, graphql } from 'gatsby'
import { Box, Heading, Grid, Image, Paragraph } from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'

import { OutboundLink } from 'components/Link'

import SARPLogoImage from 'images/sarp_logo.png'

const SARPConnectivityProgram = () => {
  const {
    forestStreamPhoto: {
      childImageSharp: { gatsbyImageData: forestStreamPhoto },
    },
  } = useStaticQuery(graphql`
    query SARPConnectivityProgramQuery {
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
    }
  `)

  return (
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
          &nbsp; (SARP) was formed by the Southeastern Association of Fish and
          Wildlife Agencies (SEAFWA) to protect aquatic resources across
          political boundaries as many of our river systems cross multiple
          jurisdictional boundaries. SARP works with partners to protect,
          conserve, and restore aquatic resources including habitats throughout
          the Southeast for the continuing benefit, use, and enjoyment of the
          American people. SARP is also one of the first Fish Habitat
          Partnerships under the the National Fish Habitat Partnership umbrella
          that works to conserve and protect the nation&apos;s fisheries and
          aquatic systems through a network of 20 Fish Habitat Partnerships.
        </Paragraph>

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
      </Grid>

      <Grid columns="4fr 1fr" sx={{ mt: '1rem' }}>
        <Paragraph>
          SARP and partners within the region have been working for several
          years to compile a comprehensive inventory of aquatic barriers across
          the region. This inventory is the foundation of{' '}
          <OutboundLink to="https://southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap">
            SARP&apos;s Connectivity Program
          </OutboundLink>{' '}
          because it empowers Aquatic Connectivity Teams and other collaborators
          with the best available information on aquatic barriers.
        </Paragraph>
        <Image
          src={SARPLogoImage}
          width="224px"
          height="113px"
          alt="SARP logo"
        />
      </Grid>
    </Box>
  )
}

export default SARPConnectivityProgram
