import React from 'react'
import { Box, Divider, Flex, Grid, Heading } from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'
import { useStaticQuery, graphql } from 'gatsby'

import { Link } from 'components/Link'
import { REGIONS } from 'config'

const regions = Object.entries(REGIONS)
  .map(([id, data]) => ({ id, ...data }))
  .sort(({ order: a }, { order: b }) => (a < b ? -1 : 1))

const Regions = () => {
  const maps = useStaticQuery(graphql`
    query {
      ak: file(relativePath: { eq: "maps/ak.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      gl: file(relativePath: { eq: "maps/gl.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      gpiw: file(relativePath: { eq: "maps/gpiw.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }

      ne: file(relativePath: { eq: "maps/ne.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      pnw: file(relativePath: { eq: "maps/pnw.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      psw: file(relativePath: { eq: "maps/psw.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      se: file(relativePath: { eq: "maps/se.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      sw: file(relativePath: { eq: "maps/sw.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: FULL_WIDTH
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
    }
  `)

  return (
    <Box variant="boxes.section">
      <Divider sx={{ mb: '4rem' }} />
      <Heading as="h2" variant="heading.section">
        Explore the inventory by region:
      </Heading>

      <Grid columns={3} gap={4} sx={{ bg: 'grey.0', p: '1rem' }}>
        {regions.map(({ id, name, url, inDevelopment }) => (
          <Link key={id} to={url}>
            <Box
              sx={{
                p: '1rem',
                bg: '#FFF',
                border: '1px solid',
                borderColor: 'grey.1',
                borderRadius: '0.5rem',
                height: '100%',
                '&:hover': {
                  borderColor: 'grey.8',
                  boxShadow: '1px 1px 3px #333',
                },
              }}
            >
              <Flex
                sx={{
                  justifyContent: 'flex-end',
                  flexDirection: 'column',
                  height: '3rem',
                }}
              >
                <Heading
                  as="h4"
                  sx={{
                    flex: '0 0 auto',
                    fontWeight: 'normal',
                    mr: '0.5rem',
                  }}
                >
                  {name}
                </Heading>
                {inDevelopment ? (
                  <Box
                    sx={{
                      flex: '1 1 auto',
                      fontSize: 1,
                      color: 'grey.8',
                    }}
                  >
                    (in development)
                  </Box>
                ) : null}
              </Flex>

              <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
                <GatsbyImage
                  image={maps[id].childImageSharp.gatsbyImageData}
                  alt={`${name} region map`}
                />
              </Box>
            </Box>
          </Link>
        ))}
      </Grid>
    </Box>
  )
}

export default Regions
