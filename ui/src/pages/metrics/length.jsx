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

const LengthPage = ({ data: { headerImage } }) => (
  <Layout title="Network Length">
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author:
          'Little Tennessee River, North Carolina. U.S. Fish and Wildlife Service.',
        url: 'https://www.flickr.com/photos/usfwssoutheast/5149475130/in/gallery-141606341@N03-72157697846677391/',
      }}
    />

    <PageContainer>
      <PageTitle>Network length</PageTitle>
      <LargeText>
        Network length measures the amount of connected aquatic network length
        that would be added to the network by removing the barrier. It is the
        smaller of either the total upstream network length or total downstream
        network length for the networks subdivided by this barrier. This is
        because a barrier may have a very large upstream network, but if there
        is another barrier immediately downstream, the overall effect of
        removing this barrier will be quite small.
      </LargeText>

      <Section>
        <Columns>
          <Column>
            <HighlightBox icon="length_low" title="Low network length">
              <p>
                Barriers that have small upstream or downstream networks
                contribute relatively little connected aquatic network length if
                removed.
              </p>
            </HighlightBox>
          </Column>

          <Column>
            <HighlightBox icon="length_high" title="High network length">
              <p>
                Barriers that have large upstream and downstream networks will
                contribute a large amount of connected aquatic network length if
                they are removed.
              </p>
            </HighlightBox>
          </Column>
        </Columns>
      </Section>

      <Section>
        <Title>Methods:</Title>
        <ol>
          <li>
            The total upstream length is calculated as the sum of the lengths of
            all upstream river and stream reaches.
          </li>
          <li>
            The total downstream length is calculated for the network
            immediately downstream of the barrier. Note: this is the total
            network length of the downstream network, <i>not</i> the shortest
            downstream path to the next barrier or river mouth.
          </li>
          <li>
            Network length is the smaller of the upstream or downstream network
            lengths.
          </li>
        </ol>
      </Section>
    </PageContainer>
  </Layout>
)

LengthPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NetworkLengthQuery {
    headerImage: file(relativePath: { eq: "5149475130_b2334f1edd_4k.jpg" }) {
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
