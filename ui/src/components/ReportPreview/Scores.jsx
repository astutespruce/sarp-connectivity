/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text, Paragraph } from 'theme-ui'

import { Table, Row } from 'components/Table'
import { barrierTypeLabels } from 'config'

const Scores = ({
  barrierType,
  state,
  ranked,
  invasive,
  nostructure,
  state_nc_tier,
  state_wc_tier,
  state_ncwc_tier,
  state_pnc_tier,
  state_pwc_tier,
  state_pncwc_tier,
  sx,
}) => {
  if (!ranked) {
    return null
  }

  // small barriers do not have state ranks
  if (barrierType === 'small_barriers') {
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

  if (nostructure) {
    return (
      <Box sx={null}>
        {header}
        <Text>
          This {barrierTypeLabel} was excluded from prioritization because it is
          a water diversion without associated in-stream barrier.
        </Text>
      </Box>
    )
  }

  return (
    <Box sx={null}>
      {header}
      <Text variant="help" sx={{ fontSize: 0, textAlign: 'center' }}>
        connectivity tiers range from 20 (lowest) to 1 (highest)
      </Text>

      <Box>
        <Table
          columns="22em 1fr 12em"
          sx={{
            mt: '2rem',
            '> div:not(:first-of-type)': {
              pt: '0.5rem',
            },
          }}
        >
          <Row>
            <Box sx={{ fontStyle: 'italic' }}>
              Compared to other {barrierTypeLabel} in {state}:
            </Box>
            <Box>
              <b>full network</b>
            </Box>
            <Box>
              <b>perennial reaches only</b>
            </Box>
          </Row>
          <Row>
            <Box>Network connectivity tier</Box>
            <Box>{state_nc_tier}</Box>
            <Box>{state_pnc_tier}</Box>
          </Row>
          <Row>
            <Box>Watershed condition tier</Box>
            <Box>{state_wc_tier}</Box>
            <Box>{state_pwc_tier}</Box>
          </Row>
          <Row>
            <Box>
              Combined network connectivity &amp;
              <br />
              watershed condition tier
            </Box>
            <Box>{state_ncwc_tier}</Box>
            <Box>{state_pncwc_tier}</Box>
          </Row>
        </Table>
      </Box>

      <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
        Note: perennial network connectivity is based on the total perennial
        (non-intermittent or ephemeral) length in a given network. Perennial
        watershed condition is based partly upon the percent of the perennial
        stream reaches that are not altered (canals / ditches).
      </Paragraph>

      <Box sx={{ mt: '1rem' }} />
    </Box>
  )
}
Scores.propTypes = {
  barrierType: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  ranked: PropTypes.bool,
  invasive: PropTypes.bool,
  nostructure: PropTypes.bool,
  state_nc_tier: PropTypes.number,
  state_wc_tier: PropTypes.number,
  state_ncwc_tier: PropTypes.number,
  state_pnc_tier: PropTypes.number,
  state_pwc_tier: PropTypes.number,
  state_pncwc_tier: PropTypes.number,
  sx: PropTypes.object,
}

Scores.defaultProps = {
  ranked: false,
  invasive: false,
  nostructure: false,
  state_nc_tier: null,
  state_wc_tier: null,
  state_ncwc_tier: null,
  state_pnc_tier: null,
  state_pwc_tier: null,
  state_pncwc_tier: null,
  sx: null,
}

export default Scores
