import React from 'react'
import PropTypes from 'prop-types'

import { Text, View } from '@react-pdf/renderer'

const List = ({ title, children, marginTop }) => (
  <View style={{ marginTop }}>
    <Text
      style={{
        fontFamily: 'Helvetica-Bold',
        fontSize: 14,
        marginBottom: 4,
      }}
    >
      {title}
    </Text>
    <View>{children}</View>
  </View>
)

List.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  marginTop: PropTypes.number,
}

List.defaultProps = {
  marginTop: 0,
}

export default List
