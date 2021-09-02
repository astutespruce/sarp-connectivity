import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Heading, Paragraph } from 'theme-ui'

import { Layout } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Link, OutboundLink } from 'components/Link'
import { Downloader } from 'components/Download'
import { useStateSummary } from 'components/Data'

import { formatNumber } from 'util/format'
import { siteMetadata } from '../../gatsby-config'

const { version: dataVersion, date: dataDate } = siteMetadata

const DownloadPage = ({ data: { headerImage } }) => {
  const baseConfig = { scenario: 'NCWC', layer: 'State' }

  const states = useStateSummary()

  return (
    <Layout title="Download Aquatic Barrier Data">
      <HeaderImage
        image={headerImage.childImageSharp.gatsbyImageData}
        height="30vh"
        minHeight="18rem"
        credits={{
          author: 'Mike Lewis (HeadSmart Media)',
          url: 'https://unsplash.com/photos/waAAaeC9hns',
        }}
      />

      <Container>
        <Heading as="h1">Download Aquatic Barrier Data</Heading>
        <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
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
        </Paragraph>
        <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 2 }}>
          Please note: this inventory consists of datasets from local, state,
          and federal partners. It is supplemented with input from partners with
          on the ground knowledge of specific structures. The information on
          barriers is not complete or comprehensive across the region, and
          depends on the availability and completeness of existing data and
          level of partner feedback. Some areas of the region are more complete
          than others but none should be considered 100% complete.
        </Paragraph>

        <Box variant="boxes.section" sx={{ mt: '4rem' }}>
          <Heading as="h2" variant="heading.section">
            Download Dams by State
          </Heading>
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
        </Box>

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Download Road-related Barriers by State
          </Heading>
          <ul>
            {states.map(({ id, total_small_barriers }) => (
              <li key={`barriers_${id}`}>
                <Downloader
                  label={`${id} (${formatNumber(
                    total_small_barriers,
                    0
                  )} barriers)`}
                  asButton={false}
                  barrierType="small_barriers"
                  config={{ ...baseConfig, summaryUnits: [{ id }] }}
                />
              </li>
            ))}
          </ul>
          <br />
          <Downloader
            label="Download all states"
            barrierType="small_barriers"
            config={{
              ...baseConfig,
              summaryUnits: states.map(({ id }) => ({
                id,
              })),
            }}
          />
        </Box>
      </Container>
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
