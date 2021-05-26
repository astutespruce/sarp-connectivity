import React from 'react'
import PropTypes from 'prop-types'
import { Link as PDFLink } from '@react-pdf/renderer'

const Link = ({ href, children }) => (
  <PDFLink
    src={href}
    style={{
      textDecoration: 'underline',
      color: '#1891ac',
    }}
  >
    {children}
  </PDFLink>
)

Link.propTypes = {
  href: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
}

export default Link
