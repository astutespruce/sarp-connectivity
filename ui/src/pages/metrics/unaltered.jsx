import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Grid, Heading, Paragraph } from 'theme-ui'

import { Layout } from 'components/Layout'
import { HeaderImage } from 'components/Image'

import HighlightBox from 'components/Layout/HighlightBox'

const PercentUnalteredPage = ({ data: { headerImage } }) => (
  <Layout title="Channel Alteration">
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
      <Heading as="h1">Channel alteration</Heading>
      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        Altered river and stream segments are those that are specifically
        identified as canals or ditches. These represent areas where the
        hydrography, flow, and water quality may be highly altered compared to
        natural conditions.
        <br />
        <br />
        Networks are characterized by the percent of their total network length
        that is in altered river and stream segments.
      </Paragraph>

      <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
        <HighlightBox icon="sinuosity_low" title="Highly altered">
          <p>
            Rivers and streams altered by artificial channelization to create
            canals and ditches may have a lower variety and quality of in-stream
            habitat due to differences in hydrography, flow, water quality, and
            other factors compared to natural stream channels. Barriers with
            more highly altered upstream networks may contribute less natural
            habitat if removed.
          </p>
        </HighlightBox>

        <HighlightBox icon="sinuosity_high" title="Less altered">
          <p>
            Rivers and streams with lower amounts of artificial channelization
            to create canals and ditches may have a wider variety of
            higher-quality in-stream habitat. Barriers with less altered
            upstream networks may contribute more natural habitat if removed.
          </p>
        </HighlightBox>
      </Grid>

      <Box variant="boxes.section" sx={{ mt: '6rem' }}>
        <Heading as="h2" variant="heading.section">
          Methods:
        </Heading>
        <ol>
          <li>
            Stream and river segments are identified as altered where they are
            specifically coded by NHD as canals or ditches.
          </li>
          <li>The total length of the network is calculated.</li>
          <li>
            The total length of unaltered segments within the network is
            calculated.
          </li>
          <li>percent unaltered = 100 * (unaltered length / total length)</li>
        </ol>
      </Box>
    </Container>
  </Layout>
)

PercentUnalteredPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NetworkPercentUnalteredQuery {
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

export default PercentUnalteredPage
