import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Link, OutboundLink } from 'components/Link'
import {
  PageTitle,
  PageContainer,
  Section,
  Title,
  Column,
  LargeText,
} from 'content/styles'

const LengthPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.fluid}
      height="30vh"
      minHeight="18rem"
      position="center"
      credits={{
        author: 'Puerto Rico dam | Nicholas Dutton, U.S. Air Force',
        url:
          'https://www.flickr.com/photos/133046603@N02/37390837391/in/album-72157686668751310/',
      }}
    />

    <PageContainer>
      <PageTitle>Network Analysis - Puerto Rico</PageTitle>
      <LargeText>
        Unlike states in the southeastern U.S., the{' '}
        <OutboundLink to="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/national-hydrography-dataset?qt-science_support_page_related_con=0#qt-science_support_page_related_con">
          Medium Resolution National Hydrography Dataset
        </OutboundLink>{' '}
        (NHD) from the U.S. Geological Survey is the best available hydrography
        data in Puerto Rico. These data are defined at a 1:100,000 scale.
      </LargeText>
      <Section>
        <Title>Methods</Title>
        <ol>
          <li>
            All coastline and "loop" segments were first removed from the NHD
            flowlines dataset in order to create a dendritic aquatic network for
            analysis.
          </li>
          <li>Barriers were snapped to this network.</li>
          <li>
            The Barrier Assessment Tool created by The Nature Conservancy was
            used to determine the upstream functional networks for these
            barriers.
          </li>
          <li>
            Metrics for <Link to="/metrics/length">network length</Link>,{' '}
            <Link to="/metrics/complexity">network complexity</Link>,{' '}
            <Link to="/metrics/sinuosity">sinuosity</Link>, and{' '}
            <Link to="/metrics/landcover">natural landcover</Link> were
            calculated based on these functional networks.
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
  query NetworkMethodsPRPageQuery {
    headerImage: file(relativePath: { eq: "37390837391_95a70430ab_k.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
  }
`

export default LengthPage
