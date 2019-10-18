import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Image } from 'rebass'

import { Box, Flex } from 'components/Grid'
import { OutboundLink } from 'components/Link'
import { HelpText } from 'components/Text'
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
        <LargeText>By using this tool, you agree to the following:</LargeText>

        <ul>
          <li>
            you will credit the Southeast Aquatic Resources Partnership (SARP)
            in anything produced using the data provided in this dataset
            including, including, but not limited to, peer-reviewed publications
            via acknowledgments, presentations and reports via logo placement,
            and newsletter or interview articles via logo and/or verbal credit.{' '}
          </li>
        </ul>

        <Flex>
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
