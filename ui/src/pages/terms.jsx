import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { PageTitle, PageContainer, LargeText } from 'content/styles'

const TermsPage = ({ data: { headerImage } }) => {
  return (
    <Layout title="Terms of Use">
      <HeaderImage
        image={headerImage.childImageSharp.fluid}
        height="20vh"
        minHeight="18rem"
        position="center"
        credits={{
          author: 'David Kovalenko.',
          url: 'https://unsplash.com/photos/qYMa2-P-U0M',
        }}
      />

      <PageContainer>
        <PageTitle>Terms of Use</PageTitle>
        <LargeText>By using this tool, you agree to the following:</LargeText>

        <ul>
          <li>TODO:</li>
        </ul>
      </PageContainer>
    </Layout>
  )
}

TermsPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query TermsOfUseImageQuery {
    headerImage: file(
      relativePath: { eq: "david-kovalenko-447548-unsplash.jpg" }
    ) {
      childImageSharp {
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
  }
`

export default TermsPage
