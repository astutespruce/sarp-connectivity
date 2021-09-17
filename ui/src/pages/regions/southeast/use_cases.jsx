import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import { Box, Container, Heading, Paragraph } from 'theme-ui'

import { Layout } from 'components/Layout'
import { OutboundLink } from 'components/Link'
import { HeaderImage } from 'components/Image'

const SoutheastRegionUseCases = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    removalImage: {
      childImageSharp: { gatsbyImageData: removalImage },
    },
  },
}) => (
  <Layout title="Example: prioritizing a failing dam for removal">
    <HeaderImage
      image={headerImage}
      height="30vh"
      minHeight="24rem"
      credits={{
        author:
          'Steeles Mill Dam Hitchcock Creek during removal. Peter Raabe, American Rivers.',
        url: null,
      }}
    />

    <Container>
      <Heading as="h1">Prioritizing a failing dam for removal</Heading>

      <Paragraph sx={{ mt: '1rem' }}>
        This Aquatic Barrier Inventory tool will enable partners to identify and
        prioritize aging dams for removal, such as the Roaring River Dam in
        Tennessee removed in 2017. At 220 feet wide and 15 tall, this dam is the
        largest removed in Tennessee for river and stream restoration.
        <br />
        <br />
        Built in 1976 by the U.S. Army Corps of Engineers to keep reservoir fish
        species from migrating upstream, partners determined that this
        deteriorating dam no longer met its original purpose. Instead of
        repairing the dam, partners decided that it would be better to remove
        the dam altogether in order to restore aquatic connectivity. Partners
        working on this project included the Tennessee Wildlife Resources
        Agency, the U.S. Army Corps of Engineers, The Nature Conservancy, the
        U.S. Fish and Wildlife Service, and the Southeast Aquatic Resources
        Partnership.
      </Paragraph>

      <Box my="4rem">
        <GatsbyImage
          image={removalImage}
          alt="Roaring River Dam Removal, Tennessee"
        />
        <Box sx={{ fontSize: 0 }}>
          Photo:{' '}
          <OutboundLink to="https://www.nature.org/en-us/about-us/where-we-work/united-states/tennessee/stories-in-tennessee/dam-removal-opens-up-roaring-river/">
            Roaring River Dam Removal, Tennessee, 2017. © Rob Bullard, The
            Nature Conservancy.
          </OutboundLink>
        </Box>
      </Box>
    </Container>
  </Layout>
)

SoutheastRegionUseCases.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    removalImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query SoutheastRegionUseCasesQuery {
    headerImage: file(
      relativePath: {
        eq: "Steeles_Mill_Dam_Hitchcock_Creek_during_removal__Peter_Raabe_A.jpg"
      }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    removalImage: file(
      relativePath: {
        eq: "Roaring_River_Dam_Removal_-_digging_-_Paul_Kingsbury_TNC_P1030732.jpg"
      }
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
`

export default SoutheastRegionUseCases
