/* eslint-disable camelcase */

import React from 'react'
import { Box, Flex, Grid, Image, Paragraph, Heading } from 'theme-ui'

import { Link, OutboundLink } from 'components/Link'
import { HighlightBox } from 'components/Layout'
import { formatNumber } from 'util/format'
import { useSummaryData } from 'components/Data'
import SARPLogoImage from 'images/sarp_logo.png'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion, date: dataDate } = siteMetadata

const Inventory = () => {
  const { dams, total_barriers, miles } = useSummaryData()

  return (
    <Box variant="boxes.section">
      <Heading as="h2" variant="heading.section">
        The Southeast Aquatic Barrier Inventory:
      </Heading>
      <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '2rem' }}>
        <Box>
          <Paragraph>
            This inventory is a growing and living database of dams, culverts,
            and other road crossings compiled by the{' '}
            <OutboundLink to="https://southeastaquatics.net/">
              Southeast Aquatic Resources Partnership
            </OutboundLink>{' '}
            with the generous support from many partners and funders. The
            Inventory is the foundation of{' '}
            <OutboundLink to="https://southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap">
              SARP&apos;s Connectivity Program
            </OutboundLink>{' '}
            because it empowers{' '}
            <Link to="/teams">Aquatic Connectivity Teams</Link> and other
            collaborators with the best available information on aquatic
            barriers. The inventory directly supports prioritization of barriers
            by including metrics that describe network connectivity, landscape
            condition, and presence of threatened and endangered aquatic
            organisms.
            <br />
            <br />
            This inventory consists of datasets from local, state, and federal
            partners. It is supplemented with input from partners with on the
            ground knowledge of specific structures.{' '}
            <Link to="/#example">
              See an example of how the inventory can assist local partners to
              identify and prioritize barriers for removal.
            </Link>
            <br />
            <br />
            The information on barriers is not complete or comprehensive across
            the region, and depends on the availability and completeness of
            existing data and level of partner feedback. Some areas of the
            region are more complete than others but none should be considered
            100% complete.
          </Paragraph>
        </Box>

        <Box
          sx={{
            h3: {
              textAlign: 'center',
            },
          }}
        >
          <HighlightBox title="At a Glance" icon="">
            <Box
              as="ul"
              sx={{
                listStyle: 'none',
                fontSize: '1.25rem',
                mt: '1rem',
                ml: 0,
                p: 0,
                lineHeight: 1.3,
                li: {
                  mb: '2rem',
                },
              }}
            >
              <li>
                <b>14</b> states and Puerto Rico
              </li>
              <li>
                <b>{formatNumber(dams, 0)}</b> dams
              </li>
              <li>
                <b>{formatNumber(total_barriers, 0)}</b> road-related barriers
                assessed for impact to aquatic organisms
              </li>
              <li>
                <b>{formatNumber(miles, 1)}</b> miles of connected aquatic
                network length, on average
              </li>
            </Box>

            <Flex sx={{ justifyContent: 'center', width: '100%' }}>
              <Image src={SARPLogoImage} width="224px" alt="SARP logo" />
            </Flex>

            <Paragraph
              sx={{
                mt: '1rem',
                textAlign: 'center',
              }}
            >
              Data version: {dataVersion} ({dataDate})
            </Paragraph>
          </HighlightBox>
        </Box>
      </Grid>
    </Box>
  )
}

export default Inventory
