import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Grid, Heading, Paragraph } from 'theme-ui'

import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'

import HighlightBox from 'components/Layout/HighlightBox'

const SinuosityPage = ({ data: { headerImage } }) => (
  <Layout title="Network Sinuosity">
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author: 'Carl Cerstrand',
        url: 'https://unsplash.com/photos/J2bNC9gW5NI',
      }}
    />

    <Container>
      <Heading as="h1">Network sinuosity</Heading>
      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        Network sinuosity is a measure of how much the path of the river or
        stream deviates from a straight line. In general, rivers and streams
        that are more sinuous generally indicate those that have lower
        alteration from human disturbance such as channelization and diking,
        whereas rivers that have been extensively altered tend to be less
        sinuous. Sinuosity ranges from low (&lt;1.2) to moderate (1.2 - 1.5) to
        high (&gt;1.5) (Rosgen, 1996).
      </Paragraph>

      <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
        <HighlightBox icon="sinuosity_low" title="Low sinuosity">
          <p>
            Rivers and streams with lower sinuosity may be more altered by
            artificial channelization and may have a lower variety of in-stream
            habitat. Barriers with less sinuous upstream networks may contribute
            less natural habitat if removed.
          </p>
        </HighlightBox>

        <HighlightBox icon="sinuosity_high" title="High sinuosity">
          <p>
            Rivers and streams with high sinuosity are likely less altered by
            artificial channelization and may have a wider variety of in-stream
            habitat. Barriers with more sinuous upstream networks may contribute
            more natural habitat if removed.
          </p>
        </HighlightBox>
      </Grid>

      <Box variant="boxes.section" sx={{ mt: '6rem' }}>
        <Heading as="h2" variant="heading.section">
          Methods:
        </Heading>
        <ol>
          <li>
            The sinuosity of each stream is calculated as the ratio between the
            length of that reach and the straight line distance between the
            endpoints of that reach. The greater the total length compared to
            the straight line distance, the higher the sinuosity.
          </li>
          <li>
            Reaches are combined using a length-weighted average to calculate
            the overall sinuosity of each functional network.
          </li>
        </ol>
      </Box>
      <Box variant="boxes.section">
        <Heading as="h2" variant="heading.section">
          References:
        </Heading>
        <ul>
          <li>
            Rosgen, David L. 1996. Applied river morphology. Pagosa Springs,
            Colo: Wildland Hydrology.
          </li>
        </ul>
      </Box>
    </Container>
  </Layout>
)

SinuosityPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NetworkSinuosityQuery {
    headerImage: file(
      relativePath: { eq: "carl-cerstrand-J2bNC9gW5NI-unsplash.jpg" }
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

export default SinuosityPage
