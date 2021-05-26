/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { RECON, HUC8_USFS } from '../../../config/constants'

const Feasibility = ({ recon, huc8_coa, huc8_sgcn, huc8_usfs }) => (
  <Box>
    <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
      Feasibility & conservation benefit
    </Text>

    <Box as="ul" sx={{ mt: '0.5rem' }}>
      {recon !== null ? (
        <li>{RECON[recon]}</li>
      ) : (
        <li>No feasibility information is available for this barrier.</li>
      )}

      {/* watershed priorities */}
      {huc8_usfs > 0 && (
        <li>Within USFS {HUC8_USFS[huc8_usfs]} priority watershed.</li>
      )}
      {huc8_coa > 0 && <li>Within a SARP conservation opportunity area.</li>}
      {huc8_sgcn > 0 && (
        <li>
          Within one of the top 10 watersheds in this state based on number of
          state-listed Species of Greatest Conservation Need.
        </li>
      )}
    </Box>
  </Box>
)

Feasibility.propTypes = {
  recon: PropTypes.number,
  huc8_usfs: PropTypes.number,
  huc8_coa: PropTypes.number,
  huc8_sgcn: PropTypes.number,
}

Feasibility.defaultProps = {
  recon: 0,
  huc8_usfs: 0,
  huc8_coa: 0,
  huc8_sgcn: 0,
}

export default Feasibility
