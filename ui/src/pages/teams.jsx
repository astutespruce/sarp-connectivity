import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import { Text } from 'components/Text'
import Layout from 'components/Layout'
import { Container } from 'components/Grid'
import { OutboundLink } from 'components/Link'
import { HeaderImage, GatsbyImage } from 'components/Image'
import { extractNodes, GraphQLArrayPropType } from 'util/graphql'
import { groupBy } from 'util/data'
import styled, { themeGet } from 'style'
import { Section, ImageCredits } from 'content/styles'
import { CONNECTIVITY_TEAMS } from '../../config/constants'

const Content = styled(Container).attrs({
  px: ['1rem', '1rem', 0],
  mt: '2rem',
  mb: '4rem',
})``

const Title = styled(Text).attrs({ as: 'h1', fontSize: '3rem' })``


const TeamSection = styled(Section)`
  &:not(:first-child) {
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
text-align: right;`


const teamImageCredits = {
  Arkansas: 'Kat Hoenke, Southeast Aquatic Resources Partnership.',
  Tennessee: 'Jessica Graham, Southeast Aquatic Resources Partnership.',
}

const TeamsPage = ({ data: { headerImage, imagesSharp, footerImage } }) => {
  const images = groupBy(extractNodes(imagesSharp), 'state')

  console.log(images)

  return (
    <Layout>
      <HeaderImage
        image={headerImage.childImageSharp.fluid}
        height="40vh"
        minHeight="22rem"
        position="center"
        credits={{
          author: 'Jessica Graham, Southeast Aquatic Resources Partnership.',
        }}
      />

      <Content>
        <Title>Aquatic Connectivity Teams</Title>

        <div>
          {Object.entries(CONNECTIVITY_TEAMS).map(([state, team], i) => (
            <TeamSection key={state}>
              <Subtitle>{state}</Subtitle>
              <p>
                {team.description}
                <br />
                <br />
                For more information, please contact{' '}
                <a href={`mailto:${team.contact.email}`}>{team.contact.name}</a>
                .
              </p>
              {images[state] ? (
                <>
                  <Image fluid={images[state].childImageSharp.fluid} />
                  {teamImageCredits[state] ? (
                    <Credits>
                      Photo: {teamImageCredits[state]}
                    </Credits>
                  ) : null}
                </>
              ) : null}
            </TeamSection>
          ))}
          <Section>
            <p>
              For more information about Aquatic Connectivity Teams, please see
              the{' '}
              <OutboundLink to="https://www.southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap/connectivity-teams">
                SARP Aquatic Connectivity Teams page
              </OutboundLink>
              .<br />
              <br />
            </p>

            <Image fluid={footerImage.childImageSharp.fluid} />
            <Credits>
            Jessica Graham, Southeast Aquatic Resources Partnership.
            </Credits>
          </Section>
        </div>
      </Content>
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
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
    imagesSharp: allFile(filter: { relativeDirectory: { eq: "teams" } }) {
      edges {
        node {
          state: name
          childImageSharp {
            fluid(maxWidth: 3200) {
              src
            }
          }
        }
      }
    }
    footerImage: file(relativePath: { eq: "IMG_1530.jpg" }) {
        childImageSharp {
          fluid(maxWidth: 960) {
            ...GatsbyImageSharpFluid_withWebp
          }
        }
      }
  }
`

export default TeamsPage
