/** @jsxRuntime classic */
/** @jsx jsx */

// eslint-disable-next-line no-unused-vars
import React from 'react'
import { OutboundLink as Link } from 'gatsby-plugin-google-gtag'
import PropTypes from 'prop-types'
import { jsx } from 'theme-ui'

const OutboundLink = ({ to, target, rel, children, ...props }) => (
  <Link href={to} target={target} rel={rel} {...props}>
    {children}
  </Link>
)

OutboundLink.propTypes = {
  to: PropTypes.string.isRequired,
  target: PropTypes.string,
  rel: PropTypes.string,
  children: PropTypes.any.isRequired,
}

OutboundLink.defaultProps = {
  target: '_blank',
  rel: 'noopener noreferrer',
}

export default OutboundLink
