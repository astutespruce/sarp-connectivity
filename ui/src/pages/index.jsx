import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import Layout from 'components/Layout'
import { Container } from 'components/Grid'
import { Link } from 'components/Link'
import { HeaderImage } from 'components/Image'
import Map from 'components/Map'
import styled from 'style'

import { TopSection, InventorySection, ToolSection } from 'content/home'

const IndexPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.fluid}
      height="40vh"
      minHeight="22rem"
      position="center"
      title="Southeast Aquatic Barrier Prioritization Tool"
      subtitle="Improve aquatic connectivity by prioritizing aquatic barriers for removal using the best
      available data."
    />

    <Container>
      <TopSection />
      <InventorySection />
      <ToolSection />
    </Container>
  </Layout>
)

IndexPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query HomePageQuery {
    headerImage: file(relativePath: { eq: "iStock-181890680.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
  }
`

export default IndexPage
