import React from 'react'
import PropTypes from 'prop-types'
import { Circle, Line, Svg, View } from '@react-pdf/renderer'

const LegendSymbol = ({ type, color, borderColor, borderWidth }) => {
  if (type === 'line') {
    return (
      <View style={{ flex: '0 0 16' }}>
        <Svg width={12} height={12}>
          <Line
            x1={0}
            x2={12}
            y1={6}
            y2={6}
            fill={color}
            strokeWidth={borderWidth}
            stroke={color}
          />
        </Svg>
      </View>
    )
  }
  return (
    <View style={{ flex: '0 0 16' }}>
      <Svg width={12} height={12}>
        <Circle
          cx={6}
          cy={6}
          r={4}
          fill={color}
          strokeWidth={borderWidth}
          stroke={borderColor}
        />
      </Svg>
    </View>
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
