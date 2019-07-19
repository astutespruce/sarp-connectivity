import React from 'react'
import PropTypes from 'prop-types'

import { Flex } from 'components/Grid'
import styled from 'style'

// sized to the max size of all patches / circles
const Wrapper = styled(Flex).attrs({
  justifyContent: 'flex-start',
  alignItems: 'center',
})`
  width: 18px;
  flex: 0 0 auto;
`

const Circle = ({ radius, color, borderColor, borderWidth }) => {
  const width = 2 * borderWidth + 2 * radius
  const center = width / 2

  return (
    <Wrapper>
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
    </Wrapper>
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
