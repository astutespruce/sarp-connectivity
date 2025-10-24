import React from 'react'
import {
  Box,
  Container,
  Flex,
  Heading,
  Grid,
  Image,
  Paragraph,
  Text,
  Divider,
} from 'theme-ui'

import { siteMetadata } from 'config'
import { useSummaryData } from 'components/Data'
import { Link, OutboundLink } from 'components/Link'
import { HighlightBox } from 'components/Layout'
import { formatNumber } from 'util/format'

import NACCLogo from 'images/nacc_logo.svg'
import FlockProcessDamImage from 'images/28274676694_1840f44362_o.jpg'
import NumanaDamImage from 'images/53188100355_4ac3d174a8_o.jpg'
import GrahamCulvertImage from 'images/54791618987_56ea39a5db_o.jpg'
import DamRemovalTeamImage from 'images/Roaring_River_dam_removal_partners_small.jpg'

const { naccURL } = siteMetadata

const Top = () => {
  const {
    dams,
    removedDams,
    smallBarriers,
    totalSmallBarriers,
    removedSmallBarriers,
    unsurveyedRoadCrossings,
  } = useSummaryData()

  return (
    <>
      <Container sx={{ mt: '2rem', mb: 0 }}>
        <Flex
          sx={{
            gap: '1rem',
            alignItems: 'flex-end',
            justifyContent: 'center',
          }}
        >
          <OutboundLink to={naccURL}>
            <Image
              src={NACCLogo}
              alt="National Aquatic Connectivity Collaborative logo"
              sx={{ width: '32rem' }}
            />
          </OutboundLink>
        </Flex>
      </Container>

      <Box
        sx={{
          background:
            'radial-gradient(farthest-corner circle at 50% 85% in oklch, oklch(0.4 0.12 240), oklch(0.26 0.08 240))',
        }}
      >
        <Container sx={{ mt: 0, mb: 0, py: '1rem' }}>
          <Heading
            as="h1"
            sx={{
              fontSize: [4, 5, 6],
              lineHeight: 1.1,
              color: '#FFF',
              textShadow: '1px 1px 3px #000',
            }}
          >
            <Box sx={{ fontSize: 4, fontStyle: 'italic' }}>National</Box>
            Aquatic Barrier Inventory
            <br />& Prioritization Tool
          </Heading>
        </Container>
      </Box>

      <Box
        sx={{
          bg: 'blue.0',
          borderBottom: '1px solid',
          borderBottomColor: 'grey.2',
        }}
      >
        <Container sx={{ mt: 0, mb: 0, py: '1rem' }}>
          <Grid columns={[0, 2]} gap={0}>
            <Box>
              <Box sx={{ fontSize: 3, mb: '0.25rem' }}>
                <Text
                  sx={{ display: 'inline', fontWeight: 'bold', fontSize: 4 }}
                >
                  {formatNumber(dams)}
                </Text>{' '}
                inventoried dams
              </Box>
              <Box sx={{ fontSize: 1, color: 'grey.8' }}>
                <b>{formatNumber(removedDams)}</b> removed for conservation
              </Box>
            </Box>
            <Box
              sx={{
                borderLeft: '1px solid',
                borderLeftColor: 'grey.2',
                pl: '1rem',
              }}
            >
              <Box
                sx={{
                  fontSize: 3,
                  mb: '0.25rem',
                }}
              >
                <Text
                  sx={{ display: 'inline', fontWeight: 'bold', fontSize: 4 }}
                >
                  {formatNumber(totalSmallBarriers + unsurveyedRoadCrossings)}
                </Text>{' '}
                road/stream crossings
              </Box>
              <Box sx={{ fontSize: 1, color: 'grey.8' }}>
                <b>{formatNumber(totalSmallBarriers)}</b> assessed for impacts
                to aquatic organisms
                <br />
                <b>{formatNumber(smallBarriers - removedSmallBarriers)}</b>{' '}
                assessed barriers likely to impact aquatic organisms
                <br />
                <b>{formatNumber(removedSmallBarriers)}</b> removed for
                conservation
              </Box>
            </Box>
          </Grid>
        </Container>
      </Box>
    </>
  )
}

export default Top
