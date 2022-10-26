import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { SearchLocation } from '@emotion-icons/fa-solid'
import {
  Box,
  Container,
  Heading,
  Flex,
  Button,
  Divider,
  Paragraph,
} from 'theme-ui'

import { Link } from 'components/Link'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'

const PrioritizePage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author: 'American Public Power Association',
        url: 'https://unsplash.com/photos/FUeb2npsblQ',
      }}
    />

    <Container>
      <Heading as="h1">Prioritize barriers for removal</Heading>

      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        To prioritize barriers, you will work through the following steps:
      </Paragraph>

      <Box sx={{ mt: '2rem' }}>
        <Flex sx={{ alignItems: 'center' }}>
          <Box variant="boxes.step">1</Box>
          <Heading as="h3" sx={{ flex: '1 1 auto' }}>
            Select area of interest.
          </Heading>
        </Flex>
        <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
          You can select areas using state, county, watershed, and ecoregion
          boundaries.
        </Paragraph>
      </Box>

      <Box sx={{ mt: '2rem' }}>
        <Flex sx={{ alignItems: 'center' }}>
          <Box variant="boxes.step">2</Box>
          <Heading as="h3" sx={{ flex: '1 1 auto' }}>
            Filter barriers.
          </Heading>
        </Flex>
        <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
          You can filter barriers by feasibility, height, and other key
          characteristics to select those that best meet your needs.
        </Paragraph>
      </Box>

      <Box sx={{ mt: '2rem' }}>
        <Flex sx={{ alignItems: 'center' }}>
          <Box variant="boxes.step">3</Box>
          <Heading as="h3" sx={{ flex: '1 1 auto' }}>
            Explore priorities on the map.
          </Heading>
        </Flex>
        <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
          Once you have defined your area of interest and selected the barriers
          you want, you can explore them on the map.
        </Paragraph>
      </Box>

      <Box sx={{ mt: '2rem' }}>
        <Flex sx={{ alignItems: 'center' }}>
          <Box variant="boxes.step">4</Box>
          <Heading as="h3" sx={{ flex: '1 1 auto' }}>
            Download prioritized barriers.
          </Heading>
        </Flex>
        <Paragraph variant="help" sx={{ ml: '3.75rem' }}>
          You can download the inventory for your area of interest and perform
          offline work.
        </Paragraph>
      </Box>

      <Divider />

      <Heading as="h2">Get started now</Heading>

      <Flex
        sx={{
          alignItems: 'center',
          justifyContent: 'space-between',
          width: '100%',
          fontSize: '1.5rem',
          mt: '1rem',
          mb: '8rem',
        }}
      >
        <Box
          sx={{
            flex: '1 0 auto',
          }}
        >
          <Link to="/priority/dams">
            <Button>
              <SearchLocation size="1em" style={{ marginRight: '0.5rem' }} />
              Prioritize dams
            </Button>
          </Link>
        </Box>

        <Box
          sx={{
            flex: '0 0 auto',
          }}
        >
          <Link to="/priority/barriers">
            <Button>
              <SearchLocation size="1em" style={{ marginRight: '0.5rem' }} />
              Prioritize road-related barriers
            </Button>
          </Link>
        </Box>
      </Flex>
    </Container>
  </Layout>
)

PrioritizePage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query PrioritizeStartPageQuery {
    headerImage: file(
      relativePath: {
        eq: "american-public-power-association-430861-unsplash.jpg"
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
  }
`

export default PrioritizePage

export const Head = () => (
  <SEO title="Prioritize dams and road-related barriers" />
)
