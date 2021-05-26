import React from 'react'
import PropTypes from 'prop-types'

import { View, Text } from '@react-pdf/renderer'

const Section = ({ title, children, marginTop }) => (
  <View style={{ marginTop }}>
    <Text
      style={{
        fontFamily: 'Helvetica-Bold',
        fontSize: 14,
        marginBottom: 6,
      }}
    >
      {title}
    </Text>
    {children}
  </View>
)

Section.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  marginTop: PropTypes.number,
}

Section.defaultProps = {
  marginTop: 0,
}

export default Section
