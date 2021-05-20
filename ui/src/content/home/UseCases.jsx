import React from 'react'
import { useStaticQuery, graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import { Box, Flex, Heading, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/Link'

const UseCases = () => {
  const img = useStaticQuery(graphql`
    query {
      removalImage: file(
        relativePath: {
          eq: "Roaring_River_Dam_Removal_-_digging_-_Paul_Kingsbury_TNC_P1030732.jpg"
        }
      ) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            width: 960
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
    }
  `).removalImage.childImageSharp.gatsbyImageData

  return (
    <Box id="example" variant="boxes.section">
      <Heading as="h2" variant="header.section">
        Example: prioritizing a failing dam for removal
      </Heading>
      <Paragraph>
        The Southeast Aquatic Barrier Inventory and this tool will enable
        partners to identify and prioritize aging dams for removal, such as the
        Roaring River Dam in Tennessee removed in 2017. At 220 feet wide and 15
        tall, this dam is the largest removed in Tennessee for river and stream
        restoration.
      </Paragraph>

      <Box my="2rem">
        <GatsbyImage image={img} />
        <Box sx={{ fontSize: 0 }}>
          Photo:{' '}
          <OutboundLink to="https://www.nature.org/en-us/about-us/where-we-work/united-states/tennessee/stories-in-tennessee/dam-removal-opens-up-roaring-river/">
            Roaring River Dam Removal, Tennessee, 2017. © Rob Bullard, The
            Nature Conservancy.
          </OutboundLink>
        </Box>
      </Box>

      <Paragraph>
        Built in 1976 by the U.S. Army Corps of Engineers to keep reservoir fish
        species from migrating upstream, partners determined that this
        deteriorating dam no longer met its original purpose. Instead of
        repairing the dam, partners decided that it would be better to remove
        the dam altogether in order to restore aquatic connectivity. Partners
        working on this project included the Tennessee Wildlife Resources
        Agency, the U.S. Army Corps of Engineers, The Nature Conservancy, the
        U.S. Fish and Wildlife Service, and the Southeast Aquatic Resources
        Partnership.
      </Paragraph>
    </Box>
  )
}

export default UseCases
