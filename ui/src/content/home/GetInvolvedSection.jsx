import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import { Box, Divider, Heading, Paragraph, Grid, Text } from 'theme-ui'

import { OutboundLink } from 'components/Link'

const GetInvolvedSection = () => {
  const {
    damRemovalTeamPhoto: {
      childImageSharp: { gatsbyImageData: damRemovalTeamPhoto },
    },
  } = useStaticQuery(graphql`
    query {
      damRemovalTeamPhoto: file(
        relativePath: {
          eq: "Roaring_River_dam_removal_-_All_the_Partners_-_DSC_0178.jpg"
        }
      ) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
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
      <Grid columns={[0, '3fr 5fr']} gap={5}>
        <Box>
          <Heading as="h2" sx={{ fontWeight: 'normal' }}>
            Get involved!
          </Heading>
          <Paragraph sx={{ mt: '1rem' }}>
            You can help improve the inventory by sharing data, assisting with
            field reconnaissance to evaluate the impact of aquatic barriers,
            joining an{' '}
            <OutboundLink to="https://www.americanrivers.org/aquatic-connectivity-groups/">
              Aquatic Connectivity Team
            </OutboundLink>
            , or even by reporting issues with the inventory data in this tool.
            <br />
            <br />
            <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
            more about how you can help improve this barrier inventory and tool.
          </Paragraph>
        </Box>

        <Box>
          <GatsbyImage
            image={damRemovalTeamPhoto}
            alt="Roaring River Dam Removal, Tennessee, 2017. Mark Thurman, Tennessee
            Wildlife Resources Agency."
          />
          <Text variant="help">
            Roaring River Dam Removal, Tennessee, 2017. Mark Thurman, Tennessee
            Wildlife Resources Agency.
          </Text>
        </Box>
      </Grid>
      <Heading as="h2" sx={{ fontWeight: 'normal', mt: '1rem' }}>
        Need Help?
      </Heading>
      <Paragraph sx={{ mt: '1rem' }}>
        If you are not able to get what you need from this tool or if you need
        to report an issue, please&nbsp;
        <a href="mailto:kat@southeastaquatics.net">let us know</a>!
      </Paragraph>
    </Box>
  )
}

export default GetInvolvedSection
