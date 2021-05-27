import React from 'react'
import PropTypes from 'prop-types'

import { View } from '@react-pdf/renderer'

import Bold from './Bold'

const Section = ({ title, children, style }) => (
  <View style={style}>
    <Bold style={{ fontSize: 14, marginBottom: 6 }}>{title}</Bold>
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
