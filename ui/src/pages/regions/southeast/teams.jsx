import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import { Box, Container, Heading, Paragraph } from 'theme-ui'

import { Layout, SEO } from 'components/Layout'
import { OutboundLink } from 'components/Link'
import { HeaderImage } from 'components/Image'
import { CONNECTIVITY_TEAMS } from 'config'
import { extractNodes, GraphQLArrayPropType } from 'util/graphql'
import { groupBy } from 'util/data'

const teamImageCredits = {
  Arkansas: 'Kat Hoenke, Southeast Aquatic Resources Partnership.',
  Tennessee: 'Jessica Graham, Southeast Aquatic Resources Partnership.',
}

const TeamsPage = ({ data: { headerImage, imagesSharp, footerImage } }) => {
  const images = groupBy(extractNodes(imagesSharp), 'state')

  return (
    <Layout>
      <HeaderImage
        image={headerImage.childImageSharp.gatsbyImageData}
        height="40vh"
        minHeight="22rem"
        credits={{
          author: 'Jessica Graham, Southeast Aquatic Resources Partnership.',
        }}
      />

      <Container>
        <Heading as="h1">Aquatic Connectivity Teams</Heading>

        <Box sx={{ mt: '2rem' }}>
          {Object.entries(CONNECTIVITY_TEAMS.southeast).map(([state, team]) => (
            <Box
              key={state}
              sx={{
                '&:not(:first-of-type)': {
                  mt: '6rem',
                  pt: '3rem',
                  borderTop: '1px solid',
                  borderTopColor: 'grey.2',
                },
              }}
            >
              <Heading
                as="h2"
                sx={{ fontSize: ['1.5rem', '2rem'], mb: '1.5rem' }}
              >
                {state}
              </Heading>
              <Paragraph>
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
              </Paragraph>
              {images[state] ? (
                <>
                  <Box
                    sx={{
                      overflow: 'hidden',
                      height: ['360px', '540px', '600px'],
                      mt: '1rem',
                      mb: '0.25rem',
                      img: {
                        objectPosition: 'center',
                      },
                    }}
                  >
                    <GatsbyImage
                      image={images[state].childImageSharp.gatsbyImageData}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </Box>
                  {teamImageCredits[state] ? (
                    <Box
                      sx={{ textAlign: 'right', color: 'grey.7', fontSize: 0 }}
                    >
                      Photo: {teamImageCredits[state]}
                    </Box>
                  ) : null}
                </>
              ) : null}
            </Box>
          ))}
          <Box
            sx={{
              mt: '6rem',
              pt: '3rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.2',
            }}
          >
            <Paragraph>
              For more information about Aquatic Connectivity Teams, please see
              the{' '}
              <OutboundLink to="https://www.southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap/connectivity-teams">
                SARP Aquatic Connectivity Teams page
              </OutboundLink>
              .<br />
              <br />
            </Paragraph>

            <Box
              sx={{
                height: ['360px', '540px', '600px'],
                mt: '1rem',
                mb: '0.25rem',
                img: {
                  objectPosition: 'top',
                },
              }}
            >
              <GatsbyImage
                image={footerImage.childImageSharp.gatsbyImageData}
              />
            </Box>
            <Box sx={{ textAlign: 'right', color: 'grey.7', fontSize: 0 }}>
              Photo: Jessica Graham, Southeast Aquatic Resources Partnership.
            </Box>
          </Box>
        </Box>
      </Container>
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

export const Head = () => <SEO title="Southeast Aquatic Connectivity Teams" />
