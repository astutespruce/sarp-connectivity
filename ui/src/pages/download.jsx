import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Grid, Heading, Paragraph, Text } from 'theme-ui'

import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Link, OutboundLink } from 'components/Link'
import { StateDownloadTable } from 'components/Download'
import { useSummaryData } from 'components/Data'
import { siteMetadata } from 'constants'

const { version: dataVersion, date: dataDate } = siteMetadata

const DownloadPage = ({ data: { headerImage } }) => {
  const { total } = useSummaryData()

  return (
    <Layout>
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

        <Grid columns={[0, '2.5fr 1fr']} gap={4} sx={{ mt: '2rem' }}>
          <Box>
            <Paragraph>
              To select a different area for download or perform a custom
              prioritization, use the <Link to="/priority">Prioritize</Link>{' '}
              page.
              <br />
              <br />
              The following download options include the latest available data
              within this tool. These data are subject to change at any point
              due to improvements to the inventory of aquatic barriers or
              improvements to the network connectivity analyses used by this
              tool. Dams include priorities evaluated at the state level.
              <br />
              <br />
              The inventory consists of datasets from local, state, and federal
              partners. It is supplemented with input from partners with on the
              ground knowledge of specific structures. The information on
              barriers is not complete or comprehensive and depends on the
              availability and completeness of existing data and level of
              partner feedback. Some areas are more complete than others but
              none should be considered 100% complete.
            </Paragraph>
          </Box>
          <Box sx={{ p: '1rem', bg: 'blue.1', borderRadius: '0.5rem' }}>
            <Paragraph>
              <b>
                Data Version: {dataVersion} ({dataDate})
              </b>
            </Paragraph>
            <Text
              sx={{
                mt: '1rem',
                pt: '1rem',
                borderTop: '4px solid #FFF',
              }}
            >
              Please{' '}
              <OutboundLink to="https://southeastaquatics.net/about/contact-us">
                Contact Us
              </OutboundLink>{' '}
              if you discover any issues with these data, need assistance
              interpreting or applying these data, or would like to contribute
              data.
              <br />
              <br />
              Please review the <Link to="/terms">Terms of Use</Link> before
              downloading data.
            </Text>
          </Box>
        </Grid>

        <StateDownloadTable region="total" {...total} sx={{ mt: '4rem' }} />
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

export const Head = () => <SEO title="Download Aquatic Barrier Data" />
