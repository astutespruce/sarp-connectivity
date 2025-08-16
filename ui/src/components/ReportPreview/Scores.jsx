/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text, Paragraph } from 'theme-ui'

import { Table, Row } from 'components/Table'
import { barrierTypeLabels, STATES } from 'config'

const Scores = ({
  barrierType,
  networkType,
  state,
  ranked,
  invasive,
  state_nc_tier,
  state_wc_tier,
  state_ncwc_tier,
  state_pnc_tier,
  state_pwc_tier,
  state_pncwc_tier,
  state_mnc_tier,
  state_mwc_tier,
  state_mncwc_tier,
  huc8_nc_tier,
  huc8_wc_tier,
  huc8_ncwc_tier,
  huc8_pnc_tier,
  huc8_pwc_tier,
  huc8_pncwc_tier,
  huc8_mnc_tier,
  huc8_mwc_tier,
  huc8_mncwc_tier,
  sx,
}) => {
  if (!ranked) {
    return null
  }

  const hasStateTiers = networkType === 'dams' && state_ncwc_tier !== -1
  const hasHUC8Tiers = huc8_ncwc_tier !== -1

  if (!(hasStateTiers || hasHUC8Tiers)) {
    return null
  }

  const barrierTypeLabel = barrierTypeLabels[barrierType]

  const header = <Heading as="h3">Connectivity ranks</Heading>

  if (invasive) {
    return (
      <Box sx={sx}>
        {header}
        <Text>
          This {barrierTypeLabel} was excluded from prioritization because it
          provides an ecological benefit by restricting the movement of invasive
          aquatic species.
        </Text>
      </Box>
    )
  }

  return (
    <Box sx={sx}>
      {header}
      <Text variant="help" sx={{ fontSize: 0, textAlign: 'center' }}>
        connectivity tiers range from 20 (lowest) to 1 (highest)
      </Text>

      <Box>
        {hasStateTiers ? (
          <Table
            columns="18em 1fr 1fr 1fr"
            sx={{
              mt: '2rem',
              '> div:not(:first-of-type)': {
                pt: '0.5rem',
              },
            }}
          >
            <Row
              sx={{
                lineHeight: 1.2,
                alignItems: 'end',
                '& > div+div': { textAlign: 'center' },
              }}
            >
              <Box sx={{ fontStyle: 'italic' }}>
                Compared to other {barrierTypeLabel} in {STATES[state]}:
              </Box>
              <Box sx={{ fontWeight: 'bold' }}>full network</Box>
              <Box sx={{ fontWeight: 'bold' }}>perennial reaches</Box>
              <Box sx={{ fontWeight: 'bold' }}>mainstem network</Box>
            </Row>
            <Row sx={{ '& > div+div': { textAlign: 'center' } }}>
              <Box>Network connectivity tier</Box>
              <Box>{state_nc_tier}</Box>
              <Box>{state_pnc_tier}</Box>
              <Box>{state_mnc_tier}</Box>
            </Row>
            <Row sx={{ '& > div+div': { textAlign: 'center' } }}>
              <Box>Watershed condition tier</Box>
              <Box>{state_wc_tier}</Box>
              <Box>{state_pwc_tier}</Box>
              <Box>{state_mwc_tier}</Box>
            </Row>
            <Row sx={{ '& > div+div': { textAlign: 'center' } }}>
              <Box>
                Combined network connectivity &amp;
                <br />
                watershed condition tier
              </Box>
              <Box>{state_ncwc_tier}</Box>
              <Box>{state_pncwc_tier}</Box>
              <Box>{state_mncwc_tier}</Box>
            </Row>
          </Table>
        ) : null}

        {hasHUC8Tiers ? (
          <Table
            columns="18em 1fr 1fr 1fr"
            sx={{
              mt: hasStateTiers ? '4rem' : '2rem',
              '> div:not(:first-of-type)': {
                pt: '0.5rem',
              },
            }}
          >
            <Row
              sx={{
                lineHeight: 1.2,
                alignItems: 'end',
                '& > div+div': { textAlign: 'center' },
              }}
            >
              <Box sx={{ fontStyle: 'italic' }}>
                Compared to other {barrierTypeLabel} in this subbasin:
              </Box>
              <Box sx={{ fontWeight: 'bold' }}>
                full
                <br />
                network
              </Box>
              <Box sx={{ fontWeight: 'bold' }}>
                perennial
                <br />
                reaches
              </Box>
              <Box sx={{ fontWeight: 'bold' }}>
                mainstem
                <br />
                network
              </Box>
            </Row>
            <Row sx={{ '& > div+div': { textAlign: 'center' } }}>
              <Box>Network connectivity tier</Box>
              <Box>{huc8_nc_tier}</Box>
              <Box>{huc8_pnc_tier}</Box>
              <Box>{huc8_mnc_tier}</Box>
            </Row>
            <Row sx={{ '& > div+div': { textAlign: 'center' } }}>
              <Box>Watershed condition tier</Box>
              <Box>{huc8_wc_tier}</Box>
              <Box>{huc8_pwc_tier}</Box>
              <Box>{huc8_mwc_tier}</Box>
            </Row>
            <Row sx={{ '& > div+div': { textAlign: 'center' } }}>
              <Box>
                Combined network connectivity &amp;
                <br />
                watershed condition tier
              </Box>
              <Box>{huc8_ncwc_tier}</Box>
              <Box>{huc8_pncwc_tier}</Box>
              <Box>{huc8_mncwc_tier}</Box>
            </Row>
          </Table>
        ) : null}
      </Box>

      <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
        Note: network connectivity is based on the total perennial length in a
        given network. Watershed condition is based on the percent of the total
        length of stream reaches in the network that are not altered (canals /
        ditches), the number of unique stream size classes, and the percent of
        natural landcover in the floodplains. Perennial network connectivity is
        based on the total perennial (non-intermittent or ephemeral) length in a
        given network. Perennial watershed condition is based on the percent of
        the total length of perennial stream reaches that are not altered
        (canals / ditches), the number of unique stream size classes in
        perennial reaches, and the percent of natural landcover in the
        floodplains for the full network. Mainstem network connectivity is based
        on the total mainstem network length in a given network. Mainstem
        watershed condition is based on the percent of the total length of
        stream reaches in the mainstem network that are not altered (canals /
        ditches), the number of unique stream size classes in the mainstem
        network, and the percent of natural landcover in the floodplains for the
        full network.
      </Paragraph>

      <Box sx={{ mt: '1rem' }} />
    </Box>
  )
}
Scores.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  ranked: PropTypes.bool,
  invasive: PropTypes.bool,
  state_nc_tier: PropTypes.number,
  state_wc_tier: PropTypes.number,
  state_ncwc_tier: PropTypes.number,
  state_pnc_tier: PropTypes.number,
  state_pwc_tier: PropTypes.number,
  state_pncwc_tier: PropTypes.number,
  state_mnc_tier: PropTypes.number,
  state_mwc_tier: PropTypes.number,
  state_mncwc_tier: PropTypes.number,
  huc8_nc_tier: PropTypes.number,
  huc8_wc_tier: PropTypes.number,
  huc8_ncwc_tier: PropTypes.number,
  huc8_pnc_tier: PropTypes.number,
  huc8_pwc_tier: PropTypes.number,
  huc8_pncwc_tier: PropTypes.number,
  huc8_mnc_tier: PropTypes.number,
  huc8_mwc_tier: PropTypes.number,
  huc8_mncwc_tier: PropTypes.number,
  sx: PropTypes.object,
}

Scores.defaultProps = {
  ranked: false,
  invasive: false,
  state_nc_tier: null,
  state_wc_tier: null,
  state_ncwc_tier: null,
  state_pnc_tier: null,
  state_pwc_tier: null,
  state_pncwc_tier: null,
  state_mnc_tier: null,
  state_mwc_tier: null,
  state_mncwc_tier: null,
  huc8_nc_tier: null,
  huc8_wc_tier: null,
  huc8_ncwc_tier: null,
  huc8_pnc_tier: null,
  huc8_pwc_tier: null,
  huc8_pncwc_tier: null,
  huc8_mnc_tier: null,
  huc8_mwc_tier: null,
  huc8_mncwc_tier: null,
  sx: null,
}

export default Scores
