import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Container } from 'theme-ui'

import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'

import {
  TopSection,
  InventorySection,
  RegionSection,
  ToolSection,
  GetInvolvedSection,
  CreditsSection,
} from 'content/home'

const IndexPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="28vh"
      minHeight="18rem"
      title="Aquatic Barrier Prioritization Tool"
      subtitle="Improve aquatic connectivity by prioritizing aquatic barriers for removal using the best
      available data."
    />

    <Container sx={{ mt: 0 }}>
      <TopSection />
      <InventorySection />
      <RegionSection />
      <ToolSection />

      {/* <DividerImage
      image={dividerImage2.childImageSharp.gatsbyImageData}
      height="50vh"
      minHeight="26rem"
      credits={{
        author:
          'Roaring River Dam Removal, Tennessee, 2017. Mark Thurman, Tennessee Wildlife Resources Agency.',
      }}
    /> */}

      <GetInvolvedSection />
      <CreditsSection />
    </Container>
  </Layout>
)

IndexPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    dividerImage1: PropTypes.object.isRequired,
    dividerImage2: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query HomePageQuery {
    headerImage: file(relativePath: { eq: "iStock-181890680.jpg" }) {
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

export default IndexPage
