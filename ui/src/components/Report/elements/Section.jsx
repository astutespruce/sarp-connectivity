import React from 'react'
import PropTypes from 'prop-types'

import { View } from '@react-pdf/renderer'

import Bold from './Bold'

const Section = ({ title, children, style, marginBottom, wrap }) => (
  <View style={style} wrap={wrap}>
    <Bold
      style={{
        fontSize: 14,
        marginBottom,
        padding: '6pt 12pt',
        lineHeight: 1,
        backgroundColor: '#dbf0ff',
      }}
    >
      {title}
    </Bold>
    {children}
  </View>
)

Section.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  style: PropTypes.object,
  marginBottom: PropTypes.number,
  wrap: PropTypes.bool,
}

Section.defaultProps = {
  style: {},
  marginBottom: 14,
  wrap: false,
}

export default Section
