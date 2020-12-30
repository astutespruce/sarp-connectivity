import React from 'react'
import PropTypes from 'prop-types'

const FaIcon = ({ name, size, ...props }) => {
  const iconName = `Fa${name.slice(0, 1).toUpperCase()}${name.slice(1)}`

  /* eslint-disable-next-line global-require */
  const Icon = require('react-icons/fa')[iconName]

  if (!Icon) return null

  return <Icon size={size} style={{ width: size, height: size }} {...props} />
}

FaIcon.propTypes = {
  name: PropTypes.string.isRequired,
  size: PropTypes.string,
}

FaIcon.defaultProps = {
  size: null,
}

export default FaIcon
