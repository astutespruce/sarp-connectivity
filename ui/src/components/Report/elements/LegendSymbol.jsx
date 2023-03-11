import React from 'react'
import PropTypes from 'prop-types'
import { Circle, Line, Svg, View } from '@react-pdf/renderer'

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
      <View style={{ flex: '0 0 16' }}>
        <Svg width={12} height={12}>
          <Line
            x1={0}
            x2={12}
            y1={6}
            y2={6}
            fill={color}
            strokeWidth={borderWidth}
            strokeDasharray={borderStyle === 'dashed' ? '4, 1' : null}
            stroke={color}
          />
        </Svg>
      </View>
    )
  }
  return (
    <View style={{ flex: '0 0 16' }}>
      <Svg
        width={(radius + borderWidth) * 2}
        height={(radius + borderWidth) * 2}
      >
        <Circle
          cx={radius + borderWidth}
          cy={radius + borderWidth}
          r={radius}
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
  radius: PropTypes.number,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string,
  borderWidth: PropTypes.number,
  borderStyle: PropTypes.string,
}

LegendSymbol.defaultProps = {
  borderColor: null,
  borderWidth: null,
  borderStyle: null,
  radius: 8,
}

export default LegendSymbol
