import React from 'react'
import PropTypes from 'prop-types'

import { Flex } from 'theme-ui'

const Circle = ({ radius, color, borderColor, borderWidth }) => {
  const width = 2 * borderWidth + 2 * radius
  const center = width / 2

  return (
    <Flex
      sx={{
        justifyContent: 'flex-start',
        alignItems: 'center',
        width: '18px',
        flex: '0 0 auto',
      }}
    >
      <svg style={{ width, height: width }}>
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill={color}
          stroke={borderColor}
          strokeWidth={borderWidth}
        />
      </svg>
    </Flex>
  )
}

Circle.propTypes = {
  radius: PropTypes.number.isRequired,
  color: PropTypes.string,
  borderColor: PropTypes.string,
  borderWidth: PropTypes.number,
}

Circle.defaultProps = {
  borderWidth: 0,
  color: null,
  borderColor: null,
}

export default Circle
