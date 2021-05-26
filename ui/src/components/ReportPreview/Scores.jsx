/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

const Scores = ({
  barrierType,
  hasnetwork,
  excluded,
  se_nc_tier,
  se_wc_tier,
  se_ncwc_tier,
  state_nc_tier,
  state_wc_tier,
  state_ncwc_tier,
}) => {
  const typeLabel = barrierType === 'dams' ? 'dam' : 'road-related barrier'
  return (
    <Box>
      <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>Connectivity ranks</Text>
      <Text variant="help" sx={{ fontSize: 0 }}>
        Tiers range from 20 (lowest) to 1 (highest).
      </Text>

      <Box sx={{ mt: '1rem' }} />
      {hasnetwork ? (
        <Box>
          <Text sx={{ fontStyle: 'italic' }}>State ranks</Text>
          <Box as="ul">
            <li>Network connectivity tier: {state_nc_tier}</li>
            <li>Watershed condition tier: {state_wc_tier}</li>
            <li>
              Network connectivity & watershed condition tier: {state_ncwc_tier}
            </li>
          </Box>

          <Text sx={{ fontStyle: 'italic', mt: '2rem' }}>Southeast ranks</Text>
          <Box as="ul">
            <li>Network connectivity tier: {se_nc_tier}</li>
            <li>Watershed condition tier: {se_wc_tier}</li>
            <li>
              Network connectivity & watershed condition tier: {se_ncwc_tier}
            </li>
          </Box>
        </Box>
      ) : (
        <Text variant="help">
          {excluded
            ? `This ${typeLabel} was excluded from the connectivity analysis based on field reconnaissance or manual review of aerial imagery.`
            : `This ${typeLabel} is off-network and has no functional network information.`}
        </Text>
      )}
    </Box>
  )
}
Scores.propTypes = {
  barrierType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool,
  excluded: PropTypes.bool,
  se_nc_tier: PropTypes.number,
  se_wc_tier: PropTypes.number,
  se_ncwc_tier: PropTypes.number,
  state_nc_tier: PropTypes.number,
  state_wc_tier: PropTypes.number,
  state_ncwc_tier: PropTypes.number,
}

Scores.defaultProps = {
  hasnetwork: false,
  excluded: false,
  se_nc_tier: null,
  se_wc_tier: null,
  se_ncwc_tier: null,
  state_nc_tier: null,
  state_wc_tier: null,
  state_ncwc_tier: null,
}

export default Scores
