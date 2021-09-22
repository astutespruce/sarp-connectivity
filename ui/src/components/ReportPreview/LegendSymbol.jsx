import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex } from 'theme-ui'

const LegendSymbol = ({
  type,
  color,
  borderColor,
  borderWidth,
  borderStyle,
}) => {
  if (type === 'line') {
    return (
      <Flex sx={{ alignItems: 'center', flex: '0 0 auto' }}>
        {/* <Box sx={{ width: '1rem', height: `${borderWidth}px`, bg: color }} /> */}
        <Box
          sx={{
            width: '1rem',
            borderTop: `${borderWidth}px ${borderStyle} ${color}`,
          }}
        />
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
  borderStyle: PropTypes.string,
}

LegendSymbol.defaultProps = {
  borderColor: null,
  borderWidth: null,
  borderStyle: 'solid',
}

export default LegendSymbol
