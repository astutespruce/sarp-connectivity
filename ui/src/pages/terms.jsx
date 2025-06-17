import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Flex, Paragraph, Heading, Image } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import SARPLogoImage from 'images/sarp_logo_highres.png'

const TermsPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author: 'David Kovalenko.',
        url: 'https://unsplash.com/photos/qYMa2-P-U0M',
      }}
    />

    <Container>
      <Heading as="h1">Terms of Use</Heading>

      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        The data made available through this tool represent substantial effort
        and investment from the{' '}
        <OutboundLink to="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
          Southeast Aquatic Resources Partnership
        </OutboundLink>{' '}
        (SARP) and SARP&apos;s funders, partners, and data contributors.
        <br />
        <br />
        This project was supported in part by grants from the{' '}
        <OutboundLink to="https://www.fws.gov/fisheries/fish-passage.html">
          U.S. Fish and Wildlife Service Fish Passage Program
        </OutboundLink>
        ,{' '}
        <OutboundLink to="https://www.americanrivers.org/">
          American Rivers
        </OutboundLink>
        , the{' '}
        <OutboundLink to="https://www.fs.usda.gov/">
          U.S. Department of Agriculture, Forest Service
        </OutboundLink>
        , the{' '}
        <OutboundLink to="https://www.nfwf.org/">
          National Fish and Wildlife Foundation
        </OutboundLink>
        ,{' '}
        <OutboundLink to="https://www.nature.org/">
          The Nature Conservancy
        </OutboundLink>
        , <OutboundLink to="https://www.tu.org/">Trout Unlimited</OutboundLink>,{' '}
        the{' '}
        <OutboundLink to="https://gcpolcc.org/">
          Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
        </OutboundLink>
        , and the{' '}
        <OutboundLink to="https://myfwc.com/conservation/special-initiatives/swap/grant/">
          Florida State Wildlife Grants Program
        </OutboundLink>
        .
      </Paragraph>

      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        By using this tool, you agree to the following:
      </Paragraph>

      <ol>
        <li>
          you will credit SARP in anything produced using the data provided by
          this tool including, but not limited to, peer-reviewed publications
          via acknowledgments, presentations and reports via logo placement, and
          newsletter or interview articles via logo and/or verbal credit.
        </li>
      </ol>

      <Paragraph variant="paragraph.large">
        In order to download data:
      </Paragraph>
      <ol>
        <li>
          you will provide your name, email address, and other information to
          SARP.
        </li>
        <li>
          you agree to be contacted by SARP staff if a data issue is discovered
          in the data made available through this tool. However, SARP staff are
          not obligated to notify you of any data issues.
        </li>
        <li>
          you agree to be contacted by SARP staff for information about how you
          are using these data, in order to help SARP staff report statistics to
          SARP&apos;s funders and partners, who have helped make these data
          available to you.
        </li>
        <li>
          you agree to be contacted by SARP staff upon data updates to ensure
          you are working with the most accurate data available. However, SARP
          staff are not obligated to notify you of data updates.
        </li>
      </ol>

      <Flex sx={{ mt: '4rem', alignItems: 'center' }}>
        <Box sx={{ mr: '2rem' }}>
          <OutboundLink to={SARPLogoImage}>
            <Image
              src={SARPLogoImage}
              sx={{ width: '32rem', flex: '0 0 auto' }}
            />
          </OutboundLink>
        </Box>

        <Paragraph variant="help" sx={{ fontSize: 2 }}>
          A high resolution logo can be obtained by clicking on the logo to the
          left to open it in a new window.
        </Paragraph>
      </Flex>
    </Container>
  </Layout>
)

TermsPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query TermsOfUseImageQuery {
    headerImage: file(
      relativePath: { eq: "david-kovalenko-qYMa2-P-U0M-unsplash.jpg" }
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

export default TermsPage

export const Head = () => <SEO title="Terms of Use" />
