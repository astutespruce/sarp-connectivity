import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import { HelpText } from 'components/Text'
import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Link, OutboundLink } from 'components/Link'
import { Downloader } from 'components/Download'
import { useStateSummary } from 'components/Data'
import {
  PageTitle,
  PageContainer,
  Section as BaseSection,
  Title,
  LargeText,
} from 'content/styles'
import styled from 'style'
import { formatNumber } from 'util/format'
import { siteMetadata } from '../../gatsby-config'

const { version: dataVersion, date: dataDate } = siteMetadata

const Section = styled(BaseSection)`
  &:not(:first-of-type) {
    margin-top: 3rem;
  }
`

const DownloadPage = ({ data: { headerImage } }) => {
  const baseConfig = { scenario: 'NCWC', layer: 'State' }

  const states = useStateSummary()

  return (
    <Layout title="Download Aquatic Barrier Data">
      <HeaderImage
        image={headerImage.childImageSharp.gatsbyImageData}
        height="30vh"
        minHeight="18rem"
        position="center"
        credits={{
          author: 'Mike Lewis (HeadSmart Media)',
          url: 'https://unsplash.com/photos/waAAaeC9hns',
        }}
      />

      <PageContainer>
        <PageTitle>Download Aquatic Barrier Data</PageTitle>
        <LargeText>
          <b>
            Data Version: {dataVersion} ({dataDate})
          </b>
          <br />
          <br />
          The following download options include the latest available data
          within this tool. These data are subject to change at any point due to
          improvements to the inventory of aquatic barriers or improvements to
          the network connectivity analyses used by this tool. These data
          include priorities evaluated at the regional and state levels.
          <br />
          <br />
          To select a different area for download or perform a custom
          prioritization, use the <Link to="/priority">Prioritize</Link> page.
          <br />
          <br />
          Please review the <Link to="/terms">Terms of Use</Link> before
          downloading data.
          <br />
          <br />
          Please{' '}
          <OutboundLink to="https://southeastaquatics.net/about/contact-us">
            Contact Us
          </OutboundLink>{' '}
          if you discover any issues with these data, need assistance
          interpreting or applying these data, or would like to contribute data.
        </LargeText>
        <HelpText>
          Please note: this inventory consists of datasets from local, state,
          and federal partners. It is supplemented with input from partners with
          on the ground knowledge of specific structures. The information on
          barriers is not complete or comprehensive across the region, and
          depends on the availability and completeness of existing data and
          level of partner feedback. Some areas of the region are more complete
          than others but none should be considered 100% complete.
        </HelpText>

        <Section>
          <Title>Download Dams by State</Title>
          <ul>
            {states.map(({ id, dams }) => (
              <li key={`dams_${id}`}>
                <Downloader
                  label={`${id} (${formatNumber(dams, 0)} dams)`}
                  asButton={false}
                  barrierType="dams"
                  config={{ ...baseConfig, summaryUnits: [{ id }] }}
                />
              </li>
            ))}
          </ul>
          <br />
          <Downloader
            label="Download all states"
            barrierType="dams"
            config={{
              ...baseConfig,
              summaryUnits: states.map(({ id }) => ({
                id,
              })),
            }}
          />
        </Section>

        <Section>
          <Title>Download Road-related Barriers by State</Title>
          <ul>
            {states.map(({ id, total_barriers }) => (
              <li key={`barriers_${id}`}>
                <Downloader
                  label={`${id} (${formatNumber(total_barriers, 0)} barriers)`}
                  asButton={false}
                  barrierType="barriers"
                  config={{ ...baseConfig, summaryUnits: [{ id }] }}
                />
              </li>
            ))}
          </ul>
          <br />
          <Downloader
            label="Download all states"
            barrierType="barriers"
            config={{
              ...baseConfig,
              summaryUnits: states.map(({ id }) => ({
                id,
              })),
            }}
          />
        </Section>
      </PageContainer>
    </Layout>
  )
}

DownloadPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query DownloadPageQuery {
    headerImage: file(
      relativePath: {
        eq: "mike-lewis-headsmart-media-waAAaeC9hns-unsplash.jpg"
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

export default DownloadPage
