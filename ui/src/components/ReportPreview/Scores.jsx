/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text, Paragraph } from 'theme-ui'

import { Table, Row } from 'components/Table'
import { barrierTypeLabels } from '../../../config/constants'

const Scores = ({
  barrierType,
  state,
  hasnetwork,
  ranked,
  state_nc_tier,
  state_wc_tier,
  state_ncwc_tier,
  state_pnc_tier,
  state_pwc_tier,
  state_pncwc_tier,
  se_nc_tier,
  se_wc_tier,
  se_ncwc_tier,
  se_pnc_tier,
  se_pwc_tier,
  se_pncwc_tier,
  ...props
}) => {
  if (!hasnetwork) {
    return null
  }

  const hasSoutheast =
    se_nc_tier !== null && se_nc_tier !== undefined && se_nc_tier !== -1

  const barrierTypeLabel = barrierTypeLabels[barrierType]

  const header = <Heading as="h3">Connectivity ranks</Heading>

  if (!ranked) {
    return (
      <Box {...props}>
        {header}
        <Text>
          This {barrierType === 'dams' ? 'dam' : 'road-related barrier'} was
          excluded from prioritization because it provides an ecological benefit
          by restricting the movement of invasive aquatic species.
        </Text>
      </Box>
    )
  }

  return (
    <Box {...props}>
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
              <b>perennial segments only</b>
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
              Combined network connectivity &amp; watershed condition tier
            </Box>
            <Box>{state_ncwc_tier}</Box>
            <Box>{state_pncwc_tier}</Box>
          </Row>
        </Table>

        {hasSoutheast ? (
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
                Compared to other {barrierTypeLabel} in the Southeast:
              </Box>
              <Box />
              <Box />
            </Row>
            <Row>
              <Box>Network connectivity tier</Box>
              <Box>{se_nc_tier}</Box>
              <Box>{se_pnc_tier}</Box>
            </Row>
            <Row>
              <Box>Watershed condition tier</Box>
              <Box>{se_wc_tier}</Box>
              <Box>{se_pwc_tier}</Box>
            </Row>
            <Row>
              <Box>
                Combined network connectivity &amp; watershed condition tier
              </Box>
              <Box>{se_ncwc_tier}</Box>
              <Box>{se_pncwc_tier}</Box>
            </Row>
          </Table>
        ) : null}
      </Box>

      <Paragraph variant="help" sx={{ mt: '2rem' }}>
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
  hasnetwork: PropTypes.bool,
  ranked: PropTypes.bool,
  state_nc_tier: PropTypes.number,
  state_wc_tier: PropTypes.number,
  state_ncwc_tier: PropTypes.number,
  state_pnc_tier: PropTypes.number,
  state_pwc_tier: PropTypes.number,
  state_pncwc_tier: PropTypes.number,
  se_nc_tier: PropTypes.number,
  se_wc_tier: PropTypes.number,
  se_ncwc_tier: PropTypes.number,
  se_pnc_tier: PropTypes.number,
  se_pwc_tier: PropTypes.number,
  se_pncwc_tier: PropTypes.number,
}

Scores.defaultProps = {
  hasnetwork: false,
  ranked: false,
  state_nc_tier: null,
  state_wc_tier: null,
  state_ncwc_tier: null,
  state_pnc_tier: null,
  state_pwc_tier: null,
  state_pncwc_tier: null,
  se_nc_tier: null,
  se_wc_tier: null,
  se_ncwc_tier: null,
  se_pnc_tier: null,
  se_pwc_tier: null,
  se_pncwc_tier: null,
}

export default Scores
