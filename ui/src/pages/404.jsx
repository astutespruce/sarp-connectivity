import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'

const IndexPage = ({ data: { headerImage } }) => (
  <Layout title="NOT FOUND">
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="100%"
      minHeight="22rem"
      title="PAGE NOT FOUND"
      subtitle="However, we hope that by restoring aquatic connectivity, aquatic organisms will continue to be FOUND."
      credits={{
        author: 'U.S. Fish & Wildlife Service Southeast Region',
        url: 'https://www.flickr.com/photos/usfwssoutheast/25898720604/',
      }}
    />
  </Layout>
)

IndexPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NotFoundPageQuery {
    headerImage: file(relativePath: { eq: "25898720604_f380ee9709_k.jpg" }) {
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
