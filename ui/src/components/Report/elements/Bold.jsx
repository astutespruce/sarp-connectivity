import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

const Bold = ({ children, style }) => (
  <Text style={{ ...style, fontFamily: 'Helvetica-Bold' }}>{children}</Text>
)

Bold.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  style: PropTypes.object,
}

Bold.defaultProps = {
  style: null,
}

export default Bold
