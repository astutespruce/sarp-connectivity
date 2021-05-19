import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { FaSearchLocation } from 'react-icons/fa'

import { Text, HelpText } from 'components/Text'
import { PrimaryButton } from 'components/Button'
import { Flex, Box } from 'components/Grid'
import { Link } from 'components/Link'
import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import {
  PageTitle as BasePageTitle,
  PageContainer,
  Title,
  StepHeader as BaseStepHeader,
  StepNumber,
  Divider,
} from 'content/styles'
import styled from 'style'

const PageTitle = styled(BasePageTitle)`
  margin-bottom: 0.5rem;
`

const Subtitle = styled(Title)`
  font-weight: normal;
  margin-bottom: 1rem;
`

const StepHeader = styled(BaseStepHeader)`
  margin-bottom: 0;
`

const StepTitle = styled(Text)`
  font-weight: bold;
`

const Step = styled(Box).attrs({ mb: '2rem' })``

const StepDescription = styled(HelpText)`
  font-size: 1.25rem;
  margin-left: 3.5rem;
`

const ButtonContainer = styled(Flex).attrs({
  justifyContent: 'space-between',
})`
  margin-bottom: 8rem;
`

const Button = styled(PrimaryButton)`
  font-size: 1.5rem;
`

const SearchIcon = styled(FaSearchLocation)`
  height: 0.8em;
  width: 1em;
  margin-right: 0.25em;
`

const PrioritizePage = ({ data: { headerImage } }) => (
  <Layout title="Prioritize">
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="20vh"
      minHeight="18rem"
      credits={{
        author: 'American Public Power Association',
        url: 'https://unsplash.com/photos/FUeb2npsblQ',
      }}
    />

    <PageContainer>
      <PageTitle>Prioritize barriers for removal</PageTitle>

      <Subtitle>
        To prioritize barriers, you will work through the following steps:
      </Subtitle>

      <Step>
        <StepHeader>
          <StepNumber>
            <div>1</div>
          </StepNumber>
          <StepTitle>Select area of interest.</StepTitle>
        </StepHeader>
        <StepDescription>
          You can select areas using state, county, watershed, and ecoregion
          boundaries.
        </StepDescription>
      </Step>

      <Step>
        <StepHeader>
          <StepNumber>
            <div>2</div>
          </StepNumber>
          <StepTitle>Filter barriers.</StepTitle>
        </StepHeader>
        <StepDescription>
          You can filter barriers by feasibility, height, and other key
          characteristics to select those that best meet your needs.
        </StepDescription>
      </Step>

      <Step>
        <StepHeader>
          <StepNumber>
            <div>3</div>
          </StepNumber>
          <StepTitle>Explore priorities on the map.</StepTitle>
        </StepHeader>
        <StepDescription>
          Once you have defined your area of interest and selected the barriers
          you want, you can explore them on the map.
        </StepDescription>
      </Step>

      <Step>
        <StepHeader>
          <StepNumber>
            <div>4</div>
          </StepNumber>
          <StepTitle>Download prioritized barriers.</StepTitle>
        </StepHeader>
        <StepDescription>
          You can download the inventory for your area of interest and perform
          offline work.
        </StepDescription>
      </Step>

      <Divider />

      <Title>Get started now</Title>

      <ButtonContainer>
        <Link to="/priority/dams">
          <Button>
            <SearchIcon />
            Prioritize dams
          </Button>
        </Link>

        <Link to="/priority/barriers">
          <Button>
            <SearchIcon />
            Prioritize road-related barriers
          </Button>
        </Link>
      </ButtonContainer>
    </PageContainer>
  </Layout>
)

PrioritizePage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query PrioritizeStartPageQuery {
    headerImage: file(
      relativePath: {
        eq: "american-public-power-association-430861-unsplash.jpg"
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

export default PrioritizePage
