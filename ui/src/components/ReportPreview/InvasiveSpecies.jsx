import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading } from 'theme-ui'

import { barrierTypeLabelSingular } from 'config'

const InvasiveSpecies = ({ barrierType, invasive, invasivenetwork, sx }) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

  return (
    <Box sx={sx}>
      <Heading as="h3">Invasive species management</Heading>

      <Box sx={{ mt: '0.5rem' }}>
        {!invasive && invasivenetwork === 1 ? (
          <Box>
            Upstream of a barrier identified as a beneficial to restricting the
            movement of invasive species.
          </Box>
        ) : null}

        {invasive ? (
          <Box>
            Note: this {barrierTypeLabel} is identified as a beneficial to
            restricting the movement of invasive species.
          </Box>
        ) : null}
      </Box>
    </Box>
  )
}

InvasiveSpecies.propTypes = {
  barrierType: PropTypes.string.isRequired,
  invasive: PropTypes.bool,
  invasivenetwork: PropTypes.number,
  sx: PropTypes.object,
}

InvasiveSpecies.defaultProps = {
  invasive: 0,
  invasivenetwork: 0,
  sx: null,
}

export default InvasiveSpecies
