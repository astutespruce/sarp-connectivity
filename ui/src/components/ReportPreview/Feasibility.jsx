/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading } from 'theme-ui'

import { RECON } from 'constants'

const Feasibility = ({ recon, huc8_coa, sx }) => (
  <Box sx={sx}>
    <Heading as="h3">Feasibility & conservation benefit</Heading>

    <Box as="ul" sx={{ mt: '0.5rem' }}>
      {recon !== null ? (
        <li>{RECON[recon]}</li>
      ) : (
        <li>No feasibility information is available for this barrier.</li>
      )}

      {/* watershed priorities */}
      {huc8_coa > 0 ? (
        <li>Within a SARP conservation opportunity area.</li>
      ) : null}
    </Box>
  </Box>
)

Feasibility.propTypes = {
  recon: PropTypes.number,
  huc8_coa: PropTypes.number,
  sx: PropTypes.object,
}

Feasibility.defaultProps = {
  recon: 0,
  huc8_coa: 0,
  sx: null,
}

export default Feasibility
