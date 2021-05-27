import React from 'react'
import PropTypes from 'prop-types'

import { Circle, Svg, View } from '@react-pdf/renderer'

const ListItem = ({ children, style }) => (
  <View
    style={{
      marginBottom: 4,
      display: 'flex',
      flexDirection: 'row',
      alignItems: 'flex-start',
      flexWrap: 'nowrap',
      ...style,
    }}
  >
    <View style={{ flex: '0 0 16' }}>
      <Svg width={12} height={12}>
        <Circle cx={6} cy={6} r={2} fill="#333" />
      </Svg>
    </View>
    <View style={{ flex: '1 1 auto' }}>{children}</View>
  </View>
)

ListItem.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  style: PropTypes.object,
}

ListItem.defaultProps = {
  style: {},
}

export default ListItem
