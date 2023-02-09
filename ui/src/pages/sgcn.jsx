import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Heading, Paragraph } from 'theme-ui'

import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { OutboundLink } from 'components/Link'

const LengthPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="30vh"
      minHeight="18rem"
      credits={{
        author:
          'Appalachian elktoe | U.S. Fish & Wildlife Service Southeast Region',
        url: 'https://www.flickr.com/photos/usfwssoutheast/33643109826/',
      }}
    />

    <Container>
      <Heading as="h1">
        Listed Species and Species of Greatest Conservation Need
      </Heading>
      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        The presence of federally-listed threatened and endangered aquatic
        species and state and regionally-listed aquatic Species of Greatest
        Conservation Need (SGCN) is an important factor in evaluating the
        priority of a given barrier for removal or mitigation.
        <br />
        <br />
        We compiled information on the location of these species using element
        occurrence data obtained from state natural heritage programs or similar
        organizations. These data were limited to aquatic species, specifically
        fishes, crayfishes, mussels, snails, and amphibians.
      </Paragraph>

      <Box sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Methods
        </Heading>
        <Paragraph>
          We summarized species data to the subwatershed level based on:
        </Paragraph>
        <ol>
          <li>
            Presence of federally-listed species using data managed by the state
            programs or species lists from the U.S. Fish and Wildlife Service.
          </li>
          <li>
            Presence of state-listed Species of Greatest Conservation Need using
            species lists from{' '}
            <OutboundLink to="https://www1.usgs.gov/csas/swap/">
              State Wildlife Action Plan species lists
            </OutboundLink>{' '}
            compiled by the U.S. Geological Survey.
          </li>
          <li>
            Presence of regionally-listed Species of Greatest Conservation Need
            using a species list from the Southeast Association of Fish and
            Wildlife Agencies.
          </li>
          <li>
            Presence of trout species using a combination of data provided from
            natural heritage programs and NatureServe, as well as data from the
            Eastern Brook Trout Joint Venture (
            <OutboundLink to="https://easternbrooktrout.org/about/reports/ebtjv-salmonid-catchment-assessment-and-habitat-patch-layers">
              EBTJV Habitat Patch Dataset
            </OutboundLink>
            , brook trout only).
          </li>
          <li>
            Overlap with salmon and steelhead Evolutionarily Significant Units /
            Discrete Population Segment data provided by the National Oceanic
            and Atmospheric Administration (NOAA){' '}
            <OutboundLink to="https://www.fisheries.noaa.gov/about/northwest-fisheries-science-center">
              Northwest Fisheries Science Center
            </OutboundLink>
            .
          </li>
        </ol>
      </Box>

      <Box sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Caveats:
        </Heading>
        <ul>
          <li>
            The presence of one or more of these species in the same
            subwatershed as a barrier does not necessarily mean that the species
            is directly impacted by that barrier. Likewise, it does not
            necessarily imply that the species will directly benefit by removal
            or mitigation of the barrier.
          </li>
          <li>
            Information on these species is limited and comprehensive
            information has not been provided for all states at this time.
          </li>
          <li>
            Due to variations in taxonomic representation of a given species or
            subspecies, not all species are necessarily correctly categorized
            according to the above breakdown.
          </li>
        </ul>
      </Box>
    </Container>
  </Layout>
)

LengthPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query SGCNPageQuery {
    headerImage: file(relativePath: { eq: "33643109826_51296358b0_k.jpg" }) {
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

export default LengthPage

export const Head = () => (
  <SEO title="Listed Species and Species of Greatest Conservation Need" />
)
