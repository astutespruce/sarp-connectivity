import React from 'react'
import PropTypes from 'prop-types'

import { View } from '@react-pdf/renderer'

import Bold from './Bold'

const Section = ({ title, children, style }) => (
  <View style={style} wrap={false}>
    <Bold
      style={{
        fontSize: 14,
        marginBottom: 14,
        padding: '6pt 12pt',
        lineHeight: 1,
        backgroundColor: '#ebedee',
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
}

Section.defaultProps = {
  style: {},
}

export default Section
