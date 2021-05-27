import React from 'react'
import PropTypes from 'prop-types'

import { Text, View } from '@react-pdf/renderer'

import Bold from './Bold'

const List = ({ title, note, children, style }) => (
  <View style={style}>
    <View style={{ marginBottom: 4 }}>
      <Bold
        style={{
          fontSize: 14,
        }}
      >
        {title}
      </Bold>
      {note ? (
        <Text style={{ color: '#7f8a93', fontSize: 10 }}>{note}</Text>
      ) : null}
    </View>
    <View>{children}</View>
  </View>
)

List.propTypes = {
  title: PropTypes.string.isRequired,
  note: PropTypes.string,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  style: PropTypes.object,
}

List.defaultProps = {
  note: null,
  style: {},
}

export default List
