import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Columns } from 'components/Grid'
import HighlightBox from 'components/Layout/HighlightBox'
import {
  PageTitle,
  PageContainer,
  Section,
  Title,
  Column,
  LargeText,
} from 'content/styles'

const ComplexityPage = ({ data: { headerImage } }) => (
  <Layout>
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
      <PageTitle>Network complexity</PageTitle>
      <LargeText>
        A barrier that has upstream tributaries of different size classes, such
        as small streams, small rivers, and large rivers, would contribute a
        more complex connected aquatic network if it was removed. In contrast, a
        barrier with fewer upstream tributaries may contribute few if any size
        classes to the network if removed. In general, a more complex network
        composed of a greater range of size classes is more likely to have a
        wide range of available habitat for a greater number of aquatic species.
      </LargeText>

      <Section>
        <Columns>
          <Column>
            <HighlightBox
              icon="size_classes_low"
              title="No size classes gained"
            >
              <p>
                Barriers that do not contribute any additional size classes are
                less likely to contribute a wide range of aquatic habitat.
              </p>
            </HighlightBox>
          </Column>

          <Column>
            <HighlightBox
              icon="size_classes_high"
              title="Several size classes gained"
            >
              <p>
                Barriers that have several size classes upstream are more likely
                to contribute a more complex network with a greater range of
                aquatic habitat for a greater variety of species.
              </p>
            </HighlightBox>
          </Column>
        </Columns>
      </Section>

      <Section>
        <Title>Methods:</Title>
        <ol>
          <li>
            Stream and river reaches were assigned to size classes based on
            total drainage area:
            <ul>
              <li>
                Headwaters: &lt; 10 km
                <sup>2</sup>
              </li>
              <li>
                Creeks: &ge; 10 km
                <sup>2</sup> and &lt; 100 km
                <sup>2</sup>
              </li>
              <li>
                Small rivers: &ge; 100 km
                <sup>2</sup> and &lt; 518 km
                <sup>2</sup>
              </li>
              <li>
                Medium tributary rivers: &ge; 519 km
                <sup>2</sup> and &lt; 2,590 km
                <sup>2</sup>
              </li>
              <li>
                Medium mainstem rivers: &ge; 2,590 km
                <sup>2</sup> and &lt; 10,000 km
                <sup>2</sup>
              </li>
              <li>
                Large rivers: &ge; 10,000 km
                <sup>2</sup> and &lt; 25,000 km
                <sup>2</sup>
              </li>
              <li>
                Great rivers: &ge; 25,000 km
                <sup>2</sup>
              </li>
            </ul>
          </li>
          <li>
            Each barrier is assigned the total number of unique size classes in
            its upstream functional network.
          </li>
        </ol>
      </Section>
    </PageContainer>
  </Layout>
)

ComplexityPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NetworkComplexityQuery {
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

export default ComplexityPage
