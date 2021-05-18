import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import Layout from 'components/Layout'
import { Container } from 'components/Grid'
import { HeaderImage, DividerImage } from 'components/Image'
import styled from 'style'

import {
  TopSection,
  InventorySection,
  ToolSection,
  ScoringSection,
  UseCasesSection,
  SARPSection,
  CreditsSection,
} from 'content/home'

const Content = styled(Container).attrs({
  px: ['1rem', '1rem', 0],
})``

const IndexPage = ({ data: { headerImage, dividerImage1, dividerImage2 } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="40vh"
      minHeight="22rem"
      position="center"
      title="Southeast Aquatic Barrier Prioritization Tool"
      subtitle="Improve aquatic connectivity by prioritizing aquatic barriers for removal using the best
      available data."
    />

    <Content>
      <TopSection />
      <InventorySection />
      <ToolSection />
      <ScoringSection />
    </Content>

    <DividerImage
      image={dividerImage1.childImageSharp.gatsbyImageData}
      height="75vh"
      minHeight="26rem"
      credits={{
        author:
          'Steeles Mill Dam Hitchcock Creek during removal. Peter Raabe, American Rivers.',
      }}
    />

    <Content>
      <UseCasesSection />
    </Content>

    <DividerImage
      image={dividerImage2.childImageSharp.gatsbyImageData}
      height="50vh"
      minHeight="26rem"
      credits={{
        author:
          'Roaring River Dam Removal, Tennessee, 2017. Mark Thurman, Tennessee Wildlife Resources Agency.',
      }}
    />

    <Content>
      <SARPSection />
      <CreditsSection />
    </Content>
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
    dividerImage1: file(
      relativePath: {
        eq: "Steeles_Mill_Dam_Hitchcock_Creek_during_removal__Peter_Raabe_A.jpg"
      }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    dividerImage2: file(
      relativePath: {
        eq: "Roaring_River_dam_removal_-_All_the_Partners_-_DSC_0178.jpg"
      }
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

export default IndexPage
