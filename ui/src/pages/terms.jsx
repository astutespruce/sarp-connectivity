import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Image } from 'rebass/styled-components'

import { Box, Flex } from 'components/Grid'
import { OutboundLink } from 'components/Link'
import { HelpText, Text } from 'components/Text'
import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { PageTitle, PageContainer, LargeText } from 'content/styles'
import SARPLogoImage from 'images/sarp_logo.png'

import styled from 'style'

const SARPLogo = styled(Image).attrs({ src: SARPLogoImage })`
  width: 32rem;
  flex: 0 0 auto;
`

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

        <Text as="p">
          The data made available through this tool represent substantial effort
          and investment from the{' '}
          <OutboundLink to="https://southeastaquatics.net/">
            Southeast Aquatic Resources Partnership
          </OutboundLink>{' '}
          (SARP) and SARP&apos;s funders, partners, and data contributors.
          <br />
          <br />
          This project was supported in part by grants from the&nbsp;
          <OutboundLink to="https://www.fws.gov/fisheries/fish-passage.html">
            U.S. Fish and Wildlife Service Fish Passage Program
          </OutboundLink>
          , the&nbsp;
          <OutboundLink to="https://gcpolcc.org/">
            Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
          </OutboundLink>
          , and the&nbsp;
          <OutboundLink to="https://myfwc.com/conservation/special-initiatives/fwli/grant/">
            Florida State Wildlife Grants Program
          </OutboundLink>
          .
          <br />
          <br />
        </Text>

        <LargeText>By using this tool, you agree to the following:</LargeText>

        <ol>
          <li>
            you will credit SARP in anything produced using the data provided by
            this tool including, but not limited to, peer-reviewed publications
            via acknowledgments, presentations and reports via logo placement,
            and newsletter or interview articles via logo and/or verbal credit.
          </li>
        </ol>

        <LargeText>In order to download data:</LargeText>
        <ol>
          <li>
            you will provide your name, email address, and other information to
            SARP.
          </li>
          <li>
            you agree to be contacted by SARP staff if a data issue is
            discovered in the data made available through this tool. However,
            SARP staff are not obligated to notify you of any data issues.
          </li>
          <li>
            you agree to be contacted by SARP staff for information about how
            you are using these data, in order to help SARP staff report
            statistics to SARP&apos;s funders and partners, who have helped make
            these data available to you.
          </li>
          <li>
            you agree to be contacted by SARP staff upon data updates to ensure
            you are working with the most accurate data available. However, SARP
            staff are not obligated to notify you of data updates.
          </li>
        </ol>

        <Flex mt="4rem">
          <Box mr="2rem">
            <OutboundLink to={SARPLogoImage}>
              <SARPLogo />
            </OutboundLink>
          </Box>

          <HelpText>
            A high resolution copy of the SARP logo can be requested from
            Jessica Graham via email at{' '}
            <OutboundLink to="jessica@southeastaquatics.net">
              jessica@southeastaquatics.net
            </OutboundLink>
            . A small version can be obtained by clicking on the logo to the
            left open it in a new window.
          </HelpText>
        </Flex>
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
