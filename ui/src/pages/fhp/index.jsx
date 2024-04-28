import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Heading, Paragraph } from 'theme-ui'

import { FISH_HABITAT_PARTNERSHIPS } from 'config'
import { Link, OutboundLink } from 'components/Link'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'

const FHPListPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author:
          'Loakfoma Creek, Noxubee National Wildlife Refuge, Mississippi. U.S. Fish and Wildlife Service.',
        url: 'https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/',
      }}
    />

    <Container>
      <Heading as="h1">Fish Habitat Partnerships</Heading>
      <Paragraph variant="paragraph.large">
        The{' '}
        <OutboundLink to="https://www.fishhabitat.org/">
          {' '}
          National Fish Habitat Partnership
        </OutboundLink>{' '}
        works to conserve and protect the nation&apos;s fisheries and aquatic
        systems through a network of 20 Fish Habitat Partnerships.
      </Paragraph>
      <Heading as="h4" sx={{ mt: '2rem' }}>
        View more about the status of the inventory in each Fish Habitat
        Partnership:
      </Heading>
      <Box as="ul" sx={{ mt: '0.5rem', ml: '1rem' }}>
        {Object.entries(FISH_HABITAT_PARTNERSHIPS)
          .sort(([leftId], [rightId]) => (leftId < rightId ? -1 : 1))
          .map(([id, { name }]) => (
            <Box key={id} as="li">
              <Link to={`/fhp/${id}`}>{name}</Link>
            </Box>
          ))}
      </Box>
    </Container>
  </Layout>
)

FHPListPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query FHPListPageQuery {
    headerImage: file(relativePath: { eq: "6882770647_c43a945282_o.jpg" }) {
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

export default FHPListPage

export const Head = () => <SEO title="Fish Habitat Partnerships" />
