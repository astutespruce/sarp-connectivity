import React from 'react'
import { Box, Grid, Paragraph, Heading, Text } from 'theme-ui'

import { Link, OutboundLink } from 'components/Link'
import { HighlightBox } from 'components/Layout'
import { siteMetadata, ANALYSIS_STATES } from 'config'
import { formatNumber } from 'util/format'
import { useSummaryData } from 'components/Data'

const { version: dataVersion, date: dataDate } = siteMetadata

const Inventory = () => {
  const { dams, removedDams, totalSmallBarriers, removedSmallBarriers } =
    useSummaryData()

  return (
    <Box variant="boxes.section">
      <Heading as="h2" variant="heading.section">
        The Aquatic Barrier Inventory:
      </Heading>
      <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '2rem' }}>
        <Box>
          <Paragraph>
            This inventory is a growing and living database of dams, culverts,
            and other road crossings compiled by SARP with the generous support
            from many partners and funders. Originally developed within the
            Southeast as part of SARP&apos;s Aquatic Connectivity Program, this
            inventory and tool have been expanded to a broader geographic area
            to empower state-level Aquatic Connectivity Teams and other
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
            <Link to="/regions/southeast/use_cases">
              See an example of how the inventory can assist local partners to
              identify and prioritize barriers for removal.
            </Link>
            <br />
            <br />
            If you have recently completed a dam removal, fish passage, or
            barrier remediation project, please use the following links to
            report these projects so they may be included in the inventory:
          </Paragraph>
          <Box as="ul" sx={{ mt: '0.5rem' }}>
            <li>
              <OutboundLink to="https://arcg.is/1fvmXS1">
                Dam removal and fish passage at dams
              </OutboundLink>
            </li>
            <li>
              <OutboundLink to="https://arcg.is/11OSuL0">
                Road related barrier replacement
              </OutboundLink>
            </li>
          </Box>
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
                <b>{ANALYSIS_STATES.length - 3}</b> states, Washington DC,
                Puerto Rico, and U.S. Virgin Islands
              </li>
              <li>
                <b>{formatNumber(dams, 0)}</b> inventoried dams
                <Text sx={{ fontSize: 1, mt: '0.25rem' }}>
                  ({formatNumber(removedDams, 0)} removed for conservation)
                </Text>
              </li>

              <li>
                <b>{formatNumber(totalSmallBarriers, 0)}</b> road-related
                barriers assessed for impact to aquatic organisms
                <Text sx={{ fontSize: 1, mt: '0.25rem' }}>
                  ({formatNumber(removedSmallBarriers, 0)} removed for
                  conservation)
                </Text>
              </li>
            </Box>

            <Paragraph
              sx={{
                mt: '1rem',
                textAlign: 'center',
              }}
            >
              Data version: {dataVersion} ({dataDate})
            </Paragraph>
          </HighlightBox>
          <Paragraph variant="help" sx={{ mt: '1rem' }}>
            Note: the information on barriers is not yet complete or
            comprehensive. It depends on the availability and completeness of
            existing data and level of partner feedback. Some states are more
            complete than others but none should be considered 100% complete.
          </Paragraph>
        </Box>
      </Grid>
    </Box>
  )
}

export default Inventory
