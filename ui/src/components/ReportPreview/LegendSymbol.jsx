import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex } from 'theme-ui'

const LegendSymbol = ({
  type,
  color,
  radius,
  borderColor,
  borderWidth,
  borderStyle,
}) => {
  if (type === 'line') {
    return (
      <Flex sx={{ alignItems: 'center', flex: '0 0 auto' }}>
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
        flex: `0 0 auto`,
        mt: '0.25rem',
        width: `${radius * 2.5}px`,
        height: `${radius * 2.5}px`,
        borderRadius: '1rem',
        bg: color,
        border: borderWidth ? `${borderWidth}px solid ${borderColor}` : null,
      }}
    />
  )
}

LegendSymbol.propTypes = {
  type: PropTypes.string.isRequired,
  radius: PropTypes.number,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string,
  borderWidth: PropTypes.number,
  borderStyle: PropTypes.string,
}

LegendSymbol.defaultProps = {
  radius: 8,
  borderColor: null,
  borderWidth: null,
  borderStyle: 'solid',
}

export default LegendSymbol
