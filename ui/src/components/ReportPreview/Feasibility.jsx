/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading } from 'theme-ui'

import { RECON, FEASIBILITYCLASS } from 'config'

const Feasibility = ({ recon, feasibilityclass, sx }) => (
  <Box sx={sx}>
    <Heading as="h3">Feasibility & conservation benefit</Heading>

    <Box sx={{ mt: '0.5rem' }}>
      <Box>Feasibility: {FEASIBILITYCLASS[feasibilityclass]}</Box>

      {recon !== null && recon > 0 ? (
        <Box sx={{ mt: '0.5rem' }}>Field recon notes: {RECON[recon]}</Box>
      ) : null}
    </Box>
  </Box>
)

Feasibility.propTypes = {
  recon: PropTypes.number,
  feasibilityclass: PropTypes.number,
  sx: PropTypes.object,
}

Feasibility.defaultProps = {
  recon: 0,
  feasibilityclass: 0,
  sx: null,
}

export default Feasibility
