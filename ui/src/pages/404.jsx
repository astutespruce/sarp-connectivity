import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'

import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { hasWindow } from 'util/dom'

const IndexPage = () => {
  const {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  } = useStaticQuery(graphql`
    query {
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
  `)

  if (!hasWindow) {
    // prevents initial load of this page for client-only pages that are still loading
    return null
  }

  return (
    <Layout>
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

export const Head = () => <SEO title="NOT FOUND" />
