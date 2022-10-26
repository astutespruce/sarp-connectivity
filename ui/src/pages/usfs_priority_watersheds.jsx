import React from 'react'
import PropTypes from 'prop-types'
import { graphql, withPrefix } from 'gatsby'
import { Container, Paragraph, Heading } from 'theme-ui'

import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'

const LengthPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="30vh"
      minHeight="18rem"
      credits={{
        author: 'U.S. Forest Service Southern Region',
        url: 'https://www.flickr.com/photos/forest_service_southern_region/16244961613/',
      }}
    />

    <Container>
      <Heading as="h1">
        U.S. Forest Service Southern Region Priority Watersheds for Aquatic
        Conservation
      </Heading>
      <Paragraph sx={{ mt: '2rem' }}>
        In order to better prioritize aquatic conservation on National Forests
        in the southern U.S., in 2010 the Forest Service developed a framework
        for identifying priority watersheds based on:
      </Paragraph>
      <ul>
        <li>
          TNC critical watersheds (critical watersheds for conservation of
          imperiled fish and mussels)
        </li>
        <li>
          TNC Hotspots (subbasins that contain 10 or more at-risk freshwater and
          mussel species)
        </li>
        <li>
          Watersheds with U.S. Fish and Wildlife Service Critical Habitat
          designations
        </li>
        <li>
          Southeast Aquatic Resources Partnership (SARP) priority watersheds
          (watersheds identified by SARP as key in preserving biodiversity in
          the southern U.S.)
        </li>
        <li>Watersheds containing aquatic passage inventories</li>
        <li>
          EPA priority watersheds (watersheds where the EPA and state partners
          agreed to focus to protect and restore waters)
        </li>
      </ul>
      <Paragraph sx={{ mt: '2rem' }}>
        These watersheds were identified at the subbasin (HUC8) level.
        <br />
        <br />
        <a
          href={withPrefix('USFS_R8_priority_watersheds_2010.pdf')}
          download="USFS_R8_priority_watersheds_2010.pdf"
        >
          Download report.
        </a>
      </Paragraph>
    </Container>
  </Layout>
)

LengthPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query USFSPriorityPageQuery {
    headerImage: file(relativePath: { eq: "16244961613_6db5ed78f1_o.jpg" }) {
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
  <SEO title="U.S. Forest Service Southern Region Priority Watersheds for Aquatic Conservation" />
)
