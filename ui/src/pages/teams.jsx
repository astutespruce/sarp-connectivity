import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'

import { Text } from 'components/Text'
import Layout from 'components/Layout'
import { OutboundLink } from 'components/Link'
import { HeaderImage } from 'components/Image'
import { extractNodes, GraphQLArrayPropType } from 'util/graphql'
import { groupBy } from 'util/data'
import styled, { themeGet } from 'style'
import { PageTitle, Section, ImageCredits, PageContainer } from 'content/styles'
import { CONNECTIVITY_TEAMS } from '../../config/constants'

const TeamSection = styled(Section)`
  &:not(:first-of-type) {
    padding-top: 3rem;
    border-top: 1px solid ${themeGet('colors.grey.200')};
  }
`

const Subtitle = styled(Text).attrs({
  as: 'h2',
  fontSize: ['1.5rem', '2rem'],
  mb: '1.5rem',
})``

const Image = styled(GatsbyImage).attrs({
  height: ['360px', '540px', '600px'],
  width: '100%',
})`
  margin-top: 1rem;
  margin-bottom: 0.25rem;

  img {
    object-position: top;
  }
`

const Credits = styled(ImageCredits)`
  text-align: right;
`

const teamImageCredits = {
  Arkansas: 'Kat Hoenke, Southeast Aquatic Resources Partnership.',
  Tennessee: 'Jessica Graham, Southeast Aquatic Resources Partnership.',
}

const TeamsPage = ({ data: { headerImage, imagesSharp, footerImage } }) => {
  const images = groupBy(extractNodes(imagesSharp), 'state')

  return (
    <Layout title="Aquatic Connectivity Teams">
      <HeaderImage
        image={headerImage.childImageSharp.gatsbyImageData}
        height="40vh"
        minHeight="22rem"
        credits={{
          author: 'Jessica Graham, Southeast Aquatic Resources Partnership.',
        }}
      />

      <PageContainer>
        <PageTitle>Aquatic Connectivity Teams</PageTitle>

        <div>
          {Object.entries(CONNECTIVITY_TEAMS).map(([state, team]) => (
            <TeamSection key={state}>
              <Subtitle>{state}</Subtitle>
              <p>
                {team.description}
                <br />
                <br />
                {team.url !== undefined ? (
                  <>
                    Please see the{' '}
                    <OutboundLink to={team.url}>
                      {state} Aquatic Connectivity Team website
                    </OutboundLink>
                    .
                    <br />
                    <br />
                  </>
                ) : null}
                For more information, please contact{' '}
                <a href={`mailto:${team.contact.email}`}>
                  {team.contact.name}
                </a>{' '}
                ({team.contact.org}).
              </p>
              {images[state] ? (
                <>
                  <Image
                    image={images[state].childImageSharp.gatsbyImageData}
                  />
                  {teamImageCredits[state] ? (
                    <Credits>Photo: {teamImageCredits[state]}</Credits>
                  ) : null}
                </>
              ) : null}
            </TeamSection>
          ))}
          <TeamSection>
            <p>
              For more information about Aquatic Connectivity Teams, please see
              the{' '}
              <OutboundLink to="https://www.southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap/connectivity-teams">
                SARP Aquatic Connectivity Teams page
              </OutboundLink>
              .<br />
              <br />
            </p>

            <Image image={footerImage.childImageSharp.gatsbyImageData} />
            <Credits>
              Photo: Jessica Graham, Southeast Aquatic Resources Partnership.
            </Credits>
          </TeamSection>
        </div>
      </PageContainer>
    </Layout>
  )
}

TeamsPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    imagesSharp: GraphQLArrayPropType.isRequired,
    footerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query TeamsPageQuery {
    headerImage: file(relativePath: { eq: "TN_ACT2.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    imagesSharp: allFile(filter: { relativeDirectory: { eq: "teams" } }) {
      edges {
        node {
          state: name
          childImageSharp {
            gatsbyImageData(
              layout: FULL_WIDTH
              formats: [AUTO, WEBP]
              placeholder: BLURRED
            )
          }
        }
      }
    }
    footerImage: file(relativePath: { eq: "IMG_1530.jpg" }) {
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

export default TeamsPage
