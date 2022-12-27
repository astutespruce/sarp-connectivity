import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Grid, Heading, Paragraph } from 'theme-ui'

import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import HighlightBox from 'components/Layout/HighlightBox'

const ComplexityPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author: 'David Kovalenko.',
        url: 'https://unsplash.com/photos/qYMa2-P-U0M',
      }}
    />

    <Container>
      <Heading as="h1">Network complexity</Heading>
      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        A barrier that has upstream tributaries of different size classes, such
        as small streams, small rivers, and large rivers, would contribute a
        more complex connected aquatic network if it was removed. In contrast, a
        barrier with fewer upstream tributaries may contribute few if any size
        classes to the network if removed. In general, a more complex network
        composed of a greater range of size classes is more likely to have a
        wide range of available habitat for a greater number of aquatic species.
      </Paragraph>

      <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
        <HighlightBox icon="size_classes_low" title="No size classes gained">
          <p>
            Barriers that do not contribute any additional size classes are less
            likely to contribute a wide range of aquatic habitat.
          </p>
        </HighlightBox>

        <HighlightBox
          icon="size_classes_high"
          title="Several size classes gained"
        >
          <p>
            Barriers that have several size classes upstream are more likely to
            contribute a more complex network with a greater range of aquatic
            habitat for a greater variety of species.
          </p>
        </HighlightBox>
      </Grid>

      <Box variant="boxes.section" sx={{ mt: '6rem' }}>
        <Heading as="h2" variant="heading.section">
          Methods:
        </Heading>
        <ol>
          <li>
            Stream and river reaches were assigned to size classes based on
            total drainage area:
            <Box as="ul" sx={{ mb: '1rem' }}>
              <li>
                Headwaters: &lt; 10 km
                <sup>2</sup>
              </li>
              <li>
                Creeks: &ge; 10 km
                <sup>2</sup> and &lt; 100 km
                <sup>2</sup>
              </li>
              <li>
                Small rivers: &ge; 100 km
                <sup>2</sup> and &lt; 518 km
                <sup>2</sup>
              </li>
              <li>
                Medium tributary rivers: &ge; 519 km
                <sup>2</sup> and &lt; 2,590 km
                <sup>2</sup>
              </li>
              <li>
                Medium mainstem rivers: &ge; 2,590 km
                <sup>2</sup> and &lt; 10,000 km
                <sup>2</sup>
              </li>
              <li>
                Large rivers: &ge; 10,000 km
                <sup>2</sup> and &lt; 25,000 km
                <sup>2</sup>
              </li>
              <li>
                Great rivers: &ge; 25,000 km
                <sup>2</sup>
              </li>
            </Box>
          </li>
          <li>
            Each barrier is assigned the total number of unique size classes in
            its upstream functional network.
          </li>
        </ol>
      </Box>
    </Container>
  </Layout>
)

ComplexityPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NetworkComplexityQuery {
    headerImage: file(
      relativePath: { eq: "david-kovalenko-qYMa2-P-U0M-unsplash.jpg" }
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

export default ComplexityPage

export const Head = () => <SEO title="Network Complexity" />
