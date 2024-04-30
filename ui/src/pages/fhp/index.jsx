import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Flex, Grid, Heading, Image, Paragraph } from 'theme-ui'

import { FISH_HABITAT_PARTNERSHIPS } from 'config'
import { Link, OutboundLink } from 'components/Link'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { dynamicallyLoadImage } from 'util/dom'
import NFHPLogo from 'images/nfhp_logo.svg'

const FHPListPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author: 'Brook trout,  Jason Ross/USFWS',
        url: 'https://www.flickr.com/photos/usfwsmidwest/34597621345/',
      }}
    />

    <Container>
      <Heading as="h1">Fish Habitat Partnerships</Heading>
      <Grid columns="2fr 1fr" gap={5} sx={{ mt: '1rem' }}>
        <Paragraph variant="paragraph.large">
          The{' '}
          <OutboundLink to="https://www.fishhabitat.org/">
            {' '}
            National Fish Habitat Partnership
          </OutboundLink>{' '}
          works to conserve and protect the nation&apos;s fisheries and aquatic
          systems through a network of 20 Fish Habitat Partnerships.
        </Paragraph>
        <Box>
          <OutboundLink to="https://www.fishhabitat.org/">
            <Image
              src={NFHPLogo}
              sx={{ width: '264px', height: '56px' }}
              alt="National Fish Habitat Partnership logo"
            />
          </OutboundLink>
        </Box>
      </Grid>

      <Heading as="h4" sx={{ mt: '3rem' }}>
        View more about the status of the inventory in each Fish Habitat
        Partnership:
      </Heading>
      {/* <Box as="ul" sx={{ mt: '0.5rem', ml: '1rem' }}>
        {Object.entries(FISH_HABITAT_PARTNERSHIPS)
          .sort(([leftId], [rightId]) => (leftId < rightId ? -1 : 1))
          .map(([id, { name }]) => (
            <Box key={id} as="li">
              <Link to={`/fhp/${id}`}>{name}</Link>
            </Box>
          ))}
      </Box> */}
      <Grid columns={3} gap={4} sx={{ mt: '1rem', bg: 'grey.0', p: '1rem' }}>
        {Object.entries(FISH_HABITAT_PARTNERSHIPS)
          .sort(([leftId], [rightId]) => (leftId < rightId ? -1 : 1))
          .map(([id, { name }]) => (
            <Link key={id} to={`/fhp/${id}`}>
              <Box
                sx={{
                  p: '1rem',
                  bg: '#FFF',
                  border: '1px solid',
                  borderColor: 'grey.1',
                  borderRadius: '0.5rem',
                  height: '100%',
                  '&:hover': {
                    borderColor: 'grey.8',
                    boxShadow: '1px 1px 3px #333',
                  },
                }}
              >
                <Flex
                  sx={{
                    justifyContent: 'flex-end',
                    flexDirection: 'column',
                    height: '3rem',
                  }}
                >
                  <Heading
                    as="h4"
                    sx={{
                      flex: '0 0 auto',
                      fontWeight: 'normal',
                      mr: '0.5rem',
                    }}
                  >
                    {name}
                  </Heading>
                </Flex>

                <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
                  <Image
                    src={dynamicallyLoadImage(`maps/fhp/${id}.png`)}
                    alt={`${name} region map`}
                  />
                </Box>
              </Box>
            </Link>
          ))}
      </Grid>
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
    headerImage: file(relativePath: { eq: "34597621345_26d60382fd_o.jpg" }) {
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
