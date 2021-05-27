import React from 'react'
import PropTypes from 'prop-types'

import { View } from '@react-pdf/renderer'

const Flex = ({ children, style, ...props }) => (
  <View
    style={{
      display: 'flex',
      flexDirection: 'row',
      flexWrap: 'nowrap',
      ...style,
    }}
    {...props}
  >
    {children}
  </View>
)

Flex.propTypes = {
  children: PropTypes.arrayOf(PropTypes.node).isRequired,
  style: PropTypes.object,
}

Flex.defaultProps = {
  style: {},
}

export default Flex
