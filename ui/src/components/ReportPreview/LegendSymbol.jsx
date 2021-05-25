import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex } from 'theme-ui'

const LegendSymbol = ({ type, color, borderColor, borderWidth }) => {
  if (type === 'line') {
    return (
      <Flex sx={{ alignItems: 'center', flex: '0 0 auto' }}>
        <Box sx={{ width: '1rem', height: `${borderWidth}px`, bg: color }} />
      </Flex>
    )
  }
  // circle
  return (
    <Box
      sx={{
        flex: '0 0 auto',
        mt: '0.25rem',
        width: '0.75rem',
        height: '0.75rem',
        borderRadius: '1rem',
        bg: color,
        border: borderWidth ? `${borderWidth}px solid ${borderColor}` : null,
      }}
    />
  )
}

LegendSymbol.propTypes = {
  type: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string,
  borderWidth: PropTypes.number,
}

LegendSymbol.defaultProps = {
  borderColor: null,
  borderWidth: null,
}

export default LegendSymbol
