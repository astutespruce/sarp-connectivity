import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

const Italic = ({ children, style }) => (
  <Text style={{ ...style, fontFamily: 'Helvetica-Oblique' }}>{children}</Text>
)

Italic.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  style: PropTypes.object,
}

Italic.defaultProps = {
  style: null,
}

export default Italic
