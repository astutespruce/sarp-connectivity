import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'

import { Layout } from 'components/Layout'
import { HeaderImage } from 'components/Image'

const IndexPage = () => {
  const {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  } = useStaticQuery(
    graphql`
      query {
        headerImage: file(
          relativePath: { eq: "25898720604_f380ee9709_k.jpg" }
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
  )
  return (
    <Layout title="NOT FOUND">
      <HeaderImage
        image={headerImage}
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
}

export default IndexPage
